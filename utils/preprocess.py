# utils/preprocess.py

import re
import json

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    return texto.lower().strip()

def detectar_coluna_texto(df):
    for col in df.columns:
        if "texto" in col.lower() or "coment" in col.lower():
            return col
    return df.columns[0]

def carregar_glossario(path="glossario/Glossario_BR-ECHO_Classificado.json"):
    glossario = []
    with open(path, "r", encoding="utf-8") as f:
        dados = json.load(f)
        for chave, item in dados.items():
            token = item.get("token_pt") or item.get("token_original")
            if token:
                glossario.append({
                    "token": token
                })
    return glossario

def ativar_tokens(texto, glossario):
    texto = normalizar_texto(texto)
    ativados = []
    for item in glossario:
        termo = item["token"].lower()
        if re.search(rf"\b{re.escape(termo)}\b", texto):
            ativados.append(item["token"])
    return ativados


def aplicar_schema_padrao(df):
    for col in ["texto", "risk_score", "subcultura", "tokens_ativados", "score_bert", "timestamp"]:
        if col not in df.columns:
            df[col] = None
    return df
