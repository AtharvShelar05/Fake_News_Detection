"""
app.py — Real-Time Fake News Detection Web Application
=======================================================
Flask backend powering the interactive fake news detector.

Routes:
  GET  /           → Serve the main UI (index.html)
  POST /check-news → Full detection pipeline with decision logic (PRIMARY)
  POST /predict    → Legacy prediction endpoint (backward compatible)
  GET  /health     → System status (models loaded, API key, etc.)

Run:
  python run_app.py          (recommended — trains models first if needed)
  python app.py              (direct launch — models must already exist)
"""

import os
import sys
import re
import logging
import traceback
from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, request, jsonify, render_template  # type: ignore[import-untyped]

# ── Project root setup ────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ── Load .env ─────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv  # type: ignore[import-untyped]
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("FakeNewsApp")

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["JSON_SORT_KEYS"] = False

# ── Lazy-loaded components (populated on first request) ───────────────────────
_predictor      = None   # EnsemblePredictor
_fact_checker   = None   # FactChecker
_explainer      = None   # Explainer (TF-IDF)
_shap_explainer = None   # SHAPExplainer (SHAP + fallback)
_init_error     = None   # str if init failed


def _initialize() -> None:
    """
    Load all ML components on first use.
    Keeps startup fast and prints clear errors if models are missing.
    """
    global _predictor, _fact_checker, _explainer, _shap_explainer, _init_error

    if _predictor is not None or _init_error is not None:
        return  # already initialised

    try:
        from realtime.ensemble     import EnsemblePredictor        # type: ignore[import-not-found]
        from realtime.fact_checker import FactChecker               # type: ignore[import-not-found]
        from realtime.explainer    import load_explainer_from_paths # type: ignore[import-not-found]

        model_path = os.path.join(BASE_DIR, "ml_models", "fake_news_model.pkl")
        vec_path   = os.path.join(BASE_DIR, "ml_models", "vectorizer.pkl")

        logger.info("Loading prediction models (TF-IDF + BERT ensemble)…")
        _predictor    = EnsemblePredictor()

        logger.info("Loading fact-checker…")
        _fact_checker = FactChecker()

        logger.info("Loading TF-IDF explainer…")
        _explainer    = load_explainer_from_paths(model_path, vec_path)

        # ── SHAP Explainer (optional — uses SHAP if installed) ────────────
        logger.info("Loading SHAP explainer…")
        try:
            import pickle as _pk
            from realtime.shap_explainer import SHAPExplainer  # type: ignore[import-not-found]
            with open(vec_path, "rb") as f:
                _vec = _pk.load(f)
            with open(model_path, "rb") as f:
                _obj = _pk.load(f)
            _clf = _obj.get("model") if isinstance(_obj, dict) else _obj
            _shap_explainer = SHAPExplainer(_vec, _clf)
            logger.info("✅ SHAP explainer loaded.")
        except Exception as shap_exc:
            logger.warning(f"SHAP explainer not available: {shap_exc}")

        logger.info("✅ All components initialised successfully.")

    except Exception as exc:
        _init_error = str(exc)
        logger.error(f"⚠️  Component initialisation failed: {exc}")
        logger.error(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════════════
#  MODULAR HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def preprocess(text: str) -> str:
    """
    Step 1: Validate and clean user input.
    - Strips whitespace
    - Truncates to 10,000 chars
    - Returns cleaned text ready for ML + API
    """
    text = str(text).strip()

    if not text:
        raise ValueError("Input text is required.")

    if len(text) < 10:
        raise ValueError("Text too short — please enter at least 10 characters.")

    # Truncate very long input
    if len(text) > 10_000:
        text = text[:10_000]

    return text


def predict_ml(text: str) -> Dict[str, Any]:
    """
    Step 2: Run ML ensemble prediction.
    Returns dict with: label, confidence, fake_proba, real_proba, clean_text, model_source
    """
    if _predictor is None:
        raise RuntimeError("ML model not loaded.")

    result = _predictor.predict(text)
    return {
        "label":        result["label"],          # "Fake" | "Real"
        "confidence":   result["confidence"],     # 0.0 – 1.0
        "fake_proba":   result["fake_proba"],     # 0.0 – 1.0
        "real_proba":   result["real_proba"],     # 0.0 – 1.0
        "clean_text":   result["clean_text"],
        "model_source": result["model_source"],
    }


def fact_check(text: str) -> Dict[str, Any]:
    """
    Step 3: Query Google Fact Check Tools API.
    Returns dict with: available, matched, api_rating, claims list, error
    """
    if _fact_checker is None or not _fact_checker.is_available():
        return {
            "available": False,
            "matched":   False,
            "api_rating": None,
            "claims":    [],
            "error":     None,
        }

    try:
        fc = _fact_checker.check(text, max_results=5)
    except Exception as exc:
        logger.warning(f"Fact-check error: {exc}")
        return {
            "available": True,
            "matched":   False,
            "api_rating": None,
            "claims":    [],
            "error":     str(exc),
        }

    # Parse claims into the user-requested format
    parsed_claims: List[Dict[str, str]] = []
    for c in fc.get("claims", []):
        parsed_claims.append({
            "claim":     c.get("text", ""),
            "publisher": c.get("publisher", "Unknown"),
            "rating":    c.get("rating", "Unknown"),
            "url":       c.get("rating_url", ""),
        })

    # Determine overall API rating from verified_label
    api_rating = None
    vl = fc.get("verified_label")
    if vl == "Verified Fake":
        api_rating = "False"
    elif vl == "Verified True":
        api_rating = "True"
    elif vl == "Fact-Checked":
        api_rating = "Mixed"

    return {
        "available":  True,
        "matched":    fc.get("matched", False),
        "api_rating": api_rating,
        "claims":     parsed_claims,
        "error":      fc.get("error"),
    }


def combine_results(
    ml_result: Dict[str, Any],
    fc_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Step 4: Apply decision matrix to combine ML + fact-check results.

    Decision Matrix:
      ML=FAKE  + API=False/Misleading → HIGH confidence FAKE
      ML=REAL  + API=True/Correct     → HIGH confidence REAL
      ML=FAKE  + API=True   (mismatch)→ MEDIUM confidence
      ML=REAL  + API=False  (mismatch)→ MEDIUM confidence
      Any      + No API results       → LOW confidence (ML only)
    """
    ml_label    = ml_result["label"].upper()    # "FAKE" | "REAL"
    ml_conf     = ml_result["confidence"]       # 0.0–1.0
    api_rating  = fc_result.get("api_rating")   # "False" | "True" | "Mixed" | None
    api_matched = fc_result.get("matched", False)

    # ── No API results → LOW confidence (ML only) ────────────────────────────
    if not api_matched or api_rating is None:
        return {
            "final_verdict": ml_label,
            "confidence":    "Low",
            "reason":        "No matching fact-check claims found. Verdict based on ML model only.",
        }

    # ── Classify the API rating ──────────────────────────────────────────────
    api_says_false = api_rating in ("False", "Mixed")
    api_says_true  = api_rating == "True"

    # ── ML=FAKE + API=False → HIGH confidence FAKE ───────────────────────────
    if ml_label == "FAKE" and api_says_false:
        return {
            "final_verdict": "FAKE",
            "confidence":    "High",
            "reason":        "ML model and fact-checkers both agree this is fake/misleading.",
        }

    # ── ML=REAL + API=True → HIGH confidence REAL ────────────────────────────
    if ml_label == "REAL" and api_says_true:
        return {
            "final_verdict": "REAL",
            "confidence":    "High",
            "reason":        "ML model and fact-checkers both agree this is real/accurate.",
        }

    # ── Mismatch: ML=FAKE but API=True ───────────────────────────────────────
    if ml_label == "FAKE" and api_says_true:
        return {
            "final_verdict": "FAKE",
            "confidence":    "Medium",
            "reason":        "ML model says fake, but fact-checkers rate related claims as true. Review recommended.",
        }

    # ── Mismatch: ML=REAL but API=False ──────────────────────────────────────
    if ml_label == "REAL" and api_says_false:
        return {
            "final_verdict": "FAKE",
            "confidence":    "Medium",
            "reason":        "ML model says real, but fact-checkers rate related claims as false/misleading.",
        }

    # ── Fallback ─────────────────────────────────────────────────────────────
    return {
        "final_verdict": ml_label,
        "confidence":    "Medium",
        "reason":        "Inconclusive — could not determine agreement between ML and fact-checkers.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the main interactive UI."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Return system status as JSON."""
    _initialize()
    return jsonify({
        "status":           "ok" if _predictor and _init_error is None else "degraded",
        "models_loaded":    _predictor is not None,
        "bert_loaded":      getattr(_predictor, '_has_bert', False) if _predictor else False,
        "fact_check_api":   _fact_checker.is_available() if _fact_checker else False,
        "explainer_ready":  _explainer.is_ready() if _explainer else False,
        "shap_ready":       _shap_explainer.is_ready() if _shap_explainer else False,
        "init_error":       _init_error,
    })


# ═══════════════════════════════════════════════════════════════════════════════
#  PRIMARY ENDPOINT: /check-news
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/check-news", methods=["POST"])
def check_news():
    """
    POST /check-news
    Body: { "text": "<news text>" }

    Returns structured JSON:
    {
      "input_news":          "...",
      "ml_prediction":       "FAKE" | "REAL",
      "ml_confidence":       94.7,
      "fact_check_results":  [ { claim, publisher, rating, url } ],
      "final_verdict":       "FAKE" | "REAL",
      "confidence":          "High" | "Medium" | "Low",
      "confidence_reason":   "...",
      "top_keywords":        [ { word, score, direction } ],
      "model_source":        "ensemble" | "baseline"
    }
    """
    _initialize()

    # ── Guard: init failed ────────────────────────────────────────────────────
    if _predictor is None:
        return jsonify({
            "error": f"Model not loaded: {_init_error}. "
                     "Run: python ml_models/train_and_save.py"
        }), 503

    # ── Step 1: Preprocess input ──────────────────────────────────────────────
    body = request.get_json(silent=True) or {}
    raw_text = body.get("text", "")

    try:
        clean_input = preprocess(raw_text)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    try:
        from realtime.integration import predict_news, final_decision
        
        # ── Step 2 & 3 & 4: Integrated ML Prediction & Decision Engine ────────
        ml_label, ml_real_proba = predict_news(clean_input)
        final_label, fact_check_status = final_decision(ml_real_proba, clean_input)

        # ── Assemble final response with required fields ──────────────────────
        response: Dict[str, Any] = {
            "input_news":             clean_input,
            "final_label":            final_label,
            "confidence_score":       ml_real_proba,
            "fact_check_status":      fact_check_status,
            # Legacy/Debug fields for convenience
            "ml_prediction":          ml_label,
            "ml_confidence":          ml_real_proba * 100,
        }

        logger.info(
            f"[/check-news] '{str(clean_input)[:60]}' → "  # type: ignore[str-bytes-safe]
            f"{final_label} (score={ml_real_proba}, FC={fact_check_status})"
        )
        return jsonify(response)

    except Exception as exc:
        logger.error(f"Prediction error: {exc}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error during prediction."}), 500


# ═══════════════════════════════════════════════════════════════════════════════
#  LEGACY ENDPOINT: /predict (backward compatible)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/predict", methods=["POST"])
def predict():
    """
    POST /predict — Legacy endpoint (kept for backward compatibility).
    Internally delegates to the same pipeline as /check-news.
    """
    _initialize()

    if _predictor is None:
        return jsonify({
            "error": f"Model not loaded: {_init_error}. "
                     "Run: python ml_models/train_and_save.py"
        }), 503

    body = request.get_json(silent=True) or {}
    raw_text = body.get("text", "")

    try:
        clean_input = preprocess(raw_text)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    try:
        ml_result = predict_ml(clean_input)
        fc_result = fact_check(clean_input)
        decision  = combine_results(ml_result, fc_result)

        top_keywords: List[Dict[str, Any]] = []
        if _explainer and _explainer.is_ready():
            top_keywords = _explainer.explain(ml_result["clean_text"], top_n=10)

        # Legacy format (matches original /predict response)
        label      = ml_result["label"]
        fake_proba = ml_result["fake_proba"]
        real_proba = ml_result["real_proba"]
        confidence = ml_result["confidence"]

        response: Dict[str, Any] = {
            "label":          label,
            "display_label":  decision["final_verdict"],
            "confidence":     float(round(confidence * 100, 1)),
            "fake_proba":     float(round(fake_proba * 100, 1)),
            "real_proba":     float(round(real_proba * 100, 1)),
            "model_source":   ml_result["model_source"],
            "clean_text":     ml_result["clean_text"],
            "top_keywords":   top_keywords,
            "fact_check": {
                "available":      fc_result["available"],
                "matched":        fc_result["matched"],
                "verified_label": decision["final_verdict"],
                "claims":         fc_result["claims"][:3],
                "error":          fc_result.get("error"),
            },
        }
        return jsonify(response)

    except Exception as exc:
        logger.error(f"Prediction error: {exc}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error during prediction."}), 500


# ── Dev server ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════╗")
    print("║  Fake News Detection Platform — Development Server   ║")
    print("╚══════════════════════════════════════════════════════╝")
    print("  Open: http://127.0.0.1:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
