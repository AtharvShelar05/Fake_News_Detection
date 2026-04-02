"""
Robust Fake News Detection Model with Adversarial Training
Uses transformer-based embeddings with adversarial training for robustness
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Handle both direct and package imports
try:
    from adversarial_attacks import AdversarialAttacks
except ImportError:
    from ml_models.adversarial_attacks import AdversarialAttacks


class RobustModel:
    """
    Robust fake news detector using contextual embeddings + adversarial training
    Implements adversarial data augmentation strategy for robustness
    """
    
    def __init__(self, random_state=42, embedding_dim=768):
        """
        Initialize robust model.
        
        Args:
            random_state (int): Random seed for reproducibility
            embedding_dim (int): Dimensionality of embeddings (simulated)
        """
        self.random_state = random_state
        self.embedding_dim = embedding_dim
        self.model = None
        self.attacker = AdversarialAttacks(random_state=random_state)
        self.results = {}
        self.embedding_vectors = {}  # Cache for embeddings
        
        np.random.seed(random_state)
    
    def generate_robust_embeddings(self, text: str) -> np.ndarray:
        """
        Generate robust embeddings (simulated contextual embeddings).
        In production, use BERT/RoBERTa via HuggingFace transformers.
        
        Args:
            text (str): Input text
            
        Returns:
            np.ndarray: Embedding vector of shape (embedding_dim,)
        """
        # Hash text to ensure consistent embeddings
        if text in self.embedding_vectors:
            return self.embedding_vectors[text]
        
        # Simulate contextual embeddings using text statistics
        words = text.lower().split()
        embedding = np.zeros(self.embedding_dim)
        
        # Word frequency-based features
        for i, word in enumerate(words[:self.embedding_dim // 2]):
            embedding[i] = ord(word[0]) / 255.0 if word else 0
        
        # Character n-gram based features
        chars = list(text)
        for i, char in enumerate(chars[:self.embedding_dim // 2]):
            embedding[self.embedding_dim // 2 + i % (self.embedding_dim // 2)] = ord(char) / 255.0
        
        # Add randomness based on text content for uniqueness
        np.random.seed(hash(text) % 2**32)
        noise = np.random.randn(self.embedding_dim) * 0.1
        embedding = embedding + noise
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        self.embedding_vectors[text] = embedding
        return embedding
    
    def embed_texts(self, texts):
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts (list): List of texts
            
        Returns:
            np.ndarray: Matrix of shape (len(texts), embedding_dim)
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_robust_embeddings(text)
            embeddings.append(embedding)
        return np.array(embeddings)
    
    def train_baseline_model(self, X_train, y_train):
        """
        Train model on clean data only (baseline).
        
        Args:
            X_train (list): Training texts
            y_train (np.ndarray): Training labels
        """
        print("\n=== Training Robust Model (Clean Data Only) ===")
        
        # Generate embeddings
        print("Generating embeddings for training data...")
        X_train_emb = self.embed_texts(X_train)
        
        # Train classifier on embeddings
        print("Training Logistic Regression on embeddings...")
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.model.fit(X_train_emb, y_train)
        print("Baseline model training completed.")
    
    def train_adversarial_model(self, X_train, y_train, augmentation_ratio=0.5):
        """
        Train model on augmented dataset (original + adversarial examples).
        
        Args:
            X_train (list): Training texts
            y_train (np.ndarray): Training labels
            augmentation_ratio (float): Ratio of adversarial examples to add
        """
        print("\n=== Training Robust Model (Adversarial Training) ===")
        
        # Generate adversarial examples
        print(f"Generating adversarial training examples at {augmentation_ratio:.1%} ratio...")
        X_train_list = list(X_train)
        
        # Create augmented dataset
        X_augmented = X_train_list.copy()
        y_augmented = list(y_train)
        
        # Add adversarial samples
        num_to_augment = max(1, int(len(X_train) * augmentation_ratio))
        augment_indices = np.random.choice(len(X_train), num_to_augment, replace=False)
        
        for idx in augment_indices:
            text = X_train_list[idx]
            label = y_train[idx]
            
            # Generate 3 adversarial variants per original
            adversarial_texts = [
                self.attacker.synonym_substitution_attack(text),
                self.attacker.character_perturbation_attack(text),
                self.attacker.word_level_paraphrase_attack(text)
            ]
            
            X_augmented.extend(adversarial_texts)
            y_augmented.extend([label] * 3)
        
        print(f"Augmented dataset size: {len(X_augmented)} (original: {len(X_train)})")
        
        # Generate embeddings for augmented data
        print("Generating embeddings for augmented data...")
        X_augmented_emb = self.embed_texts(X_augmented)
        
        # Train classifier
        print("Training Logistic Regression on augmented embeddings...")
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.model.fit(X_augmented_emb, np.array(y_augmented))
        print("Adversarial training completed.")
    
    def evaluate(self, X_test, y_test, dataset_name="Test"):
        """
        Evaluate model on test data.
        
        Args:
            X_test (list): Test texts
            y_test (np.ndarray): Test labels
            dataset_name (str): Name of dataset for logging
            
        Returns:
            dict: Evaluation metrics
        """
        print(f"\n=== Evaluating on {dataset_name} Data ===")
        
        # Generate embeddings
        X_test_emb = self.embed_texts(X_test)
        
        # Make predictions
        y_pred = self.model.predict(X_test_emb)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'dataset': dataset_name,
            'samples': len(X_test)
        }
        
        print(f"Accuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1-Score:  {f1:.4f}")
        
        return metrics, y_pred
    
    def evaluate_adversarial_robustness(self, X_test, y_test, attack_type='all'):
        """
        Evaluate model robustness against adversarial attacks.
        
        Args:
            X_test (list): Test texts
            y_test (np.ndarray): Test labels
            attack_type (str): Type of attack to evaluate
            
        Returns:
            dict: Robustness metrics
        """
        print(f"\n=== Evaluating Adversarial Robustness ({attack_type.upper()}) ===")
        
        X_test_emb = self.embed_texts(X_test)
        y_pred_clean = self.model.predict(X_test_emb)
        clean_accuracy = accuracy_score(y_test, y_pred_clean)
        
        # Generate adversarial test set
        if attack_type == 'all':
            attacks = ['synonym', 'character', 'paraphrase']
            robustness_results = {}
            
            for attack in attacks:
                adversarial_pairs = self.attacker.generate_adversarial_dataset(X_test, attack_type=attack)
                adversarial_texts = [pair[1] for pair in adversarial_pairs]
                
                X_adv_emb = self.embed_texts(adversarial_texts)
                y_pred_adv = self.model.predict(X_adv_emb)
                
                # Match predictions to original labels
                y_test_matched = y_test[:len(y_pred_adv)]
                adv_accuracy = accuracy_score(y_test_matched, y_pred_adv)
                
                robustness_drop = (clean_accuracy - adv_accuracy) / (clean_accuracy + 1e-8)
                robustness_results[attack] = {
                    'clean_accuracy': float(clean_accuracy),
                    'adversarial_accuracy': float(adv_accuracy),
                    'robustness_drop_percent': float(robustness_drop * 100)
                }
                
                print(f"\n{attack.upper()} Attack:")
                print(f"  Clean Accuracy:       {clean_accuracy:.4f}")
                print(f"  Adversarial Accuracy: {adv_accuracy:.4f}")
                print(f"  Robustness Drop:      {robustness_drop*100:.2f}%")
            
            return robustness_results
        else:
            adversarial_pairs = self.attacker.generate_adversarial_dataset(X_test, attack_type=attack_type)
            adversarial_texts = [pair[1] for pair in adversarial_pairs]
            
            X_adv_emb = self.embed_texts(adversarial_texts)
            y_pred_adv = self.model.predict(X_adv_emb)
            
            y_test_matched = y_test[:len(y_pred_adv)]
            adv_accuracy = accuracy_score(y_test_matched, y_pred_adv)
            robustness_drop = (clean_accuracy - adv_accuracy) / (clean_accuracy + 1e-8)
            
            print(f"Clean Accuracy:       {clean_accuracy:.4f}")
            print(f"Adversarial Accuracy: {adv_accuracy:.4f}")
            print(f"Robustness Drop:      {robustness_drop*100:.2f}%")
            
            return {
                'clean_accuracy': float(clean_accuracy),
                'adversarial_accuracy': float(adv_accuracy),
                'robustness_drop_percent': float(robustness_drop * 100)
            }
    
    def save_model(self, model_path):
        """
        Save trained model to disk.
        
        Args:
            model_path (str): Path to save model
        """
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'embedding_dim': self.embedding_dim,
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path):
        """
        Load trained model from disk.
        
        Args:
            model_path (str): Path to saved model
        """
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.embedding_dim = model_data['embedding_dim']
        
        print(f"Model loaded from {model_path}")
    
    def predict(self, texts):
        """
        Make predictions on new texts.
        
        Args:
            texts (list): Input texts
            
        Returns:
            np.ndarray: Predicted labels
        """
        X_emb = self.embed_texts(texts)
        predictions = self.model.predict(X_emb)
        return predictions


def main():
    """
    Main function: Train and evaluate robust model
    """
    # Paths
    data_path = "data/processed/clean_data.csv"
    baseline_model_path = "ml_models/saved_models/robust_model_baseline.pkl"
    adversarial_model_path = "ml_models/saved_models/robust_model_adversarial.pkl"
    results_save_path = "ml_models/saved_models/robust_model_results.json"
    
    # Load data
    print("Loading data...")
    df = pd.read_csv(data_path)
    X = df['clean_text'].values
    y = df['label'].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # === Train Baseline Robust Model ===
    robust_baseline = RobustModel(random_state=42)
    robust_baseline.train_baseline_model(X_train, y_train)
    
    test_metrics_baseline, _ = robust_baseline.evaluate(X_test, y_test, "Clean Test")
    adv_robustness_baseline = robust_baseline.evaluate_adversarial_robustness(X_test, y_test, 'all')
    
    os.makedirs(os.path.dirname(baseline_model_path), exist_ok=True)
    robust_baseline.save_model(baseline_model_path)
    
    # === Train Adversarially Trained Model ===
    robust_adversarial = RobustModel(random_state=42)
    robust_adversarial.train_adversarial_model(X_train, y_train, augmentation_ratio=0.5)
    
    test_metrics_adversarial, _ = robust_adversarial.evaluate(X_test, y_test, "Clean Test")
    adv_robustness_adversarial = robust_adversarial.evaluate_adversarial_robustness(X_test, y_test, 'all')
    
    os.makedirs(os.path.dirname(adversarial_model_path), exist_ok=True)
    robust_adversarial.save_model(adversarial_model_path)
    
    # Save results
    results = {
        'baseline_model': {
            'test_metrics': test_metrics_baseline,
            'adversarial_robustness': adv_robustness_baseline
        },
        'adversarial_training_model': {
            'test_metrics': test_metrics_adversarial,
            'adversarial_robustness': adv_robustness_adversarial
        },
        'model_config': {
            'embedding_dim': 768,
            'training_strategy': 'adversarial_augmentation',
            'augmentation_ratio': 0.5
        }
    }
    
    os.makedirs(os.path.dirname(results_save_path), exist_ok=True)
    with open(results_save_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {results_save_path}")


if __name__ == "__main__":
    main()
