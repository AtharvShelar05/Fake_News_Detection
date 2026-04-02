"""
Feature Engineering Module for Fake News Propagation Analysis

This module generates TF-IDF features from cleaned text data
for use in machine learning models.
"""

import pandas as pd
import numpy as np
import logging
import os
import pickle
from typing import Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Feature engineering pipeline using TF-IDF vectorization.
    """
    
    def __init__(self, max_features: int = 5000, min_df: int = 2, max_df: float = 0.95):
        """
        Initialize the feature engineer.
        
        Args:
            max_features (int): Maximum number of features to extract
            min_df (int): Ignore terms with document frequency < min_df
            max_df (float): Ignore terms with document frequency > max_df
        """
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.vectorizer = None
        self.feature_names = None
        logger.info(f"Initialized FeatureEngineer with max_features={max_features}")
    
    def fit_transform(self, texts: pd.Series) -> Tuple[np.ndarray, list]:
        """
        Fit vectorizer on texts and return TF-IDF features.
        
        Args:
            texts (pd.Series): Series of text documents
            
        Returns:
            Tuple[np.ndarray, list]: TF-IDF matrix and feature names
        """
        logger.info(f"Fitting TF-IDF vectorizer on {len(texts)} documents...")
        
        # Create vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            min_df=self.min_df,
            max_df=self.max_df,
            ngram_range=(1, 2),  # Unigrams and bigrams
            lowercase=True,
            stop_words='english'
        )
        
        # Fit and transform
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        logger.info(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
        logger.info(f"Number of features extracted: {len(self.feature_names)}")
        
        return tfidf_matrix, self.feature_names
    
    def transform(self, texts: pd.Series) -> np.ndarray:
        """
        Transform texts using fitted vectorizer.
        
        Args:
            texts (pd.Series): Series of text documents
            
        Returns:
            np.ndarray: TF-IDF matrix
        """
        if self.vectorizer is None:
            raise ValueError("Vectorizer not fitted. Call fit_transform first.")
        
        logger.info(f"Transforming {len(texts)} documents...")
        return self.vectorizer.transform(texts)
    
    def save_vectorizer(self, filepath: str) -> None:
        """
        Save fitted vectorizer to disk.
        
        Args:
            filepath (str): Path to save vectorizer
        """
        if self.vectorizer is None:
            raise ValueError("No vectorizer to save. Call fit_transform first.")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        logger.info(f"Vectorizer saved to {filepath}")
    
    def load_vectorizer(self, filepath: str) -> None:
        """
        Load fitted vectorizer from disk.
        
        Args:
            filepath (str): Path to vectorizer file
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Vectorizer file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            self.vectorizer = pickle.load(f)
        self.feature_names = self.vectorizer.get_feature_names_out()
        logger.info(f"Vectorizer loaded from {filepath}")


def get_top_features(tfidf_matrix: np.ndarray, feature_names: list, 
                     top_n: int = 20) -> dict:
    """
    Extract top TF-IDF features.
    
    Args:
        tfidf_matrix (np.ndarray): TF-IDF sparse matrix
        feature_names (list): Feature names
        top_n (int): Number of top features to extract
        
    Returns:
        dict: Top features and their average scores
    """
    # Calculate mean TF-IDF score for each feature
    mean_tfidf = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
    
    # Get indices of top features
    top_indices = np.argsort(mean_tfidf)[-top_n:][::-1]
    
    # Create dictionary of top features
    top_features = {
        feature_names[i]: float(mean_tfidf[i])
        for i in top_indices
    }
    
    return top_features


def generate_features(input_path: str, output_dir: str, 
                     max_features: int = 5000) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Main feature engineering pipeline.
    
    Args:
        input_path (str): Path to cleaned data CSV
        output_dir (str): Directory to save features
        max_features (int): Maximum number of TF-IDF features
        
    Returns:
        Tuple[pd.DataFrame, np.ndarray]: Dataframe with metadata and TF-IDF matrix
    """
    logger.info("Starting feature engineering pipeline...")
    
    # Load cleaned data
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    df = pd.read_csv(input_path)
    logger.info(f"Loaded {len(df)} records from {input_path}")
    
    # Check for clean_text column
    if 'clean_text' not in df.columns:
        logger.error("'clean_text' column not found. Run preprocess.py first.")
        raise ValueError("'clean_text' column required")
    
    # Initialize feature engineer
    engineer = FeatureEngineer(max_features=max_features)
    
    # Generate TF-IDF features
    tfidf_matrix, feature_names = engineer.fit_transform(df['clean_text'])
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save TF-IDF matrix as sparse format
    tfidf_path = os.path.join(output_dir, 'tfidf_features.npz')
    np.savez_compressed(
        tfidf_path,
        data=tfidf_matrix.data,
        indices=tfidf_matrix.indices,
        indptr=tfidf_matrix.indptr,
        shape=tfidf_matrix.shape
    )
    logger.info(f"TF-IDF features saved to {tfidf_path}")
    
    # Save feature names
    features_path = os.path.join(output_dir, 'feature_names.npy')
    np.save(features_path, feature_names)
    logger.info(f"Feature names saved to {features_path}")
    
    # Save vectorizer
    vectorizer_path = os.path.join(output_dir, 'tfidf_vectorizer.pkl')
    engineer.save_vectorizer(vectorizer_path)
    
    # Save metadata
    metadata_path = os.path.join(output_dir, 'features_metadata.csv')
    metadata_df = df[['label', 'user_id', 'timestamp']].copy()
    metadata_df.to_csv(metadata_path, index=False)
    logger.info(f"Metadata saved to {metadata_path}")
    
    # Get and display top features
    print("\n" + "="*60)
    print("FEATURE ENGINEERING STATISTICS")
    print("="*60)
    print(f"Total Documents: {tfidf_matrix.shape[0]}")
    print(f"Total Features: {tfidf_matrix.shape[1]}")
    print(f"Sparsity: {1 - (tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1])):.4f}")
    
    # Top features
    top_features = get_top_features(tfidf_matrix, feature_names, top_n=20)
    print(f"\nTop 20 Features by Mean TF-IDF Score:")
    for i, (feature, score) in enumerate(top_features.items(), 1):
        print(f"  {i:2d}. {feature:30s} {score:.6f}")
    
    print("="*60 + "\n")
    
    return df, tfidf_matrix


if __name__ == "__main__":
    # Default paths
    input_file = "data/processed/clean_data.csv"
    output_directory = "data/processed/features"
    
    # Generate features
    df_meta, tfidf_mat = generate_features(input_file, output_directory)
    
    logger.info("Feature engineering completed successfully")
