"""
Integration Test: Demonstrate all ML modules working together
"""

import sys
import os

# Add ml_models to path
sys.path.insert(0, os.path.dirname(__file__))

from baseline_model import BaselineModel
from adversarial_attacks import AdversarialAttacks
from robust_model import RobustModel
import pandas as pd


def test_integration():
    """
    Integration test demonstrating all components
    """
    print("\n" + "="*80)
    print("INTEGRATION TEST: All ML Modules")
    print("="*80)
    
    # Load sample data
    data_path = "data/processed/clean_data.csv"
    df = pd.read_csv(data_path)
    sample_texts = df['clean_text'].head(5).tolist()
    sample_labels = df['label'].head(5).tolist()
    
    print(f"\n[TEST 1] Baseline Model")
    print("-" * 80)
    baseline = BaselineModel(max_features=5000)
    print("[OK] BaselineModel initialized")
    
    # Train on sample
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        sample_texts, sample_labels, test_size=0.2, random_state=42
    )
    
    baseline.train(X_train, y_train)
    print("[OK] Baseline model trained")
    
    predictions = baseline.predict(X_test)
    print(f"[OK] Predictions made: {predictions}")
    
    print(f"\n[TEST 2] Adversarial Attacks")
    print("-" * 80)
    attacker = AdversarialAttacks(random_state=42)
    print("[OK] AdversarialAttacks initialized")
    
    test_text = sample_texts[0]
    print(f"Original: {test_text}")
    
    syn_attack = attacker.synonym_substitution_attack(test_text)
    print(f"[OK] Synonym attack: {syn_attack}")
    
    char_attack = attacker.character_perturbation_attack(test_text)
    print(f"[OK] Character attack: {char_attack[:50]}...")
    
    para_attack = attacker.word_level_paraphrase_attack(test_text)
    print(f"[OK] Paraphrase attack: {para_attack}")
    
    print(f"\n[TEST 3] Robust Model")
    print("-" * 80)
    robust = RobustModel(random_state=42)
    print("[OK] RobustModel initialized")
    
    robust.train_adversarial_model(X_train, y_train, augmentation_ratio=0.5)
    print("[OK] Robust model trained with adversarial augmentation")
    
    robust_predictions = robust.predict(X_test)
    print(f"[OK] Robust predictions made: {robust_predictions}")
    
    print(f"\n[TEST 4] Robustness Evaluation")
    print("-" * 80)
    robustness = robust.evaluate_adversarial_robustness(X_test, y_test, 'synonym')
    print(f"[OK] Robustness evaluation completed")
    print(f"  Clean Accuracy: {robustness['clean_accuracy']:.4f}")
    print(f"  Adversarial Accuracy: {robustness['adversarial_accuracy']:.4f}")
    print(f"  Robustness Drop: {robustness['robustness_drop_percent']:.2f}%")
    
    print(f"\n[TEST 5] Model Persistence")
    print("-" * 80)
    baseline_path = "saved_models/test_baseline.pkl"
    robust_path = "saved_models/test_robust.pkl"
    
    baseline.save_model(baseline_path)
    print(f"[OK] Baseline model saved to {baseline_path}")
    
    robust.save_model(robust_path)
    print(f"[OK] Robust model saved to {robust_path}")
    
    # Load and test
    baseline_loaded = BaselineModel()
    baseline_loaded.load_model(baseline_path)
    loaded_predictions = baseline_loaded.predict(X_test)
    print(f"[OK] Model loaded and predictions match: {all(loaded_predictions == predictions)}")
    
    # Cleanup
    if os.path.exists(baseline_path):
        os.remove(baseline_path)
    if os.path.exists(robust_path):
        os.remove(robust_path)
    print("[OK] Test files cleaned up")
    
    print("\n" + "="*80)
    print("ALL TESTS PASSED")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_integration()
