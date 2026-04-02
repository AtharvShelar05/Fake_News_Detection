"""
realtime/bert_model.py
======================
DistilBERT zero-shot classifier for fake news detection.

Uses HuggingFace's zero-shot-classification pipeline with
distilbert-base-uncased-mnli (pre-trained on NLI tasks).

Why zero-shot?
  - Our dataset has only 15 rows — far too small for fine-tuning
  - Zero-shot leverages pre-trained NLI understanding
  - No training required — works out of the box

Usage:
    from realtime.bert_model import BERTPredictor
    bert = BERTPredictor()
    result = bert.predict("COVID vaccine causes autism")
    # {'label': 'Fake', 'confidence': 0.87, ...}
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Candidate labels mapping
_LABEL_MAP = {
    "LABEL_1": "Fake",
    "LABEL_0": "Real"
}

# Guard: only load heavy imports when needed
_pipeline_fn = None
_classifier  = None


def _load_pipeline() -> Any:
    """Lazy-load the HuggingFace zero-shot pipeline (cached after first call)."""
    global _pipeline_fn, _classifier

    if _classifier is not None:
        return _classifier

    try:
        from transformers import pipeline  # type: ignore[import-untyped]
        import os
        _pipeline_fn = pipeline

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_dir = os.path.join(BASE_DIR, "ml_models", "bert_model")

        if not os.path.exists(model_dir):
            logger.warning(f"BERTPredictor: ⚠️ Local model not found at {model_dir}. Run ml_models/train_bert.py first.")
            return None

        logger.info(f"BERTPredictor: Loading fine-tuned model from {model_dir}…")
        _classifier = pipeline(
            "text-classification",
            model=model_dir,
            tokenizer=model_dir,
            device=-1,  # CPU (use 0 for GPU)
            top_k=None # Return scores for all classes
        )
        logger.info("BERTPredictor: ✅ Model loaded successfully.")
        return _classifier

    except ImportError:
        logger.error(
            "BERTPredictor: ❌ 'transformers' not installed. "
            "Run: pip install transformers torch"
        )
        return None
    except Exception as exc:
        logger.error(f"BERTPredictor: ❌ Failed to load model: {exc}")
        return None


class BERTPredictor:
    """
    Zero-shot DistilBERT classifier for fake news detection.

    Uses the fine-tuned DistilBERT model to classify text as matching
    'Fake' vs 'Real' categories.
    """

    def __init__(self) -> None:
        """Initialize and cache the model pipeline."""
        self._classifier = _load_pipeline()
        self._ready = self._classifier is not None

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Classify text as Fake or Real using DistilBERT.

        Args:
            text: Raw or cleaned news text.

        Returns:
            dict with keys:
              label       — "Fake" | "Real"
              label_id    — 1 (Fake) | 0 (Real)
              confidence  — 0.0–1.0
              fake_proba  — 0.0–1.0
              real_proba  — 0.0–1.0
        """
        if not self._ready:
            # Fallback: return neutral prediction
            return {
                "label":      "Real",
                "label_id":   0,
                "confidence": 0.5,
                "fake_proba": 0.5,
                "real_proba": 0.5,
            }

        # Truncate input for efficiency (DistilBERT max = 512 tokens)
        text = str(text).strip()[:1500]

        try:
            results = self._classifier(text)
            
            # Extract scores (pipeline returns a list of lists when top_k=None)
            # e.g., [[{'label': 'LABEL_1', 'score': 0.8}, {'label': 'LABEL_0', 'score': 0.2}]]
            if isinstance(results, list) and isinstance(results[0], list):
                result = results[0]
            else:
                result = results

            scores = {item['label']: float(item['score']) for item in result}

            fake_proba = scores.get("LABEL_1", 0.5)
            real_proba = scores.get("LABEL_0", 0.5)

            if fake_proba > real_proba:
                label = "Fake"
                label_id = 1
                confidence = fake_proba
            else:
                label = "Real"
                label_id = 0
                confidence = real_proba

            return {
                "label":      label,
                "label_id":   label_id,
                "confidence": round(confidence, 4),
                "fake_proba": round(fake_proba, 4),
                "real_proba": round(real_proba, 4),
            }
        except Exception as e:
            logger.error(f"BERTPredictor: prediction error: {e}")
            return {
                "label":      "Real",
                "label_id":   0,
                "confidence": 0.5,
                "fake_proba": 0.5,
                "real_proba": 0.5,
            }

    def is_ready(self) -> bool:
        """Return True if the model is loaded and ready."""
        return self._ready
