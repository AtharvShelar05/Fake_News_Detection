"""
realtime — Real-Time Fake News Detection Package
=================================================
Modules:
  predictor    — Core ML prediction pipeline
  fact_checker — Google Fact Check Tools API integration
  ensemble     — Weighted ensemble of baseline + robust models
  explainer    — TF-IDF keyword explainability
"""

__version__ = "1.0.0"
__all__ = ["predictor", "fact_checker", "ensemble", "explainer"]
