"""
Comprehensive Model Evaluation: Baseline vs Robust
Compares performance on clean and adversarially attacked data
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from baseline_model import BaselineModel
from robust_model import RobustModel
from adversarial_attacks import AdversarialAttacks


class ModelEvaluator:
    """
    Comprehensive evaluation framework for fake news detection models
    """
    
    def __init__(self, results_save_path="data/processed/model_evaluation.json"):
        """
        Initialize evaluator.
        
        Args:
            results_save_path (str): Path to save evaluation results
        """
        self.results_save_path = results_save_path
        self.all_results = {}
        self.attacker = AdversarialAttacks(random_state=42)
    
    def evaluate_models(self, data_path):
        """
        Train and evaluate both baseline and robust models.
        
        Args:
            data_path (str): Path to clean_data.csv
            
        Returns:
            dict: Comprehensive evaluation results
        """
        print("\n" + "="*80)
        print("COMPREHENSIVE MODEL EVALUATION")
        print("="*80)
        
        # Load data
        print("\n[1/5] Loading and splitting data...")
        df = pd.read_csv(data_path)
        X = df['clean_text'].values
        y = df['label'].values
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training samples: {len(X_train)}")
        print(f"Test samples: {len(X_test)}")
        
        # === BASELINE MODEL ===
        print("\n[2/5] Training Baseline Model (TF-IDF + Logistic Regression)...")
        baseline = BaselineModel(max_features=5000, random_state=42)
        baseline.train(X_train, y_train)
        
        baseline_clean_metrics, baseline_clean_preds = baseline.evaluate(X_test, y_test, "Clean Test")
        
        # Generate adversarial test set for baseline
        print("\n[3/5] Generating adversarial test set and evaluating baseline...")
        baseline_adversarial_results = self._evaluate_baseline_adversarial(
            baseline, X_test, y_test
        )
        
        # === ROBUST MODEL ===
        print("\n[4/5] Training Robust Model (Embeddings + Adversarial Training)...")
        robust = RobustModel(random_state=42)
        robust.train_adversarial_model(X_train, y_train, augmentation_ratio=0.5)
        
        robust_clean_metrics, robust_clean_preds = robust.evaluate(X_test, y_test, "Clean Test")
        
        # Evaluate robust model on adversarial data
        print("\nEvaluating robust model on adversarial data...")
        robust_adversarial_results = robust.evaluate_adversarial_robustness(X_test, y_test, 'all')
        
        # === COMPREHENSIVE RESULTS ===
        print("\n[5/5] Compiling results...")
        
        results = {
            'evaluation_date': pd.Timestamp.now().isoformat(),
            'dataset_info': {
                'total_samples': len(X),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'class_distribution': {
                    'real_news': int(np.sum(y == 0)),
                    'fake_news': int(np.sum(y == 1))
                }
            },
            'baseline_model': {
                'type': 'TF-IDF + Logistic Regression',
                'clean_test_performance': baseline_clean_metrics,
                'adversarial_performance': baseline_adversarial_results,
                'average_robustness_drop': np.mean([
                    baseline_adversarial_results['synonym']['robustness_drop_percent'],
                    baseline_adversarial_results['character']['robustness_drop_percent'],
                    baseline_adversarial_results['paraphrase']['robustness_drop_percent']
                ])
            },
            'robust_model': {
                'type': 'Embeddings + Adversarial Training',
                'clean_test_performance': robust_clean_metrics,
                'adversarial_performance': robust_adversarial_results,
                'average_robustness_drop': np.mean([
                    robust_adversarial_results['synonym']['robustness_drop_percent'],
                    robust_adversarial_results['character']['robustness_drop_percent'],
                    robust_adversarial_results['paraphrase']['robustness_drop_percent']
                ]) if isinstance(robust_adversarial_results, dict) and 'synonym' in robust_adversarial_results else 0
            },
            'comparative_analysis': self._generate_comparative_analysis(
                baseline_clean_metrics,
                robust_clean_metrics,
                baseline_adversarial_results,
                robust_adversarial_results
            )
        }
        
        self.all_results = results
        return results
    
    def _evaluate_baseline_adversarial(self, baseline_model, X_test, y_test):
        """
        Evaluate baseline model on adversarial data.
        
        Args:
            baseline_model: Trained baseline model
            X_test: Test texts
            y_test: Test labels
            
        Returns:
            dict: Robustness metrics
        """
        attacks = ['synonym', 'character', 'paraphrase']
        robustness_results = {}
        
        X_test_emb = baseline_model.vectorizer.transform(X_test)
        y_pred_clean = baseline_model.model.predict(X_test_emb)
        clean_accuracy = np.mean(y_pred_clean == y_test)
        
        for attack in attacks:
            print(f"  Evaluating {attack} attack on baseline...")
            
            adversarial_pairs = self.attacker.generate_adversarial_dataset(X_test, attack_type=attack)
            adversarial_texts = [pair[1] for pair in adversarial_pairs]
            
            X_adv_emb = baseline_model.vectorizer.transform(adversarial_texts)
            y_pred_adv = baseline_model.model.predict(X_adv_emb)
            
            y_test_matched = y_test[:len(y_pred_adv)]
            adv_accuracy = np.mean(y_pred_adv == y_test_matched)
            robustness_drop = (clean_accuracy - adv_accuracy) / (clean_accuracy + 1e-8)
            
            robustness_results[attack] = {
                'clean_accuracy': float(clean_accuracy),
                'adversarial_accuracy': float(adv_accuracy),
                'robustness_drop_percent': float(robustness_drop * 100)
            }
        
        return robustness_results
    
    def _generate_comparative_analysis(self, baseline_clean, robust_clean, 
                                       baseline_adv, robust_adv):
        """
        Generate comparative analysis between models.
        
        Args:
            baseline_clean (dict): Baseline clean performance
            robust_clean (dict): Robust clean performance
            baseline_adv (dict): Baseline adversarial performance
            robust_adv (dict): Robust adversarial performance
            
        Returns:
            dict: Comparative metrics
        """
        baseline_avg_drop = np.mean([
            baseline_adv['synonym']['robustness_drop_percent'],
            baseline_adv['character']['robustness_drop_percent'],
            baseline_adv['paraphrase']['robustness_drop_percent']
        ])
        
        robust_avg_drop = np.mean([
            robust_adv['synonym']['robustness_drop_percent'],
            robust_adv['character']['robustness_drop_percent'],
            robust_adv['paraphrase']['robustness_drop_percent']
        ]) if isinstance(robust_adv, dict) and 'synonym' in robust_adv else 0
        
        return {
            'clean_accuracy_improvement': float(robust_clean['accuracy'] - baseline_clean['accuracy']),
            'robustness_improvement': float(baseline_avg_drop - robust_avg_drop),
            'baseline_avg_robustness_drop_percent': float(baseline_avg_drop),
            'robust_avg_robustness_drop_percent': float(robust_avg_drop),
            'recommendation': 'Robust model recommended' if robust_avg_drop < baseline_avg_drop else 'Compare trade-offs'
        }
    
    def save_results(self):
        """
        Save evaluation results to JSON.
        """
        os.makedirs(os.path.dirname(self.results_save_path), exist_ok=True)
        
        with open(self.results_save_path, 'w') as f:
            json.dump(self.all_results, f, indent=2)
        
        print(f"\n✓ Results saved to {self.results_save_path}")
    
    def print_summary(self):
        """
        Print human-readable summary of results.
        """
        if not self.all_results:
            print("No results to display. Run evaluate_models() first.")
            return
        
        print("\n" + "="*80)
        print("EVALUATION SUMMARY")
        print("="*80)
        
        # Clean accuracy comparison
        print("\n[CLEAN DATA PERFORMANCE]")
        baseline_acc = self.all_results['baseline_model']['clean_test_performance']['accuracy']
        robust_acc = self.all_results['robust_model']['clean_test_performance']['accuracy']
        
        print(f"Baseline Accuracy: {baseline_acc:.4f}")
        print(f"Robust Accuracy:   {robust_acc:.4f}")
        print(f"Improvement:       {(robust_acc - baseline_acc):.4f} ({(robust_acc - baseline_acc)*100:.2f}%)")
        
        # Adversarial robustness comparison
        print("\n[ADVERSARIAL ROBUSTNESS]")
        baseline_drop = self.all_results['baseline_model']['average_robustness_drop']
        robust_drop = self.all_results['robust_model']['average_robustness_drop']
        
        print(f"Baseline Avg Robustness Drop: {baseline_drop:.2f}%")
        print(f"Robust Avg Robustness Drop:   {robust_drop:.2f}%")
        print(f"Improvement:                  {(baseline_drop - robust_drop):.2f}%")
        
        # Per-attack analysis
        print("\n[PER-ATTACK ANALYSIS]")
        for attack in ['synonym', 'character', 'paraphrase']:
            print(f"\n{attack.upper()}:")
            baseline_adv_acc = self.all_results['baseline_model']['adversarial_performance'][attack]['adversarial_accuracy']
            robust_adv_acc = self.all_results['robust_model']['adversarial_performance'][attack]['adversarial_accuracy']
            
            print(f"  Baseline Accuracy: {baseline_adv_acc:.4f}")
            print(f"  Robust Accuracy:   {robust_adv_acc:.4f}")
            print(f"  Improvement:       {(robust_adv_acc - baseline_adv_acc):.4f}")
        
        # Final recommendation
        print("\n[RECOMMENDATION]")
        print(self.all_results['comparative_analysis']['recommendation'])
        print("="*80 + "\n")


def main():
    """
    Main function: Run comprehensive model evaluation
    """
    # Configuration
    data_path = "data/processed/clean_data.csv"
    results_save_path = "data/processed/model_evaluation.json"
    
    # Initialize evaluator
    evaluator = ModelEvaluator(results_save_path=results_save_path)
    
    # Run evaluation
    results = evaluator.evaluate_models(data_path)
    
    # Save and display results
    evaluator.save_results()
    evaluator.print_summary()


if __name__ == "__main__":
    main()
