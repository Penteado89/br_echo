import json
import os
import csv
import re

GLOSSARIO_PATH = "glossario/Glossario_BR-ECHO_Classificado.json"
RELATORIO_ERROS_PATH = "glossario/relatorio_erros.csv"

CAMPOS_OBRIGATORIOS = [
    "token_pt", "token_original", "regex_pt", "regex_en",
    "id_topico", "tipo_termo", "definicao_pt", "filiacao_ideologica"
]

def carregar_glossario(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validar_regex(regex):
    try:
        re.compile(regex)
        return True
    except re.error:
        return False

def detectar_erros(glossario):
    erros = []
    tokens_vistos = set()

    for chave, item in glossario.items():
        linha_erros = []

        for campo in CAMPOS_OBRIGATORIOS:
            if campo not in item or not str(item[campo]).strip():
                linha_erros.append(f"{campo} ausente ou vazio")

        token = item.get("token_pt")
        if token in tokens_vistos:
            linha_erros.append("Token duplicado")
        tokens_vistos.add(token)

        if "regex_pt" in item and not validar_regex(item["regex_pt"]):
            linha_erros.append("Regex PT inválido")

        if "regex_en" in item and not validar_regex(item["regex_en"]):
            linha_erros.append("Regex EN inválido")

        if linha_erros:
            erros.append({
                "chave": chave,
                "token_pt": item.get("token_pt", ""),
                "tipo_termo": item.get("tipo_termo", ""),
                "erros": "; ".join(linha_erros)
            })

    return erros

def salvar_csv(erros, path):
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["chave", "token_pt", "tipo_termo", "erros"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for erro in erros:
            writer.writerow(erro)

if __name__ == "__main__":
    print("🔍 Iniciando exportação de relatório de erros do glossário...")
    glossario = carregar_glossario(GLOSSARIO_PATH)
    erros = detectar_erros(glossario)
    if erros:
        salvar_csv(erros, RELATORIO_ERROS_PATH)
        print(f"⚠️ {len(erros)} erros encontrados. Relatório salvo em: {RELATORIO_ERROS_PATH}")
    else:
        print("✅ Nenhum erro encontrado no glossário.")
