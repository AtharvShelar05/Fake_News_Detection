"""
Data Validation Module for Fake News Propagation Analysis

This module validates data quality, checks for null values,
validates label consistency, and logs validation status.
"""

import pandas as pd
import logging
import os
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataValidator:
    """
    Comprehensive data validation pipeline.
    """
    
    def __init__(self, required_columns: List[str] = None):
        """
        Initialize the validator.
        
        Args:
            required_columns (List[str]): List of required column names
        """
        self.required_columns = required_columns or ['text', 'label', 'user_id', 'timestamp']
        self.validation_results = {}
        logger.info(f"Initialized DataValidator with required columns: {self.required_columns}")
    
    def check_null_values(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Check for null values in the dataset.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            Tuple[bool, Dict]: Validation status and null value counts
        """
        logger.info("Checking for null values...")
        
        null_counts = df.isnull().sum()
        null_info = null_counts[null_counts > 0].to_dict()
        
        if null_info:
            logger.warning(f"Found null values: {null_info}")
            status = False
        else:
            logger.info("No null values found")
            status = True
        
        self.validation_results['null_values'] = {
            'passed': status,
            'details': null_info,
            'total_nulls': null_counts.sum()
        }
        
        return status, null_info
    
    def check_required_columns(self, df: pd.DataFrame) -> Tuple[bool, List]:
        """
        Check if all required columns exist.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            Tuple[bool, List]: Validation status and missing columns
        """
        logger.info("Checking required columns...")
        
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            status = False
        else:
            logger.info(f"All required columns present: {self.required_columns}")
            status = True
        
        self.validation_results['required_columns'] = {
            'passed': status,
            'missing': missing_cols,
            'available': list(df.columns)
        }
        
        return status, missing_cols
    
    def check_label_consistency(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Validate label column consistency.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            Tuple[bool, Dict]: Validation status and label statistics
        """
        if 'label' not in df.columns:
            logger.warning("'label' column not found. Skipping label validation.")
            self.validation_results['label_consistency'] = {
                'passed': True,
                'skipped': True,
                'reason': 'label column not found'
            }
            return True, {}
        
        logger.info("Checking label consistency...")
        
        # Check for null labels
        null_labels = df['label'].isnull().sum()
        if null_labels > 0:
            logger.warning(f"Found {null_labels} null labels")
        
        # Get unique labels and counts
        label_counts = df['label'].value_counts().to_dict()
        unique_labels = set(df['label'].dropna())
        
        logger.info(f"Unique labels: {unique_labels}")
        logger.info(f"Label distribution: {label_counts}")
        
        # Check if labels are appropriate types (not numeric when they shouldn't be)
        status = len(unique_labels) > 0 and null_labels == 0
        
        self.validation_results['label_consistency'] = {
            'passed': status,
            'unique_labels': list(unique_labels),
            'label_distribution': label_counts,
            'null_labels': int(null_labels)
        }
        
        return status, label_counts
    
    def check_data_types(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Check data types of columns.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            Tuple[bool, Dict]: Validation status and type information
        """
        logger.info("Checking data types...")
        
        dtypes_info = {
            col: str(dtype)
            for col, dtype in df.dtypes.items()
        }
        
        logger.info(f"Data types: {dtypes_info}")
        
        # Check critical columns with flexible validation
        status = True
        issues = []
        
        # Text column should be object/string (not numeric)
        if 'text' in df.columns:
            if pd.api.types.is_numeric_dtype(df['text']):
                issues.append("'text' column should not be numeric type")
                status = False
            elif not pd.api.types.is_object_dtype(df['text']):
                issues.append(f"'text' column is {df['text'].dtype}, expected object/string")
                status = False
        
        # Label can be int or string (both valid)
        if 'label' in df.columns:
            if pd.api.types.is_object_dtype(df['label']):
                logger.info("Label is string type - will be converted for ML")
            elif not pd.api.types.is_numeric_dtype(df['label']):
                issues.append(f"'label' column should be numeric or string, got {df['label'].dtype}")
                status = False
        
        self.validation_results['data_types'] = {
            'passed': status,
            'dtypes': dtypes_info,
            'issues': issues
        }
        
        return status, dtypes_info
    
    def check_text_quality(self, df: pd.DataFrame, min_length: int = 5) -> Tuple[bool, Dict]:
        """
        Check text quality and length.
        
        Args:
            df (pd.DataFrame): Input dataframe
            min_length (int): Minimum acceptable text length
            
        Returns:
            Tuple[bool, Dict]: Validation status and text quality metrics
        """
        if 'text' not in df.columns:
            logger.warning("'text' column not found. Skipping text quality check.")
            self.validation_results['text_quality'] = {
                'passed': True,
                'skipped': True
            }
            return True, {}
        
        logger.info("Checking text quality...")
        
        # Calculate text lengths
        df['text_length'] = df['text'].astype(str).str.len()
        
        # Find problematic texts
        short_texts = (df['text_length'] < min_length).sum()
        empty_texts = (df['text_length'] == 0).sum()
        
        status = (short_texts == 0) and (empty_texts == 0)
        
        if empty_texts > 0:
            logger.warning(f"Found {empty_texts} empty texts")
        if short_texts > 0:
            logger.warning(f"Found {short_texts} texts shorter than {min_length} characters")
        
        text_stats = {
            'avg_length': float(df['text_length'].mean()),
            'min_length': int(df['text_length'].min()),
            'max_length': int(df['text_length'].max()),
            'empty_texts': int(empty_texts),
            'short_texts': int(short_texts)
        }
        
        self.validation_results['text_quality'] = {
            'passed': status,
            'stats': text_stats,
            'threshold': min_length
        }
        
        return status, text_stats
    
    def check_duplicates(self, df: pd.DataFrame) -> Tuple[bool, int]:
        """
        Check for duplicate rows.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            Tuple[bool, int]: Validation status and number of duplicates
        """
        logger.info("Checking for duplicate rows...")
        
        duplicate_count = df.duplicated().sum()
        
        if duplicate_count > 0:
            logger.warning(f"Found {duplicate_count} duplicate rows")
            status = False
        else:
            logger.info("No duplicate rows found")
            status = True
        
        self.validation_results['duplicates'] = {
            'passed': status,
            'duplicate_count': int(duplicate_count)
        }
        
        return status, duplicate_count
    
    def validate_dataset(self, df: pd.DataFrame) -> Dict:
        """
        Run complete validation pipeline.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            Dict: Comprehensive validation results
        """
        logger.info("="*60)
        logger.info("Starting comprehensive data validation...")
        logger.info("="*60)
        
        # Run all validations
        self.check_required_columns(df)
        self.check_null_values(df)
        self.check_label_consistency(df)
        self.check_data_types(df)
        self.check_text_quality(df)
        self.check_duplicates(df)
        
        # Overall status
        all_passed = all(result.get('passed', True) 
                        for result in self.validation_results.values())
        
        self.validation_results['overall_status'] = {
            'passed': all_passed,
            'total_checks': len(self.validation_results) - 1
        }
        
        logger.info("="*60)
        logger.info("Validation completed")
        logger.info("="*60)
        
        return self.validation_results
    
    def generate_report(self) -> str:
        """
        Generate validation report.
        
        Returns:
            str: Formatted validation report
        """
        report = "\n" + "="*60 + "\n"
        report += "DATA VALIDATION REPORT\n"
        report += "="*60 + "\n\n"
        
        for check_name, result in self.validation_results.items():
            if check_name == 'overall_status':
                continue
            
            status_str = "[PASS]" if result.get('passed', False) else "[FAIL]"
            report += f"{check_name}: {status_str}\n"
            
            if 'details' in result and result['details']:
                report += f"  Details: {result['details']}\n"
            
            if 'stats' in result:
                for key, value in result['stats'].items():
                    report += f"  {key}: {value}\n"
            
            report += "\n"
        
        overall = self.validation_results.get('overall_status', {})
        report += "-"*60 + "\n"
        report += f"OVERALL STATUS: {'[OK] ALL CHECKS PASSED' if overall.get('passed') else '[FAIL] SOME CHECKS FAILED'}\n"
        report += "="*60 + "\n"
        
        return report


def validate_data(file_path: str, output_report: str = None) -> Tuple[bool, Dict]:
    """
    Main data validation pipeline.
    
    Args:
        file_path (str): Path to data CSV file
        output_report (str): Optional path to save validation report
        
    Returns:
        Tuple[bool, Dict]: Validation status and results
    """
    logger.info(f"Loading data from {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} records")
    
    # Initialize validator
    validator = DataValidator()
    
    # Run validation
    results = validator.validate_dataset(df)
    
    # Generate and print report
    report = validator.generate_report()
    print(report)
    
    # Save report if requested
    if output_report:
        os.makedirs(os.path.dirname(output_report), exist_ok=True)
        with open(output_report, 'w') as f:
            f.write(report)
        logger.info(f"Validation report saved to {output_report}")
    
    overall_passed = results.get('overall_status', {}).get('passed', False)
    
    return overall_passed, results


if __name__ == "__main__":
    # Default paths
    data_file = "data/processed/clean_data.csv"
    report_file = "data/processed/validation_report.txt"
    
    # Run validation
    passed, results = validate_data(data_file, report_file)
    
    if passed:
        logger.info("Data validation successful!")
    else:
        logger.warning("Data validation found issues. See report for details.")
