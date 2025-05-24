# processing/embeddings.py

import json
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Caminhos
JSONL_PATH = "glossario/glossario_extremista_br_echo.jsonl"
CHROMA_PATH = "db/chroma_glossario"

# Carregar o glossário
def carregar_glossario(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

# Criar base vetorial
def indexar_glossario():
    glossario = carregar_glossario(JSONL_PATH)
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=CHROMA_PATH
    ))

    collection = client.get_or_create_collection("glossario_extremista")

    textos = [f"{item['termo']}: {item['definicao']} Ex: {item['exemplo']}" for item in glossario]
    ids = [f"id_{i}" for i in range(len(glossario))]

    embeddings = model.encode(textos).tolist()

    collection.add(
        documents=textos,
        ids=ids,
        metadatas=[{"subcultura": item["subcultura"], "termo": item["termo"]} for item in glossario],
        embeddings=embeddings
    )

    client.persist()
    print("Glossário indexado com sucesso!")

if __name__ == "__main__":
    indexar_glossario()
