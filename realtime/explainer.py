"""
realtime/explainer.py
=====================
TF-IDF keyword explainability module.

Extracts the words from the input text that most strongly influenced
the model's prediction, using the vectorizer's feature names and the
Logistic Regression coefficient vector.

Usage:
    from realtime.explainer import Explainer
    exp = Explainer(vectorizer, classifier)
    highlights = exp.explain("shocking viral claim propagating fake news")
"""

import os
import sys
import pickle
import logging
from typing import Any, Dict, List

import numpy as np  # type: ignore[import-untyped]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logger = logging.getLogger(__name__)


class Explainer:
    """
    Extracts top-N TF-IDF weighted terms most influential in the prediction.

    Works by:
      1. Projecting the input into TF-IDF space
      2. Element-wise multiplying TF-IDF values by model coefficients
      3. Ranking by absolute contribution magnitude
    """

    def __init__(self, vectorizer: Any, classifier: Any) -> None:
        """
        Args:
            vectorizer:  Fitted TfidfVectorizer
            classifier:  Fitted classifier with coef_ attribute (e.g., LogisticRegression)
        """
        self.vectorizer: Any = vectorizer
        self.classifier: Any = classifier
        self.feature_names: Any = None
        self.coef_fake: Any = None
        self._ready: bool = False

        try:
            # coef_ shape: (n_classes, n_features) or (1, n_features) for binary
            self.feature_names = np.array(vectorizer.get_feature_names_out())
            coef = classifier.coef_
            # For binary LR: coef_ shape is (1, n_features), class 1 = Fake
            self.coef_fake = coef[0] if coef.shape[0] == 1 else coef[1]
            self._ready = True
        except Exception as exc:
            logger.warning(f"Explainer init failed: {exc}")
            self._ready = False

    def explain(self, text: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Identify the most influential terms for the prediction.

        Args:
            text:   Preprocessed (cleaned) text.
            top_n:  Number of top terms to return.

        Returns:
            List of dicts: [{word, score, direction}]
              direction: 'fake' if pushes toward Fake, 'real' if pushes toward Real
        """
        if not self._ready:
            return []

        try:
            X_vec = self.vectorizer.transform([text])
            # Dense contribution = tfidf_weight × coef
            tfidf_vals = np.array(X_vec.todense()).flatten()
            contributions = tfidf_vals * self.coef_fake

            # Only consider terms actually present in the text
            non_zero_idxs = np.where(tfidf_vals > 0)[0]
            if len(non_zero_idxs) == 0:
                return []

            # Sort by absolute contribution
            sorted_idxs = non_zero_idxs[
                np.argsort(np.abs(contributions[non_zero_idxs]))[::-1]
            ]
            top_idxs = sorted_idxs[:top_n]

            results: List[Dict[str, Any]] = []
            for idx in top_idxs:
                score: float     = float(contributions[idx])
                word: str        = str(self.feature_names[idx])
                direction: str   = "fake" if score > 0 else "real"
                results.append({
                    "word":      word,
                    "score":     float(round(abs(score), 5)),
                    "direction": direction,
                })

            return results

        except Exception as exc:
            logger.warning(f"Explainer.explain error: {exc}")
            return []

    def is_ready(self) -> bool:
        """Return True if the explainer was initialised successfully."""
        return self._ready


def load_explainer_from_paths(model_path: str, vec_path: str) -> Explainer:
    """
    Convenience factory: load vectorizer + model from disk and return Explainer.

    Args:
        model_path: Path to fake_news_model.pkl
        vec_path:   Path to vectorizer.pkl
    """
    with open(vec_path, "rb") as f:
        vectorizer = pickle.load(f)

    with open(model_path, "rb") as f:
        obj = pickle.load(f)

    clf = obj.get("model") if isinstance(obj, dict) else obj
    return Explainer(vectorizer, clf)
