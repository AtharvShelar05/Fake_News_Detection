"""
Data Collection Module for Fake News Propagation Analysis

This module handles loading social media data from CSV files,
validating required columns, and computing basic statistics.
"""

import pandas as pd
import logging
import os
from typing import Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Required columns for the dataset
REQUIRED_COLUMNS = ['text', 'label', 'user_id', 'timestamp']


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load social media data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Loaded dataset
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If required columns are missing
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        logger.info(f"Data loaded successfully from {file_path}")
        return df
    except UnicodeDecodeError:
        logger.warning("UTF-8 encoding failed, trying latin-1...")
        try:
            df = pd.read_csv(file_path, encoding='latin-1')
            logger.info(f"Data loaded with latin-1 encoding from {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise


def validate_columns(df: pd.DataFrame) -> bool:
    """
    Validate that required columns exist in the dataset.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        bool: True if all required columns present
        
    Raises:
        ValueError: If required columns are missing
    """
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    
    if missing_cols:
        logger.warning(f"Missing columns: {missing_cols}")
        logger.info(f"Available columns: {list(df.columns)}")
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    logger.info("Column validation passed")
    return True


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values by removing rows with NaNs in critical columns.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        pd.DataFrame: Dataframe with missing values removed
    """
    initial_rows = len(df)
    
    # Remove rows with missing values in required columns
    df_clean = df.dropna(subset=REQUIRED_COLUMNS)
    
    removed_rows = initial_rows - len(df_clean)
    if removed_rows > 0:
        logger.warning(f"Removed {removed_rows} rows with missing values")
    
    logger.info(f"Remaining rows: {len(df_clean)} (from {initial_rows})")
    return df_clean


def compute_statistics(df: pd.DataFrame) -> dict:
    """
    Compute basic dataset statistics.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        dict: Dictionary containing dataset statistics
    """
    stats = {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    }
    
    # Label distribution if 'label' column exists
    if 'label' in df.columns:
        stats['label_distribution'] = df['label'].value_counts().to_dict()
    
    # Text statistics if 'text' column exists
    if 'text' in df.columns:
        df['text_length'] = df['text'].astype(str).str.len()
        stats['text_stats'] = {
            'avg_length': df['text_length'].mean(),
            'min_length': df['text_length'].min(),
            'max_length': df['text_length'].max()
        }
    
    return stats


def print_statistics(stats: dict) -> None:
    """
    Pretty print dataset statistics.
    
    Args:
        stats (dict): Statistics dictionary from compute_statistics()
    """
    print("\n" + "="*60)
    print("DATASET STATISTICS")
    print("="*60)
    print(f"Total Records: {stats['total_records']}")
    print(f"Total Columns: {stats['total_columns']}")
    print(f"Columns: {', '.join(stats['columns'])}")
    print(f"Memory Usage: {stats['memory_usage_mb']:.2f} MB")
    
    print("\nMissing Values:")
    for col, count in stats['missing_values'].items():
        if count > 0:
            print(f"  {col}: {count}")
    
    if 'label_distribution' in stats:
        print("\nLabel Distribution:")
        for label, count in stats['label_distribution'].items():
            pct = (count / stats['total_records']) * 100
            print(f"  {label}: {count} ({pct:.2f}%)")
    
    if 'text_stats' in stats:
        print("\nText Statistics:")
        print(f"  Average Length: {stats['text_stats']['avg_length']:.2f}")
        print(f"  Min Length: {stats['text_stats']['min_length']}")
        print(f"  Max Length: {stats['text_stats']['max_length']}")
    
    print("="*60 + "\n")


def collect_data(file_path: str) -> pd.DataFrame:
    """
    Main data collection pipeline.
    
    Args:
        file_path (str): Path to the raw data CSV file
        
    Returns:
        pd.DataFrame: Cleaned and validated dataset
    """
    logger.info("Starting data collection pipeline...")
    
    # Load data
    df = load_data(file_path)
    
    # Validate required columns
    validate_columns(df)
    
    # Handle missing values
    df = handle_missing_values(df)
    
    # Compute and display statistics
    stats = compute_statistics(df)
    print_statistics(stats)
    
    logger.info("Data collection pipeline completed successfully")
    return df


if __name__ == "__main__":
    # Default data path
    data_path = "data/raw/fake_news.csv"
    
    # Load and process data
    df = collect_data(data_path)
    
    # Display sample records
    print("\nSample Records (first 5):")
    print(df.head())
