"""
Baseline Fake News Detection Model
Uses TF-IDF vectorization and Logistic Regression for classification
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class BaselineModel:
    """
    Baseline fake news detector using TF-IDF + Logistic Regression
    """
    
    def __init__(self, max_features=5000, random_state=42):
        """
        Initialize baseline model.
        
        Args:
            max_features (int): Maximum number of TF-IDF features
            random_state (int): Random seed for reproducibility
        """
        self.max_features = max_features
        self.random_state = random_state
        self.vectorizer = None
        self.model = None
        self.results = {}
        
    def load_data(self, data_path):
        """
        Load cleaned dataset from CSV.
        
        Args:
            data_path (str): Path to clean_data.csv
            
        Returns:
            tuple: (X_texts, y_labels) - texts and corresponding labels
        """
        print(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        
        # Use clean_text column for model training
        X = df['clean_text'].values
        y = df['label'].values
        
        print(f"Dataset size: {len(X)} samples")
        print(f"Class distribution: {np.bincount(y)}")
        
        return X, y
    
    def train(self, X_train, y_train):
        """
        Train baseline model on training data.
        
        Args:
            X_train (array): Training texts
            y_train (array): Training labels
        """
        print("\n=== Training Baseline Model ===")
        
        # Vectorize texts using TF-IDF
        print(f"Vectorizing texts with max {self.max_features} features...")
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        X_train_vec = self.vectorizer.fit_transform(X_train)
        
        print(f"Feature matrix shape: {X_train_vec.shape}")
        
        # Train Logistic Regression classifier
        print("Training Logistic Regression classifier...")
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=self.random_state,
            n_jobs=-1,
            solver='lbfgs'
        )
        self.model.fit(X_train_vec, y_train)
        print("Model training completed.")
    
    def evaluate(self, X_test, y_test, dataset_name="Test"):
        """
        Evaluate model on test data.
        
        Args:
            X_test (array): Test texts
            y_test (array): Test labels
            dataset_name (str): Name of dataset for logging
            
        Returns:
            dict: Evaluation metrics
        """
        print(f"\n=== Evaluating on {dataset_name} Data ===")
        
        # Vectorize test data
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Make predictions
        y_pred = self.model.predict(X_test_vec)
        
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
    
    def save_model(self, model_path):
        """
        Save trained model to disk.
        
        Args:
            model_path (str): Path to save model
        """
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'vectorizer': self.vectorizer,
            'max_features': self.max_features
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
        self.vectorizer = model_data['vectorizer']
        self.max_features = model_data['max_features']
        
        print(f"Model loaded from {model_path}")
    
    def predict(self, texts):
        """
        Make predictions on new texts.
        
        Args:
            texts (array): Input texts for prediction
            
        Returns:
            array: Predicted labels (0=real, 1=fake)
        """
        X_vec = self.vectorizer.transform(texts)
        predictions = self.model.predict(X_vec)
        return predictions
    
    def predict_proba(self, texts):
        """
        Get prediction probabilities.
        
        Args:
            texts (array): Input texts
            
        Returns:
            array: Prediction probabilities
        """
        X_vec = self.vectorizer.transform(texts)
        probabilities = self.model.predict_proba(X_vec)
        return probabilities


def main():
    """
    Main function: Train and evaluate baseline model
    """
    # Paths
    data_path = "data/processed/clean_data.csv"
    model_save_path = "ml_models/saved_models/baseline_model.pkl"
    results_save_path = "ml_models/saved_models/baseline_results.json"
    
    # Initialize model
    baseline = BaselineModel(max_features=5000, random_state=42)
    
    # Load data
    X, y = baseline.load_data(data_path)
    
    # Split into train-test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    baseline.train(X_train, y_train)
    
    # Evaluate on clean data
    test_metrics, _ = baseline.evaluate(X_test, y_test, "Clean Test")
    
    # Save model
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    baseline.save_model(model_save_path)
    
    # Save results
    results = {
        'model_type': 'Baseline (TF-IDF + Logistic Regression)',
        'test_metrics': test_metrics,
        'vectorizer_params': {
            'max_features': baseline.max_features,
            'ngram_range': (1, 2),
            'stop_words': 'english'
        }
    }
    
    os.makedirs(os.path.dirname(results_save_path), exist_ok=True)
    with open(results_save_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {results_save_path}")


if __name__ == "__main__":
    main()
