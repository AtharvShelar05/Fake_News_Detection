import os
import sys
import pandas as pd
import torch
import logging
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_data.csv")
SAVE_DIR = os.path.join(BASE_DIR, "ml_models", "bert_model")

class FakeNewsDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.labels)

def train():
    logger.info("Loading dataset...")
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    
    df = pd.read_csv(DATA_PATH)
    # Use clean_text if available, else fallback to text
    text_col = "clean_text" if "clean_text" in df.columns else "text"
    texts = df[text_col].fillna("").astype(str).tolist()
    labels = df["label"].tolist()

    logger.info(f"Loaded {len(texts)} samples for training.")

    logger.info("Loading tokenizer distilbert-base-uncased...")
    tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')
    
    logger.info("Tokenizing texts...")
    encodings = tokenizer(texts, truncation=True, padding=True, max_length=128)
    dataset = FakeNewsDataset(encodings, labels)

    logger.info("Loading model distilbert-base-uncased...")
    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)

    training_args = TrainingArguments(
        output_dir=os.path.join(BASE_DIR, "ml_models", "bert_results"),
        num_train_epochs=3,
        per_device_train_batch_size=8,
        logging_steps=2,
        save_strategy="no", # Don't save checkpoints, only final model
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )

    logger.info("Starting training...")
    trainer.train()

    logger.info(f"Saving model and tokenizer to {SAVE_DIR}...")
    os.makedirs(SAVE_DIR, exist_ok=True)
    model.save_pretrained(SAVE_DIR)
    tokenizer.save_pretrained(SAVE_DIR)
    
    logger.info("Training complete and model saved.")

if __name__ == "__main__":
    train()
