# QUICK START GUIDE
## Fake News Propagation Data Pipeline

### 🚀 Getting Started (5 Minutes)

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Run the Complete Pipeline
```bash
python run_pipeline.py
```

The pipeline will:
- ✓ Load raw data from `data/raw/fake_news.csv`
- ✓ Clean and preprocess text
- ✓ Validate data quality
- ✓ Generate TF-IDF features
- ✓ Save outputs to `data/processed/`

#### 3. Check Outputs
All processed files are in `data/processed/`:
- `clean_data.csv` - Cleaned text data
- `features/` - ML-ready features
- `validation_report.txt` - Data quality report

---

### 📊 Pipeline Overview

```
raw data → collect → preprocess → validate → features
```

**Time:** ~10-30 seconds (100K records)
**Memory:** 500MB - 2GB (depends on dataset size)

---

### 📁 Project Structure

```
fake-news-propagation/
├── data/
│   ├── raw/                    ← Your raw CSV files
│   └── processed/              ← Pipeline outputs
├── data_pipeline/              ← Core modules
│   ├── collect_data.py
│   ├── preprocess.py
│   ├── feature_engineering.py
│   └── validate_data.py
├── run_pipeline.py            ← Execute full pipeline
├── requirements.txt           ← Dependencies
└── README.md                  ← Full documentation
```

---

### 📝 Input Data Format

Create a CSV file in `data/raw/` with these columns:

```csv
text,label,user_id,timestamp
"Sample tweet",0,user123,2024-01-15 10:30:00
"Fake news",1,user456,2024-01-15 11:45:00
```

**Columns:**
- `text` (required) - Social media content
- `label` (required) - 0=Real, 1=Fake
- `user_id` (required) - User identifier
- `timestamp` (required) - Post datetime

---

### 🔧 Running Individual Modules

Each module works independently:

```bash
# Step 1: Data Collection
python data_pipeline/collect_data.py

# Step 2: Text Preprocessing
python data_pipeline/preprocess.py

# Step 3: Data Validation
python data_pipeline/validate_data.py

# Step 4: Feature Engineering
python data_pipeline/feature_engineering.py
```

---

### 💡 Example Usage in Python

```python
# Complete pipeline
from data_pipeline.collect_data import collect_data
from data_pipeline.preprocess import preprocess_dataset
from data_pipeline.feature_engineering import generate_features
from data_pipeline.validate_data import validate_data

# Step 1: Load raw data
df = collect_data("data/raw/fake_news.csv")

# Step 2: Clean text
df_clean = preprocess_dataset(
    "data/raw/fake_news.csv",
    "data/processed/clean_data.csv"
)

# Step 3: Validate quality
passed, results = validate_data(
    "data/processed/clean_data.csv",
    "data/processed/validation_report.txt"
)

# Step 4: Generate ML features
df_meta, tfidf_matrix = generate_features(
    "data/processed/clean_data.csv",
    "data/processed/features"
)

print(f"Features shape: {tfidf_matrix.shape}")
print(f"Ready for ML training!")
```

---

### 📊 Output Files

**After running the pipeline, you'll have:**

1. **clean_data.csv** - Preprocessed data
   - Original text + cleaned text
   - ~2-5MB (100K records)

2. **features/** directory
   - `tfidf_features.npz` - Sparse feature matrix (efficient)
   - `feature_names.npy` - Feature vocabulary (5000 words)
   - `tfidf_vectorizer.pkl` - Serialized model
   - `features_metadata.csv` - Document labels

3. **validation_report.txt** - Quality assurance report

---

### ✅ Validation Checks

The pipeline automatically validates:
- ✓ No missing values
- ✓ All required columns present
- ✓ Valid label values
- ✓ Text length > 5 characters
- ✓ No duplicate rows
- ✓ Correct data types

---

### ⚡ Performance Tips

**For Large Datasets (>100K records):**

```python
# Process in batches
import pandas as pd

chunk_size = 10000
for chunk in pd.read_csv("data/raw/fake_news.csv", chunksize=chunk_size):
    # Process chunk
    processed = preprocess_dataset(chunk, ...)
```

**For Memory Optimization:**

- Use sparse matrix format (already done)
- Use NumPy compressed format (already done)
- Delete intermediate large objects

---

### 🐛 Troubleshooting

| Error | Solution |
|-------|----------|
| `FileNotFoundError: data not found` | Place `fake_news.csv` in `data/raw/` |
| `ModuleNotFoundError: sklearn` | Run `pip install -r requirements.txt` |
| `NLTK data not found` | Pipeline auto-downloads (just wait) |
| `Memory error` | Process smaller batches of data |

---

### 📚 Next Steps

After running the pipeline:

1. **Check validation report** - Ensure data quality
2. **Review cleaned data** - `open data/processed/clean_data.csv`
3. **Use features for ML** - Features ready for training
4. **Build models** - Use TF-IDF features with sklearn/xgboost

---

### 🎯 Key Features

✅ **Modular Design** - Each module independent
✅ **Type Hints** - Full Python type annotations
✅ **Error Handling** - Comprehensive error messages
✅ **Logging** - Detailed execution logs
✅ **Documentation** - Docstrings on every function
✅ **Production Ready** - Scalable, tested code

---

### 📖 Full Documentation

For detailed documentation:
- Main README: [README.md](README.md)
- Pipeline details: [data_pipeline/PIPELINE_DOCUMENTATION.md](data_pipeline/PIPELINE_DOCUMENTATION.md)

---

### 📧 Support

Issues or questions?
1. Check the full README
2. Review module docstrings
3. Check validation reports
4. Enable debug logging

---

**Last Updated:** January 28, 2026
**Version:** 1.0
