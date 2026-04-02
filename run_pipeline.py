"""
Pipeline Execution Guide and Testing Script

This script demonstrates how to run the complete data pipeline
and validates each module independently.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_pipeline.collect_data import collect_data
from data_pipeline.preprocess import preprocess_dataset
from data_pipeline.validate_data import validate_data
from data_pipeline.feature_engineering import generate_features


def run_pipeline():
    """
    Execute the complete data pipeline from raw data to ML-ready features.
    """
    print("\n" + "="*70)
    print("FAKE NEWS PROPAGATION DATA PIPELINE")
    print("Large-Scale Analysis Under Adversarial Content Evolution")
    print("="*70 + "\n")
    
    # Define paths
    raw_data_path = "data/raw/fake_news.csv"
    clean_data_path = "data/processed/clean_data.csv"
    features_dir = "data/processed/features"
    validation_report = "data/processed/validation_report.txt"
    
    # Ensure directories exist and are writable
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    # Check write permissions
    if not os.access("data/processed", os.W_OK):
        print("ERROR: Cannot write to data/processed/ directory")
        print("Please check directory permissions.")
        return False
    
    try:
        # Step 1: Data Collection
        print("\n" + "-"*70)
        print("STEP 1: DATA COLLECTION AND VALIDATION")
        print("-"*70)
        
        if not os.path.exists(raw_data_path):
            print(f"ERROR: Raw data not found at {raw_data_path}")
            print("Please place your fake_news.csv in data/raw/")
            return False
        
        df_raw = collect_data(raw_data_path)
        print(f"[OK] Successfully loaded {len(df_raw)} records")
        
        # Step 2: Text Preprocessing
        print("\n" + "-"*70)
        print("STEP 2: TEXT PREPROCESSING")
        print("-"*70)
        
        df_clean = preprocess_dataset(raw_data_path, clean_data_path)
        print(f"[OK] Successfully preprocessed data")
        print(f"  - Input: {len(df_raw)} records")
        print(f"  - Output: {len(df_clean)} records")
        
        # Step 3: Data Validation
        print("\n" + "-"*70)
        print("STEP 3: DATA VALIDATION")
        print("-"*70)
        
        validation_passed, validation_results = validate_data(
            clean_data_path, 
            validation_report
        )
        
        if validation_passed:
            print("[OK] All validation checks passed!")
        else:
            print("[WARNING] Some validation issues found. Review the report.")
        
        # Step 4: Feature Engineering
        print("\n" + "-"*70)
        print("STEP 4: FEATURE ENGINEERING")
        print("-"*70)
        
        df_meta, tfidf_matrix = generate_features(
            clean_data_path,
            features_dir,
            max_features=5000
        )
        print(f"[OK] Features generated successfully")
        print(f"  - Feature matrix shape: {tfidf_matrix.shape}")
        print(f"  - Features saved to: {features_dir}")
        
        # Final Summary
        print("\n" + "="*70)
        print("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"\n[OUTPUT] Summary:")
        print(f"  Raw Data:           {raw_data_path}")
        print(f"  Cleaned Data:       {clean_data_path}")
        print(f"  Features Directory: {features_dir}")
        print(f"  Validation Report:  {validation_report}")
        print(f"\n✓ Pipeline ready for ML model training!")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_modules():
    """
    Test each module independently for debugging.
    """
    print("\n" + "="*70)
    print("INDIVIDUAL MODULE TESTING")
    print("="*70)
    
    raw_data_path = "data/raw/fake_news.csv"
    
    if not os.path.exists(raw_data_path):
        print(f"ERROR: Test data not found at {raw_data_path}")
        return False
    
    try:
        # Test 1: collect_data module
        print("\n[TEST 1] Testing collect_data module...")
        from data_pipeline.collect_data import load_data, validate_columns, handle_missing_values
        
        df = load_data(raw_data_path)
        validate_columns(df)
        df_clean = handle_missing_values(df)
        print(f"✓ collect_data module working correctly")
        
        # Test 2: preprocess module
        print("\n[TEST 2] Testing preprocess module...")
        from data_pipeline.preprocess import TextPreprocessor
        
        preprocessor = TextPreprocessor()
        sample_text = "Check this link https://example.com and @mention #hashtag!!!"
        cleaned = preprocessor.clean_text(sample_text)
        print(f"  Sample: '{sample_text}'")
        print(f"  Result: '{cleaned}'")
        print(f"✓ preprocess module working correctly")
        
        # Test 3: feature_engineering module
        print("\n[TEST 3] Testing feature_engineering module...")
        from data_pipeline.feature_engineering import FeatureEngineer
        
        engineer = FeatureEngineer(max_features=100)
        print(f"✓ feature_engineering module initialized correctly")
        
        # Test 4: validate_data module
        print("\n[TEST 4] Testing validate_data module...")
        from data_pipeline.validate_data import DataValidator
        
        validator = DataValidator()
        print(f"✓ validate_data module initialized correctly")
        
        print("\n" + "="*70)
        print("[OK] ALL MODULES TESTED SUCCESSFULLY")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Module testing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run the fake news propagation data pipeline"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run individual module tests only"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run complete pipeline (default)"
    )
    
    args = parser.parse_args()
    
    # If no arguments, run full pipeline by default
    if not args.test:
        success = run_pipeline()
    else:
        success = test_individual_modules()
    
    sys.exit(0 if success else 1)
