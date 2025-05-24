# processing/fine_tune_hate_speech.py

import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
import torch

CSV_PATH = "glossario/template_anotacao_br_echo.csv"
MODEL_ID = "jcbritobr/hate-speech-pt"
SAVE_PATH = "modelos/hatebr_risco"

def carregar_dataset(path):
    df = pd.read_csv(path)
    df = df[["texto", "risk_score"]]
    df = df[df["risk_score"].notnull()]  # Remove linhas incompletas
    return df

def preparar_dataset(df, tokenizer):
    def tokenize(ex):
        return tokenizer(ex["texto"], padding="max_length", truncation=True)

    dataset = Dataset.from_pandas(df)
    dataset = dataset.map(tokenize, batched=True)
    dataset = dataset.rename_column("risk_score", "labels")
    dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
    return dataset

def treinar():
    df = carregar_dataset(CSV_PATH)
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    train_data = preparar_dataset(train_df, tokenizer)
    val_data = preparar_dataset(val_df, tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID, num_labels=6)

    args = TrainingArguments(
        output_dir=SAVE_PATH,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        num_train_epochs=4,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        logging_dir=f"{SAVE_PATH}/logs",
        load_best_model_at_end=True
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_data,
        eval_dataset=val_data
    )

    trainer.train()
    model.save_pretrained(SAVE_PATH)
    tokenizer.save_pretrained(SAVE_PATH)
    print("✅ Modelo treinado e salvo em:", SAVE_PATH)

if __name__ == "__main__":
    treinar()
