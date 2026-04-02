"""
realtime/ensemble.py
====================
Ensemble combiner: TF-IDF baseline + DistilBERT + robust embedding model.

Combines probability outputs from all available models using weighted
averaging, with graceful fallback if any model is unavailable.

Model weights:
  TF-IDF baseline:  0.40   (fast, interpretable)
  BERT (DistilBERT): 0.40  (deep contextual understanding)
  Robust model:      0.20  (adversarial defense)

Usage:
    from realtime.ensemble import EnsemblePredictor
    ens = EnsemblePredictor()
    result = ens.predict("Shocking viral claim about vaccines")
"""

import os
import sys
import pickle
import logging
from typing import Any, Dict, Optional

import numpy as np                                     # type: ignore[import-untyped]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from data_pipeline.preprocess import TextPreprocessor   # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

# ── Model weights ─────────────────────────────────────────────────────────────
# When all 3 models are available:
WEIGHT_BASELINE: float = 0.40   # TF-IDF
WEIGHT_BERT: float     = 0.40   # DistilBERT
WEIGHT_ROBUST: float   = 0.20   # Adversarial robust

# When BERT is unavailable (2-model fallback):
WEIGHT_BASELINE_NO_BERT: float = 0.65
WEIGHT_ROBUST_NO_BERT: float   = 0.35

BASELINE_MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "fake_news_model.pkl")
BASELINE_VEC_PATH   = os.path.join(BASE_DIR, "ml_models", "vectorizer.pkl")
ROBUST_MODEL_PATH   = os.path.join(BASE_DIR, "ml_models", "saved_models", "robust_model_adversarial.pkl")


class EnsemblePredictor:
    """
    Weighted ensemble of TF-IDF + BERT + Robust models.
    Falls back gracefully if BERT or robust model is unavailable.
    """

    LABEL_MAP: Dict[int, str] = {0: "Real", 1: "Fake"}

    def __init__(self) -> None:
        self.preprocessor = TextPreprocessor()
        self._baseline_clf: Any = None
        self._baseline_vec: Any = None
        self._robust_clf: Any   = None
        self._robust_emb_dim: int = 768
        self._bert_predictor: Any = None
        self._has_robust: bool  = False
        self._has_bert: bool    = False

        self._load_models()

    # ── Loading ──────────────────────────────────────────────────────────────

    def _load_models(self) -> None:
        """Load all available models; BERT and robust are optional."""

        # ── Baseline TF-IDF (required) ───────────────────────────────────────
        if not os.path.exists(BASELINE_VEC_PATH) or not os.path.exists(BASELINE_MODEL_PATH):
            raise FileNotFoundError(
                "Baseline models not found. Run: python ml_models/train_and_save.py"
            )

        with open(BASELINE_VEC_PATH, "rb") as f:
            self._baseline_vec = pickle.load(f)

        with open(BASELINE_MODEL_PATH, "rb") as f:
            obj = pickle.load(f)
        self._baseline_clf = obj.get("model") if isinstance(obj, dict) else obj

        # ── BERT / DistilBERT (optional) ─────────────────────────────────────
        try:
            from realtime.bert_model import BERTPredictor  # type: ignore[import-not-found]
            bert = BERTPredictor()
            if bert.is_ready():
                self._bert_predictor = bert
                self._has_bert = True
                logger.info("EnsemblePredictor: ✅ BERT model loaded.")
            else:
                logger.warning("EnsemblePredictor: BERT model not ready. Skipping.")
        except Exception as exc:
            logger.warning(f"EnsemblePredictor: BERT unavailable ({exc}). Skipping.")

        # ── Robust model (optional) ──────────────────────────────────────────
        if os.path.exists(ROBUST_MODEL_PATH):
            try:
                with open(ROBUST_MODEL_PATH, "rb") as f:
                    robust_data = pickle.load(f)
                self._robust_clf     = robust_data.get("model")
                self._robust_emb_dim = robust_data.get("embedding_dim", 768)
                self._has_robust     = True
                logger.info("EnsemblePredictor: ✅ Robust model loaded.")
            except Exception as exc:
                logger.warning(
                    f"EnsemblePredictor: could not load robust model ({exc}). Skipping."
                )

        # Log final configuration
        models = ["TF-IDF (baseline)"]
        if self._has_bert:
            models.append("DistilBERT")
        if self._has_robust:
            models.append("Robust")
        mode_str = " + ".join(models)
        logger.info(f"EnsemblePredictor ready — models: {mode_str}")

    # ── Robust model embedding ─────────────────────────────────────────────

    def _embed(self, text: str) -> Any:
        """Generate deterministic pseudo-embedding matching RobustModel's strategy."""
        dim = self._robust_emb_dim
        words = text.lower().split()
        embedding = np.zeros(dim)

        half = dim // 2
        for i, word in enumerate(words[:half]):  # type: ignore[arg-type]
            embedding[i] = ord(word[0]) / 255.0 if word else 0

        chars = list(text)
        for i, char in enumerate(chars[:half]):  # type: ignore[arg-type]
            embedding[half + i % half] = ord(char) / 255.0

        np.random.seed(hash(text) % 2**32)
        noise = np.random.randn(dim) * 0.1
        embedding = embedding + noise
        norm = float(np.linalg.norm(embedding))
        embedding = embedding / (norm + 1e-8)
        return embedding

    # ── Prediction ───────────────────────────────────────────────────────────

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Run ensemble prediction on raw input text.

        Returns:
            dict with keys: label, confidence, fake_proba, real_proba,
                            clean_text, model_source, model_agreement,
                            individual_predictions
        """
        text = str(text).strip()
        if not text:
            raise ValueError("Input text is empty.")

        clean: str = self.preprocessor.clean_text(text) or text.lower()

        # ── Collect predictions from all available models ────────────────────

        # 1. Baseline TF-IDF (always available)
        X_vec = self._baseline_vec.transform([clean])
        base_proba = self._baseline_clf.predict_proba(X_vec)[0]
        baseline_label = "Fake" if base_proba[1] > base_proba[0] else "Real"

        # 2. BERT (optional)
        bert_proba = None
        bert_label = None
        if self._has_bert and self._bert_predictor is not None:
            try:
                bert_result = self._bert_predictor.predict(text)  # use raw text
                bert_proba = np.array([
                    bert_result["real_proba"],
                    bert_result["fake_proba"],
                ])
                bert_label = bert_result["label"]
            except Exception as exc:
                logger.warning(f"BERT prediction failed: {exc}")

        # 3. Robust model (optional)
        robust_proba = None
        if self._has_robust and self._robust_clf is not None:
            emb = self._embed(clean).reshape(1, -1)
            try:
                robust_proba = self._robust_clf.predict_proba(emb)[0]
            except Exception:
                robust_proba = None

        # ── Weighted combination ─────────────────────────────────────────────

        combined: Any = None
        model_source: str = "baseline"

        if bert_proba is not None and robust_proba is not None:
            # All 3 models available
            combined = (
                WEIGHT_BASELINE * base_proba
                + WEIGHT_BERT * bert_proba
                + WEIGHT_ROBUST * robust_proba
            )
            model_source = "ensemble (TF-IDF + BERT + Robust)"

        elif bert_proba is not None:
            # TF-IDF + BERT only
            combined = 0.50 * base_proba + 0.50 * bert_proba
            model_source = "ensemble (TF-IDF + BERT)"

        elif robust_proba is not None:
            # TF-IDF + Robust only (no BERT)
            combined = (
                WEIGHT_BASELINE_NO_BERT * base_proba
                + WEIGHT_ROBUST_NO_BERT * robust_proba
            )
            model_source = "ensemble (TF-IDF + Robust)"

        else:
            # Baseline only
            combined = base_proba
            model_source = "baseline"

        real_proba = float(combined[0])
        fake_proba = float(combined[1]) if len(combined) > 1 else 1.0 - real_proba
        label_idx  = int(np.argmax(combined))
        confidence = float(combined[label_idx])

        # ── Model agreement ──────────────────────────────────────────────────

        individual = {"tfidf": baseline_label}
        if bert_label is not None:
            individual["bert"] = bert_label

        labels = list(individual.values())
        if len(labels) >= 2 and all(l == labels[0] for l in labels):
            agreement = "agree"
        elif len(labels) >= 2:
            agreement = "disagree"
        else:
            agreement = "single_model"

        return {
            "label":                self.LABEL_MAP[label_idx],
            "label_id":             label_idx,
            "confidence":           float(round(confidence, 4)),
            "fake_proba":           float(round(fake_proba, 4)),
            "real_proba":           float(round(real_proba, 4)),
            "clean_text":           clean,
            "model_source":         model_source,
            "model_agreement":      agreement,
            "individual_predictions": individual,
        }

    def is_ready(self) -> bool:
        """Return True if at least the baseline model is loaded."""
        return self._baseline_clf is not None
