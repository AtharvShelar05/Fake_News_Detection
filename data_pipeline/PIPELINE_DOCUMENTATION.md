# Data Pipeline Module Documentation

## Overview

This directory contains the core data processing modules for the Fake News Propagation Analysis project. Each module is designed to be independently executable while contributing to the overall pipeline.

## Module Structure

```
data_pipeline/
├── collect_data.py          # Data loading and collection
├── preprocess.py            # Text cleaning and normalization
├── feature_engineering.py   # Feature extraction (TF-IDF)
└── validate_data.py         # Data quality validation
```

## Module Details

### 1. `collect_data.py`

**Description:** Loads raw social media data and validates structure.

**Key Classes:**
- Functions only (modular design)

**Key Functions:**
- `load_data(file_path)` - Load CSV file
- `validate_columns(df)` - Check required columns
- `handle_missing_values(df)` - Remove rows with NaNs
- `compute_statistics(df)` - Calculate dataset stats
- `collect_data(file_path)` - Complete pipeline

**Input:** CSV file with columns: `text`, `label`, `user_id`, `timestamp`

**Output:** Validated DataFrame with statistics

**Dependencies:** pandas, logging

**Example:**
```python
from data_pipeline.collect_data import collect_data

df = collect_data("data/raw/fake_news.csv")
```

---

### 2. `preprocess.py`

**Description:** Cleans and normalizes text data.

**Key Classes:**
- `TextPreprocessor` - Main preprocessing class

**Key Methods:**
- `remove_urls(text)` - Remove hyperlinks
- `remove_mentions_hashtags(text)` - Remove @ and #
- `remove_special_characters(text)` - Keep only letters/spaces
- `remove_stopwords(text)` - Remove common words
- `clean_text(text)` - Complete pipeline

**Key Functions:**
- `preprocess_dataset(input_path, output_path)` - Process entire dataset

**Input:** CSV with raw `text` column

**Output:** CSV with `text` and `clean_text` columns

**Dependencies:** pandas, re, nltk, logging, os

**Example:**
```python
from data_pipeline.preprocess import preprocess_dataset

df_clean = preprocess_dataset(
    "data/raw/fake_news.csv",
    "data/processed/clean_data.csv"
)
```

**Text Cleaning Pipeline:**
1. Lowercase
2. URL removal
3. Mention/hashtag removal
4. Special character removal
5. Whitespace normalization
6. Stopword removal
7. Final cleanup

---

### 3. `feature_engineering.py`

**Description:** Generates TF-IDF features from cleaned text.

**Key Classes:**
- `FeatureEngineer` - TF-IDF vectorization

**Key Methods:**
- `fit_transform(texts)` - Fit vectorizer and transform texts
- `transform(texts)` - Apply fitted vectorizer
- `save_vectorizer(filepath)` - Serialize vectorizer
- `load_vectorizer(filepath)` - Load vectorizer

**Key Functions:**
- `get_top_features(tfidf_matrix, feature_names, top_n)` - Extract top features
- `generate_features(input_path, output_dir, max_features)` - Complete pipeline

**TF-IDF Configuration:**
```python
TfidfVectorizer(
    max_features=5000,
    min_df=2,
    max_df=0.95,
    ngram_range=(1, 2),
    lowercase=True,
    stop_words='english'
)
```

**Input:** CSV with `clean_text` column

**Output Files:**
- `tfidf_features.npz` - Sparse matrix
- `feature_names.npy` - Vocabulary
- `tfidf_vectorizer.pkl` - Fitted vectorizer
- `features_metadata.csv` - Document metadata

**Dependencies:** pandas, numpy, sklearn, logging, os, pickle

**Example:**
```python
from data_pipeline.feature_engineering import generate_features

df_meta, tfidf_matrix = generate_features(
    "data/processed/clean_data.csv",
    "data/processed/features",
    max_features=5000
)

# Access features
print(tfidf_matrix.shape)  # (num_docs, num_features)
```

---

### 4. `validate_data.py`

**Description:** Validates data quality throughout the pipeline.

**Key Classes:**
- `DataValidator` - Validation orchestrator

**Key Methods:**
- `check_null_values(df)` - Detect missing data
- `check_required_columns(df)` - Verify column presence
- `check_label_consistency(df)` - Validate labels
- `check_data_types(df)` - Check column types
- `check_text_quality(df, min_length)` - Verify text content
- `check_duplicates(df)` - Find duplicate rows
- `validate_dataset(df)` - Run all checks
- `generate_report()` - Create human-readable report

**Key Functions:**
- `validate_data(file_path, output_report)` - Complete validation pipeline

**Validation Checks:**
1. ✓ Null values
2. ✓ Required columns
3. ✓ Label consistency
4. ✓ Data types
5. ✓ Text quality
6. ✓ Duplicates

**Output:** Validation report with pass/fail status

**Dependencies:** pandas, logging, os

**Example:**
```python
from data_pipeline.validate_data import validate_data

passed, results = validate_data(
    "data/processed/clean_data.csv",
    "data/processed/validation_report.txt"
)

if passed:
    print("Data is ready for ML!")
```

---

## Data Flow Diagram

```
data/raw/fake_news.csv
         ↓
    [collect_data.py]
    - Load CSV
    - Validate columns
    - Handle missing values
    - Compute statistics
         ↓
    [preprocess.py]
    - Remove URLs
    - Remove mentions
    - Lowercase text
    - Remove stopwords
    - Save clean data
         ↓
data/processed/clean_data.csv
         ↓
    [validate_data.py]
    - Check nulls
    - Validate labels
    - Check duplicates
    - Generate report
         ↓
data/processed/validation_report.txt
         ↓
    [feature_engineering.py]
    - Fit TF-IDF
    - Generate features
    - Save vectorizer
    - Extract top features
         ↓
data/processed/features/
    - tfidf_features.npz
    - feature_names.npy
    - tfidf_vectorizer.pkl
    - features_metadata.csv
```

## Running Individual Modules

Each module can be run independently:

```bash
# Data collection
python data_pipeline/collect_data.py

# Text preprocessing
python data_pipeline/preprocess.py

# Data validation
python data_pipeline/validate_data.py

# Feature engineering
python data_pipeline/feature_engineering.py
```

## Running Complete Pipeline

Execute the full pipeline with orchestration:

```bash
python run_pipeline.py

# Or test individual modules
python run_pipeline.py --test
```

## Configuration

### Global Settings

Each module uses consistent configuration:
- **Encoding:** UTF-8
- **Random State:** Reproducible (no random seed currently set)
- **Error Handling:** Try-catch with logging

### Module-Specific Settings

Edit these in the source files:

**Preprocessing:**
- Stopwords: English (NLTK)
- Regex patterns: Customizable
- Minimum text length: 5 characters (validation)

**Feature Engineering:**
- Max features: 5000
- Min DF: 2
- Max DF: 0.95
- N-gram range: (1, 2)

**Validation:**
- Minimum text length: 5 characters
- Required columns: text, label, user_id, timestamp

## Error Handling

All modules include comprehensive error handling:

```python
try:
    # Operation
except FileNotFoundError:
    logger.error("File not found")
except ValueError:
    logger.error("Invalid value")
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
```

## Logging

All modules use Python's logging module:

- **Level:** INFO (can be changed)
- **Format:** timestamp - level - message
- **Output:** Console

To customize:

```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
```

## Performance Optimization

### Memory Usage
- Sparse matrix format for TF-IDF (5-10% of dense)
- Compressed NPZ format for storage
- Streaming for large datasets (not implemented)

### Speed
- Vectorized NumPy operations
- Efficient regex patterns
- Pre-compiled tokenizers

### Scalability
- Process datasets up to 1M+ records
- Parallelization ready (Dask/Spark compatible)

## Testing

### Unit Testing Template

```python
# tests/test_preprocess.py
import unittest
from data_pipeline.preprocess import TextPreprocessor

class TestPreprocessor(unittest.TestCase):
    def setUp(self):
        self.processor = TextPreprocessor()
    
    def test_remove_urls(self):
        text = "Check https://example.com for info"
        result = self.processor.remove_urls(text)
        self.assertNotIn("http", result)
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Functions

```python
# Quick test
from data_pipeline.preprocess import TextPreprocessor

processor = TextPreprocessor()
result = processor.clean_text("YOUR TEST TEXT HERE")
print(result)
```

## Integration with ML Pipeline

The output of feature engineering is ready for ML:

```python
import numpy as np
from data_pipeline.feature_engineering import generate_features

# Generate features
df_meta, tfidf_matrix = generate_features(...)

# Load for training
from sklearn.ensemble import RandomForestClassifier

X = tfidf_matrix
y = df_meta['label']

model = RandomForestClassifier()
model.fit(X, y)
```

## Future Enhancements

- [ ] Async processing
- [ ] Streaming support
- [ ] Additional languages
- [ ] Word embeddings (Word2Vec, GloVe, BERT)
- [ ] Named Entity Recognition
- [ ] Sentiment analysis
- [ ] Topic modeling
- [ ] Distributed processing

## Contributing Guidelines

When adding new modules:

1. Follow modular design
2. Add comprehensive docstrings
3. Include type hints
4. Use logging throughout
5. Add error handling
6. Create independent tests
7. Update documentation
8. Add example usage

---

**Version:** 1.0
**Last Updated:** January 28, 2026
