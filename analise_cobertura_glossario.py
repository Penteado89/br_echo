import pandas as pd
import json
import re
from collections import defaultdict

# Carregar dataset unificado
df = pd.read_csv("dataset_br_echo_unificado.csv")

# Carregar glossário expandido (JSONL)
glossario_tokens = []
with open("glossario_br_echo_expanded.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        entrada = json.loads(line)
        glossario_tokens.append({
            "token": entrada["token"],
            "aliases": entrada.get("aliases", []),
            "categoria": entrada.get("categoria", "indefinida")
        })

# Função para encontrar tokens com normalização (minúsculas)
def contar_tokens_normalizado(frase, glossario):
    frase_lower = frase.lower()
    tokens_encontrados = []
    for item in glossario:
        termos = [item["token"]] + item["aliases"]
        for termo in termos:
            termo_lower = termo.lower()
            if re.search(rf"\b{re.escape(termo_lower)}\b", frase_lower):
                tokens_encontrados.append(item["token"])
                break
    return tokens_encontrados

# Analisar por score
faixa_token_count = defaultdict(list)
for _, row in df.iterrows():
    frase = row["texto"]
    score = row["risk_score"]
    encontrados = contar_tokens_normalizado(frase, glossario_tokens)
    faixa_token_count[score].append(len(encontrados))

# Criar resumo
resumo = {
    "score": [],
    "n_frases": [],
    "media_tokens_encontrados": [],
    "maximo_tokens": [],
    "minimo_tokens": []
}

for score in sorted(faixa_token_count.keys()):
    counts = faixa_token_count[score]
    resumo["score"].append(score)
    resumo["n_frases"].append(len(counts))
    resumo["media_tokens_encontrados"].append(sum(counts) / len(counts))
    resumo["maximo_tokens"].append(max(counts))
    resumo["minimo_tokens"].append(min(counts))

df_resumo = pd.DataFrame(resumo)
df_resumo.to_csv("resumo_cobertura_glossario.csv", index=False)
print(df_resumo)