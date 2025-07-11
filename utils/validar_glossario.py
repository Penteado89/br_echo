import json
import re
import os

GLOSSARIO_PATH = "glossario/Glossario_BR-ECHO_Classificado.json"

# Campos obrigatórios esperados
CAMPOS_OBRIGATORIOS = [
    "token_pt", "token_original", "regex_pt", "regex_en",
    "id_topico", "tipo_termo", "definicao_pt", "filiacao_ideologica"
]

def carregar_glossario(path):
    if not os.path.exists(path):
        print(f"❌ Arquivo não encontrado: {path}")
        return {}
    
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao ler o JSON: {e}")
            return {}

def validar_regex(codigo_regex):
    try:
        re.compile(codigo_regex)
        return True
    except re.error:
        return False

def validar_glossario(dados):
    erros = []
    tokens_vistos = set()

    for chave, item in dados.items():
        linha_erros = []

        for campo in CAMPOS_OBRIGATORIOS:
            if campo not in item or not item[campo]:
                linha_erros.append(f"Campo ausente ou vazio: {campo}")

        token = item.get("token_pt")
        if token:
            if token in tokens_vistos:
                linha_erros.append(f"Token duplicado: {token}")
            else:
                tokens_vistos.add(token)

        if "regex_pt" in item and not validar_regex(item["regex_pt"]):
            linha_erros.append("Regex inválido em regex_pt")

        if "regex_en" in item and not validar_regex(item["regex_en"]):
            linha_erros.append("Regex inválido em regex_en")

        if linha_erros:
            erros.append((chave, linha_erros))

    return erros

def imprimir_relatorio(erros):
    if not erros:
        print("✅ Glossário validado com sucesso. Nenhum erro encontrado.")
        return

    print(f"⚠️ Foram encontrados {len(erros)} problemas no glossário:\n")
    for chave, problemas in erros:
        print(f"🔸 {chave}:")
        for problema in problemas:
            print(f"   - {problema}")
    print("\n💡 Revise os campos indicados para garantir a integridade do glossário.")

if __name__ == "__main__":
    print("🔍 Iniciando validação do glossário...")
    glossario = carregar_glossario(GLOSSARIO_PATH)
    if glossario:
        erros = validar_glossario(glossario)
        imprimir_relatorio(erros)
