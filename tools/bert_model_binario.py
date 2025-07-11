# bert_model_binario.py

import torch
from transformers import BertTokenizer, BertForSequenceClassification
import pandas as pd
import os

# Caminho para o modelo salvo
MODELO_PATH = "modelos/bertimbau_classificador/"

# Carregar tokenizer e modelo
tokenizer = BertTokenizer.from_pretrained(MODELO_PATH)
model = BertForSequenceClassification.from_pretrained(MODELO_PATH)
model.eval()

def classificar_texto(texto):
    """Classifica um único texto usando o modelo binário."""
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        score = probs[0][1].item()  # Probabilidade da classe 'positiva'
    return score

def classificar_dataframe(df, coluna_texto="texto"):
    """Classifica uma coluna de um DataFrame e retorna com coluna 'score_bert'."""
    df["score_bert"] = df[coluna_texto].apply(classificar_texto)
    return df
