import json
import os
import spacy

# Caminhos
GLOSSARIO_PATH = "glossario/Glossario_BR-ECHO_Classificado.json"
GLOSSARIO_LIMPO_PATH = "glossario/Glossario_filtrado_sem_stopwords.json"

# Carregar modelo spaCy para stopwords
print("🧠 Carregando modelo spaCy...")
try:
    nlp = spacy.load("pt_core_news_sm")
    STOPWORDS = nlp.Defaults.stop_words
    print(f"✅ Modelo carregado. Total de stopwords: {len(STOPWORDS)}\n")
except Exception as e:
    print(f"❌ Erro ao carregar modelo spaCy: {e}")
    exit(1)

def carregar_glossario(path):
    print(f"📂 Lendo glossário de: {path}")
    if not os.path.exists(path):
        print(f"❌ Arquivo não encontrado: {path}")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            dados = json.load(f)
            print(f"✅ Glossário carregado com {len(dados)} entradas\n")
            return dados
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler o JSON: {e}")
        return {}

def filtrar_stopwords_glossario(glossario):
    print("🔍 Filtrando tokens considerados stopwords...")
    tokens_stopwords = {}
    glossario_limpo = {}

    for chave, item in glossario.items():
        token = item.get("token_pt", "").strip().lower()
        palavras = token.split()

        if all(p in STOPWORDS for p in palavras):
            tokens_stopwords[chave] = item
        else:
            glossario_limpo[chave] = item

    print(f"📌 Tokens removidos por serem stopwords: {len(tokens_stopwords)}")
    print(f"✅ Tokens restantes no glossário: {len(glossario_limpo)}\n")
    return tokens_stopwords, glossario_limpo

def salvar_glossario(path, dados):
    print(f"💾 Salvando novo glossário em: {path}")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    print("✅ Glossário salvo com sucesso.\n")

def imprimir_relatorio(stopwords_detectadas):
    if not stopwords_detectadas:
        print("✅ Nenhuma stopword identificada no glossário.")
        return

    print(f"⚠️ Foram identificados {len(stopwords_detectadas)} tokens considerados stopwords:\n")
    for chave, item in stopwords_detectadas.items():
        print(f"🔸 {chave} → {item['token_pt']}")

if __name__ == "__main__":
    print("🚀 Iniciando processo de filtragem do glossário...\n")
    glossario = carregar_glossario(GLOSSARIO_PATH)

    if glossario:
        stopwords_detectadas, glossario_filtrado = filtrar_stopwords_glossario(glossario)
        imprimir_relatorio(stopwords_detectadas)
        salvar_glossario(GLOSSARIO_LIMPO_PATH, glossario_filtrado)
        print("🏁 Processo concluído com sucesso.")
    else:
        print("❌ Não foi possível continuar. Glossário vazio ou não encontrado.")
