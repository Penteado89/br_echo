import pandas as pd
import json
import re

# Caminhos
DATASET_CSV = "dataset_completo_br_echo.csv"
GLOSSARIO_JSONL = "glossario_br_echo_expanded.jsonl"

# Carrega o glossário
glossario = []
with open(GLOSSARIO_JSONL, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        glossario.append({
            "token": item["token"],
            "aliases": item.get("aliases", [])
        })

# Função para ativar tokens
def ativar_tokens(texto):
    texto = texto.lower()
    ativados = []
    for item in glossario:
        termos = [item["token"]] + item["aliases"]
        termos = [t.lower() for t in termos]
        for termo in termos:
            if re.search(rf"\b{re.escape(termo)}\b", texto):
                ativados.append(item["token"])
                break
    return ativados

# Carrega o CSV e processa
df = pd.read_csv(DATASET_CSV)
df["tokens_ativados"] = df["texto"].astype(str).apply(ativar_tokens)

# Salva nova versão
df.to_csv("dataset_br_echo_processado.csv", index=False)
print("✅ Dataset processado salvo como 'dataset_br_echo_processado.csv'")