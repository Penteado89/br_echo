import os
import pandas as pd
import torch
import json
from datetime import datetime
from transformers import BertTokenizerFast, BertForSequenceClassification
from tqdm import tqdm
import re

# Caminhos dos modelos e arquivos
MODEL_BIN_PATH = "modelos/bertimbau_classificador"
MODEL_MULTI_PATH = "modelos/multilabel"
INPUT_FILE = "dados/paneleiro_clean.csv"
GLOSSARIO_PATH = "glossario/Glossario_BR-ECHO_Classificado.json"

# Configurações
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
LABELS = [
    "0 - Não Extremista",
    "1 - Glorificação da Violência",
    "2 - Incitação ao Extremismo",
    "3 - Material Instrucional",
    "4 - Ameaça Iminente"
]

print(f"🖥️ Dispositivo de inferência: {DEVICE}\n")

# 🔄 Carregamento dos modelos
print("🔄 Carregando modelos e tokenizers...")
tokenizer_bin = BertTokenizerFast.from_pretrained(MODEL_BIN_PATH)
model_bin = BertForSequenceClassification.from_pretrained(MODEL_BIN_PATH)
model_bin.to(DEVICE).eval()
print("✅ Modelo binário carregado.")

tokenizer_multi = BertTokenizerFast.from_pretrained(MODEL_MULTI_PATH)
model_multi = BertForSequenceClassification.from_pretrained(MODEL_MULTI_PATH, problem_type="multi_label_classification")
model_multi.to(DEVICE).eval()
print("✅ Modelo multilabel carregado.")

# 🔍 Carregamento do glossário
def carregar_glossario(path):
    with open(path, "r", encoding="utf-8") as f:
        dados = json.load(f)
    tokens = [item["token_pt"].lower() for item in dados.values() if item.get("token_pt")]
    return tokens

glossario = carregar_glossario(GLOSSARIO_PATH)
print(f"📘 Glossário carregado com {len(glossario)} termos.\n")

# 📘 Função de ativação de tokens do glossário
def ativar_tokens(texto, glossario):
    texto = texto.lower().strip()
    ativados = []
    for token in glossario:
        if re.search(rf"\b{re.escape(token)}\b", texto):
            ativados.append(token)
    return ativados

# 🔎 Funções de inferência
def prever_binario_verbose(texto, idx=None):
    if idx is not None:
        print(f"\n📄 [Binário] Exemplo {idx+1}")
    print(f"🔍 Texto: {texto[:100]}...")

    inputs = tokenizer_bin(
        texto,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    ).to(DEVICE)

    with torch.no_grad():
        outputs = model_bin(**inputs)

    logits = outputs.logits
    pred = torch.argmax(logits, dim=1).item()
    print(f"🎯 Predição binária: {pred}")
    return int(pred)

def prever_multilabel_verbose(texto, idx=None, threshold=0.5):
    if idx is not None:
        print(f"\n📄 [Multilabel] Exemplo {idx+1}")
    print(f"🔍 Texto: {texto[:100]}...")

    inputs = tokenizer_multi(
        texto,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    ).to(DEVICE)

    with torch.no_grad():
        outputs = model_multi(**inputs)

    probs = torch.sigmoid(outputs.logits).cpu().numpy()[0]
    categorias = [LABELS[i] for i, p in enumerate(probs) if p >= threshold]
    print(f"📈 Probabilidades: {probs}")
    print(f"✅ Categorias atribuídas: {categorias if categorias else ['0 - Não Extremista']}")
    return categorias if categorias else ["0 - Não Extremista"]

def verificar_glossario(texto):
    texto = texto.lower()
    encontrados = [token for token in glossario if re.search(rf"\b{re.escape(token)}\b", texto)]
    return encontrados

# 📂 Carregamento da base
print(f"📂 Lendo base de dados: {INPUT_FILE}")
df = pd.read_csv(INPUT_FILE)
if "text_clean" not in df.columns:
    raise ValueError("❌ A coluna 'text_clean' não foi encontrada!")

df["text_clean"] = df["text_clean"].fillna("").astype(str)
print(f"📊 Total de linhas: {len(df)} — Textos únicos: {df['text_clean'].nunique()}\n")

# 🔁 Aplicando os modelos e o glossário
tqdm.pandas()
df["risco_binario"] = [
    prever_binario_verbose(texto, idx)
    for idx, texto in tqdm(enumerate(df["text_clean"]), total=len(df), desc="🔍 Binário")
]

df["riscos_multilabel"] = [
    prever_multilabel_verbose(texto, idx)
    for idx, texto in tqdm(enumerate(df["text_clean"]), total=len(df), desc="🔍 Multilabel")
]

df["tokens_ativados"] = df["text_clean"].progress_apply(verificar_glossario)

# 💾 Salvando resultados
os.makedirs("resultados", exist_ok=True)
data_str = datetime.now().strftime("%Y-%m-%d")
output_path = f"resultados/triagem_BR-ECHO_verbose_{data_str}.csv"
df.to_csv(output_path, index=False)

print(f"\n✅ Arquivo final salvo em: {output_path}")
