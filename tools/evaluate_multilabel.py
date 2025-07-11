# evaluate_multilabel.py

import torch
from transformers import BertTokenizerFast, BertForSequenceClassification
from sklearn.metrics import classification_report, roc_auc_score
import pandas as pd
import numpy as np
import os

# Caminhos
MODELO_PATH = "modelos/multilabel"
DATASET_TESTE = "dados/dataset_teste.csv"  # Adapte para seu caminho real

# Rótulos
LABELS = [
    "0 - Não Extremista",
    "1 - Glorificação da Violência",
    "2 - Incitação ao Extremismo",
    "3 - Material Instrucional",
    "4 - Ameaça Iminente"
]
NUM_LABELS = len(LABELS)

# Dispositivo
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("🚀 Iniciando avaliação do modelo multilabel...\n")

# 🔄 Carregar modelo e tokenizer
print("🔄 Carregando modelo e tokenizer...")
tokenizer = BertTokenizerFast.from_pretrained(MODELO_PATH)
model = BertForSequenceClassification.from_pretrained(MODELO_PATH, problem_type="multi_label_classification")
model.to(DEVICE)
model.eval()
print("✅ Modelo carregado com sucesso!\n")

# 🔍 Carregar dataset de teste
print(f"📂 Carregando dataset de teste: {DATASET_TESTE}")
df = pd.read_csv(DATASET_TESTE)

if "texto" not in df.columns:
    raise ValueError("⚠️ A coluna 'texto' deve estar presente no dataset de teste.")
if not all(label in df.columns for label in LABELS):
    raise ValueError("⚠️ Todas as colunas de rótulo multilabel devem estar presentes no dataset.")

print(f"✅ {len(df)} exemplos carregados.\n")

# Previsões
y_true = df[LABELS].values
y_pred_probs = []

print("🔬 Realizando inferência...")
for texto in df["texto"]:
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True).to(DEVICE)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.sigmoid(outputs.logits).cpu().numpy()[0]
    y_pred_probs.append(probs)

y_pred_probs = np.array(y_pred_probs)
y_pred_bin = (y_pred_probs >= 0.5).astype(int)

print("✅ Inferência finalizada.\n")

# 📊 Métricas
print("📈 Relatório de Classificação:\n")
print(classification_report(y_true, y_pred_bin, target_names=LABELS, zero_division=0))

# ROC-AUC por classe
try:
    roc_auc = roc_auc_score(y_true, y_pred_probs, average=None)
    for i, label in enumerate(LABELS):
        print(f"🎯 ROC-AUC para {label}: {roc_auc[i]:.4f}")
except:
    print("⚠️ ROC-AUC não pôde ser calculado. Verifique se o dataset possui exemplos positivos para cada classe.")

print("\n🏁 Avaliação finalizada.")
