"""
Machine Learning Models Module
Adversarially Robust Fake News Detection

This module implements baseline and robust fake news detection models with
comprehensive adversarial robustness evaluation.

Components:
-----------
- baseline_model: TF-IDF + Logistic Regression baseline
- adversarial_attacks: Strategies for generating adversarial examples
- robust_model: Adversarially trained model with embeddings
- evaluate_models: Comprehensive model evaluation framework

Key Classes:
------------
from baseline_model import BaselineModel
from adversarial_attacks import AdversarialAttacks
from robust_model import RobustModel
from evaluate_models import ModelEvaluator

Usage:
------
# Train and evaluate
evaluator = ModelEvaluator(results_save_path="data/processed/model_evaluation.json")
results = evaluator.evaluate_models("data/processed/clean_data.csv")
evaluator.save_results()
evaluator.print_summary()

# Individual model usage
baseline = BaselineModel(max_features=5000)
baseline.train(X_train, y_train)
predictions = baseline.predict(X_test)

# Adversarial attacks
attacker = AdversarialAttacks(random_state=42)
adversarial_text = attacker.synonym_substitution_attack(text)

# Robust model
robust = RobustModel(random_state=42)
robust.train_adversarial_model(X_train, y_train, augmentation_ratio=0.5)
robustness = robust.evaluate_adversarial_robustness(X_test, y_test)

See MODULE_DOCUMENTATION.md for detailed API documentation.
"""

__author__ = "ML Engineering Team"
__version__ = "1.0.0"
__all__ = ["BaselineModel", "AdversarialAttacks", "RobustModel", "ModelEvaluator"]
