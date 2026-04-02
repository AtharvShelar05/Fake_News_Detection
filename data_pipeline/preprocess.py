"""
Text Preprocessing Module for Fake News Propagation Analysis

This module provides comprehensive text cleaning and normalization
for social media content used in fake news analysis.
"""

import pandas as pd
import re
import logging
import os
from typing import Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Built-in English stopwords (replaces NLTK dependency — compatible with Python 3.14+)
_STOPWORDS: frozenset = frozenset([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
    'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
    'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
    'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
    'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're',
    've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't",
    'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't",
    'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn',
    "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren',
    "weren't", 'won', "won't", 'wouldn', "wouldn't",
])


class TextPreprocessor:
    """
    Comprehensive text preprocessing pipeline for social media content.
    """
    
    def __init__(self):
        """Initialize the preprocessor with stopwords."""
        self.stop_words = _STOPWORDS
        logger.info(f"Loaded {len(self.stop_words)} stopwords")
    
    def remove_urls(self, text: str) -> str:
        """
        Remove URLs from text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text without URLs
        """
        return re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    def remove_mentions_hashtags(self, text: str) -> str:
        """
        Remove @mentions and #hashtags.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text without mentions and hashtags
        """
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        return text
    
    def remove_special_characters(self, text: str) -> str:
        """
        Remove special characters and digits, keep only letters and spaces.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with special characters removed
        """
        # Keep only alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        return text
    
    def remove_extra_whitespace(self, text: str) -> str:
        """
        Remove extra whitespace and newlines.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with normalized whitespace
        """
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def remove_stopwords(self, text: str) -> str:
        """
        Remove English stopwords from text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text without stopwords
        """
        words = text.split()
        filtered_words = [w for w in words if w.lower() not in self.stop_words]
        return ' '.join(filtered_words)
    
    def clean_text(self, text: str) -> str:
        """
        Apply complete text cleaning pipeline.
        
        Args:
            text (str): Raw input text
            
        Returns:
            str: Cleaned text
        """
        # Handle None/NaN values
        if pd.isna(text):
            return ""
        
        text = str(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = self.remove_urls(text)
        
        # Remove mentions and hashtags
        text = self.remove_mentions_hashtags(text)
        
        # Remove special characters and digits
        text = self.remove_special_characters(text)
        
        # Remove extra whitespace
        text = self.remove_extra_whitespace(text)
        
        # Remove stopwords
        text = self.remove_stopwords(text)
        
        # Remove extra whitespace again after stopword removal
        text = self.remove_extra_whitespace(text)
        
        return text


def preprocess_dataset(input_path: str, output_path: str, text_column: str = 'text') -> pd.DataFrame:
    """
    Preprocess entire dataset.
    
    Args:
        input_path (str): Path to raw data CSV
        output_path (str): Path to save cleaned data CSV
        text_column (str): Name of text column to clean
        
    Returns:
        pd.DataFrame: Preprocessed dataframe
    """
    logger.info(f"Loading data from {input_path}")
    
    # Load data
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    df = pd.read_csv(input_path)
    logger.info(f"Loaded {len(df)} records")
    
    # Initialize preprocessor
    preprocessor = TextPreprocessor()
    
    # Apply cleaning
    logger.info(f"Preprocessing '{text_column}' column...")
    df['clean_text'] = df[text_column].apply(preprocessor.clean_text)
    
    # Log cleaning statistics
    empty_texts = (df['clean_text'] == "").sum()
    if empty_texts > 0:
        logger.warning(f"{empty_texts} texts became empty after preprocessing")
    
    # Remove rows with empty cleaned text
    df_clean = df[df['clean_text'] != ""].copy()
    removed = len(df) - len(df_clean)
    if removed > 0:
        logger.info(f"Removed {removed} rows with empty text after cleaning")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
    
    # Save cleaned data
    df_clean.to_csv(output_path, index=False)
    logger.info(f"Saved cleaned data to {output_path}")
    logger.info(f"Output contains {len(df_clean)} records")
    
    # Print statistics
    print("\n" + "="*60)
    print("TEXT PREPROCESSING STATISTICS")
    print("="*60)
    print(f"Original Records: {len(df)}")
    print(f"Cleaned Records: {len(df_clean)}")
    print(f"Records Removed: {removed}")
    
    # Text length statistics
    df_clean['clean_text_length'] = df_clean['clean_text'].str.len()
    print(f"\nCleaned Text Length Statistics:")
    print(f"  Average: {df_clean['clean_text_length'].mean():.2f} characters")
    print(f"  Min: {df_clean['clean_text_length'].min()}")
    print(f"  Max: {df_clean['clean_text_length'].max()}")
    
    # Word count statistics
    df_clean['word_count'] = df_clean['clean_text'].str.split().str.len()
    print(f"\nWord Count Statistics:")
    print(f"  Average: {df_clean['word_count'].mean():.2f} words")
    print(f"  Min: {df_clean['word_count'].min()}")
    print(f"  Max: {df_clean['word_count'].max()}")
    print("="*60 + "\n")
    
    return df_clean


if __name__ == "__main__":
    # Default paths
    input_file = "data/raw/fake_news.csv"
    output_file = "data/processed/clean_data.csv"
    
    # Run preprocessing
    df_cleaned = preprocess_dataset(input_file, output_file)
    
    # Display sample cleaned records
    print("\nSample Cleaned Records (first 5):")
    print(df_cleaned[['text', 'clean_text']].head())
