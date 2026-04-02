"""
Data Pipeline Module

This package contains the core data processing pipeline for the 
Fake News Propagation Analysis project.

Modules:
- collect_data: Load and validate raw data
- preprocess: Clean and normalize text
- feature_engineering: Generate ML features
- validate_data: Ensure data quality
"""

__version__ = "1.0"
__all__ = [
    'collect_data',
    'preprocess',
    'feature_engineering',
    'validate_data'
]
