"""
realtime/shap_explainer.py
==========================
SHAP-based word-level explainability for fake news detection.

Uses SHAP (SHapley Additive exPlanations) to compute per-word
contribution scores, showing which words push toward FAKE vs REAL.

The module provides both:
  1. Top contributing words with scores (for charts/lists)
  2. Full highlighted text data (for inline text coloring)

Usage:
    from realtime.shap_explainer import SHAPExplainer
    explainer = SHAPExplainer(vectorizer, classifier)
    result = explainer.explain("shocking viral claim about vaccines")
"""

import logging
import re
from typing import Any, Callable, Dict, List, Optional

import numpy as np  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

# Try to import shap — graceful fallback if not installed
_shap = None
try:
    import shap  # type: ignore[import-untyped]
    _shap = shap
except ImportError:
    logger.info("SHAPExplainer: 'shap' not installed. Using TF-IDF fallback.")


class SHAPExplainer:
    """
    SHAP-based word-level explainability.

    Computes per-word SHAP values to show which words contribute most
    to the FAKE or REAL prediction. Falls back to TF-IDF coefficient-based
    explanation if SHAP is not available.
    """

    def __init__(self, vectorizer: Any, classifier: Any) -> None:
        """
        Args:
            vectorizer: Fitted TfidfVectorizer
            classifier: Fitted classifier with predict_proba (e.g., LogisticRegression)
        """
        self.vectorizer = vectorizer
        self.classifier = classifier
        self._use_shap = _shap is not None
        self._ready = False

        try:
            self.feature_names = np.array(vectorizer.get_feature_names_out())
            # For TF-IDF fallback: get coefficient vector
            coef = classifier.coef_
            self.coef_fake = coef[0] if coef.shape[0] == 1 else coef[1]
            self._ready = True
        except Exception as exc:
            logger.warning(f"SHAPExplainer init failed: {exc}")

    def _predict_proba_for_shap(self, texts: List[str]) -> Any:
        """Prediction function compatible with SHAP's masker."""
        X = self.vectorizer.transform(texts)
        return self.classifier.predict_proba(X)

    def explain(
        self,
        text: str,
        top_n: int = 10,
    ) -> Dict[str, Any]:
        """
        Compute word-level explanations for a prediction.

        Args:
            text:   Preprocessed (cleaned) text.
            top_n:  Number of top contributing words to return.

        Returns:
            dict with:
              top_words:       List[{word, score, direction, color}]
              highlighted_text: List[{word, score, direction, color}] for every word
              method:          "shap" | "tfidf_coefficients"
        """
        if not self._ready:
            return {
                "top_words": [],
                "highlighted_text": [],
                "method": "unavailable",
            }

        # Try SHAP first, fall back to TF-IDF coefficients
        if self._use_shap:
            return self._explain_shap(text, top_n)
        else:
            return self._explain_tfidf(text, top_n)

    def _explain_shap(self, text: str, top_n: int) -> Dict[str, Any]:
        """Use SHAP to compute word-level explanations."""
        try:
            # Create a SHAP explainer with the prediction function
            masker = _shap.maskers.Text(tokenizer=r"\W+")
            explainer = _shap.Explainer(
                self._predict_proba_for_shap,
                masker=masker,
                output_names=["Real", "Fake"],
            )

            # Compute SHAP values (for the "Fake" class = index 1)
            shap_values = explainer([text])

            # Extract word-level values for the Fake class
            words = shap_values.data[0]
            values = shap_values.values[0, :, 1]  # class 1 = Fake

            # Build highlighted text
            highlighted: List[Dict[str, Any]] = []
            for word, val in zip(words, values):
                word_str = str(word).strip()
                if not word_str:
                    continue
                score = float(val)
                direction = "fake" if score > 0 else "real"
                color = self._score_to_color(score)
                highlighted.append({
                    "word": word_str,
                    "score": round(abs(score), 5),
                    "raw_score": round(score, 5),
                    "direction": direction,
                    "color": color,
                })

            # Top N by absolute score
            top_words = sorted(highlighted, key=lambda x: x["score"], reverse=True)[:top_n]

            return {
                "top_words": top_words,
                "highlighted_text": highlighted,
                "method": "shap",
            }

        except Exception as exc:
            logger.warning(f"SHAP explanation failed, falling back to TF-IDF: {exc}")
            return self._explain_tfidf(text, top_n)

    def _explain_tfidf(self, text: str, top_n: int) -> Dict[str, Any]:
        """Fallback: use TF-IDF coefficient-weighted explanation."""
        try:
            X_vec = self.vectorizer.transform([text])
            tfidf_vals = np.array(X_vec.todense()).flatten()
            contributions = tfidf_vals * self.coef_fake

            # Build highlighted text from input words
            words_in_text = text.split()
            highlighted: List[Dict[str, Any]] = []

            for word in words_in_text:
                clean_word = re.sub(r'[^\w]', '', word.lower())
                # Find this word in vocabulary
                vocab = self.vectorizer.vocabulary_
                if clean_word in vocab:
                    idx = vocab[clean_word]
                    score = float(contributions[idx])
                    direction = "fake" if score > 0 else "real"
                    color = self._score_to_color(score)
                    highlighted.append({
                        "word": word,
                        "score": round(abs(score), 5),
                        "raw_score": round(score, 5),
                        "direction": direction,
                        "color": color,
                    })
                else:
                    # Word not in vocabulary — neutral
                    highlighted.append({
                        "word": word,
                        "score": 0.0,
                        "raw_score": 0.0,
                        "direction": "neutral",
                        "color": "transparent",
                    })

            # Top N by absolute score
            top_words = sorted(
                [w for w in highlighted if w["score"] > 0],
                key=lambda x: x["score"],
                reverse=True,
            )[:top_n]

            return {
                "top_words": top_words,
                "highlighted_text": highlighted,
                "method": "tfidf_coefficients",
            }

        except Exception as exc:
            logger.warning(f"TF-IDF explanation failed: {exc}")
            return {
                "top_words": [],
                "highlighted_text": [],
                "method": "error",
            }

    @staticmethod
    def _score_to_color(score: float) -> str:
        """
        Map a SHAP/contribution score to a CSS rgba color.
        Positive (fake) = red, Negative (real) = green.
        """
        intensity = min(abs(score) * 3, 0.6)  # cap at 0.6 opacity
        if score > 0:
            return f"rgba(255, 77, 109, {intensity:.2f})"   # red (fake)
        elif score < 0:
            return f"rgba(34, 197, 94, {intensity:.2f})"    # green (real)
        else:
            return "transparent"

    def is_ready(self) -> bool:
        """Return True if the explainer is ready."""
        return self._ready
