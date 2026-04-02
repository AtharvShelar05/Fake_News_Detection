"""
realtime/predictor.py
======================
Core real-time prediction pipeline.

Loads the pre-trained TF-IDF vectorizer and Logistic Regression classifier,
applies the existing TextPreprocessor from data_pipeline/preprocess.py,
and returns a structured prediction result.

Usage:
    from realtime.predictor import FakeNewsPredictor
    predictor = FakeNewsPredictor()
    result = predictor.predict("Shocking: Scientists discover cure for everything!")
"""

import os
import sys
import pickle
import logging
from typing import Any, Dict

import numpy as np  # type: ignore[import-untyped]

# ── Add project root to path so we can import existing modules ──────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from data_pipeline.preprocess import TextPreprocessor  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

# ── Default model paths ────────────────────────────────────────────────────
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "fake_news_model.pkl")
DEFAULT_VEC_PATH   = os.path.join(BASE_DIR, "ml_models", "vectorizer.pkl")


class FakeNewsPredictor:
    """
    Single-text real-time fake news predictor.

    Wraps:
      1. TextPreprocessor (existing data_pipeline module)
      2. TF-IDF Vectorizer (pre-trained)
      3. Logistic Regression classifier (pre-trained)
    """

    LABEL_MAP: Dict[int, str] = {0: "Real", 1: "Fake"}

    def __init__(
        self,
        model_path: str = DEFAULT_MODEL_PATH,
        vectorizer_path: str = DEFAULT_VEC_PATH,
    ) -> None:
        """
        Load preprocessor, vectorizer, and classifier.

        Args:
            model_path:      Path to fake_news_model.pkl
            vectorizer_path: Path to vectorizer.pkl
        """
        self.preprocessor = TextPreprocessor()
        self.model: Any        = None
        self.vectorizer: Any   = None
        self._loaded: bool     = False

        self._model_path = model_path
        self._vec_path   = vectorizer_path

        self._load_models()

    # ── Loading ──────────────────────────────────────────────────────────────

    def _load_models(self) -> None:
        """Load vectorizer and model from disk. Raises on failure."""
        if not os.path.exists(self._vec_path):
            raise FileNotFoundError(
                f"Vectorizer not found at '{self._vec_path}'. "
                "Run: python ml_models/train_and_save.py"
            )
        if not os.path.exists(self._model_path):
            raise FileNotFoundError(
                f"Model not found at '{self._model_path}'. "
                "Run: python ml_models/train_and_save.py"
            )

        with open(self._vec_path, "rb") as f:
            self.vectorizer = pickle.load(f)

        with open(self._model_path, "rb") as f:
            obj = pickle.load(f)

        # Support both raw classifier and dict-wrapped format
        if isinstance(obj, dict):
            self.model = obj.get("model") or obj.get("classifier")
        else:
            self.model = obj

        if self.model is None:
            raise ValueError("Could not extract classifier from model file.")

        self._loaded = True
        logger.info("FakeNewsPredictor: models loaded successfully.")

    # ── Prediction ───────────────────────────────────────────────────────────

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict whether a news text is real or fake.

        Args:
            text: Raw news text from the user.

        Returns:
            dict with keys:
              label, label_id, confidence, fake_proba, real_proba,
              clean_text, model_source
        """
        if not self._loaded:
            raise RuntimeError("Models not loaded.")

        # 1. Validate
        text = str(text).strip()
        if not text:
            raise ValueError("Input text is empty.")

        # 2. Preprocess (reuse existing pipeline)
        clean: str = self.preprocessor.clean_text(text)
        if not clean:
            # Fallback: use raw lowercased text if everything was stripped
            clean = text.lower()

        # 3. Vectorise
        X_vec = self.vectorizer.transform([clean])

        # 4. Predict
        label_idx: int = int(self.model.predict(X_vec)[0])
        probas = self.model.predict_proba(X_vec)[0]  # [real_proba, fake_proba]

        fake_proba: float = float(probas[1]) if len(probas) > 1 else float(probas[0])
        real_proba: float = float(probas[0])
        confidence: float = float(probas[label_idx])

        return {
            "label":        self.LABEL_MAP[label_idx],
            "label_id":     label_idx,
            "confidence":   round(confidence, 4),
            "fake_proba":   round(fake_proba, 4),
            "real_proba":   round(real_proba, 4),
            "clean_text":   clean,
            "model_source": "baseline",
        }

    def is_ready(self) -> bool:
        """Return True if models are loaded and ready."""
        return self._loaded
