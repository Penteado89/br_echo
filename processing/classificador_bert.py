# processing/classificador_bert.py

import pandas as pd
import torch
from torch.utils.data import DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split

MODEL_PATH = "pierreguillou/bert-base-cased-pt"

def treinar_modelo_transformer(csv_path="glossario/template_anotacao_br_echo.csv", salvar_em="modelos/bert_risco"):
    df = pd.read_csv(csv_path)
    df = df[df["risk_score"].notnull()]

    texts = df["texto"].tolist()
    labels = df["risk_score"].tolist()

    tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)

    # Tokenização
    encodings = tokenizer(texts, truncation=True, padding=True, return_tensors="pt")
    dataset = torch.utils.data.TensorDataset(encodings["input_ids"], encodings["attention_mask"], torch.tensor(labels))

    # Split
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    # Modelo
    model = BertForSequenceClassification.from_pretrained(MODEL_PATH, num_labels=6)  # risco 0–5

    # Treinamento
    training_args = TrainingArguments(
        output_dir=salvar_em,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        evaluation_strategy="epoch",
        num_train_epochs=4,
        save_strategy="epoch",
        logging_dir=f"{salvar_em}/logs",
        load_best_model_at_end=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset
    )

    trainer.train()
    model.save_pretrained(salvar_em)
    tokenizer.save_pretrained(salvar_em)

# Exemplo
if __name__ == "__main__":
    treinar_modelo_transformer()
