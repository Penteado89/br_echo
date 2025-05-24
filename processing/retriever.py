# processing/retriever.py

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Caminho onde está o banco vetorial do glossário
CHROMA_PATH = "db/chroma_glossario"

# Inicializa o modelo e o cliente Chroma
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=CHROMA_PATH
))
collection = client.get_collection("glossario_extremista")

def buscar_termos_relacionados(texto_input, k=3):
    """Recebe um texto e retorna os k termos mais próximos no glossário"""
    embedding = model.encode([texto_input]).tolist()
    resultados = collection.query(
        query_embeddings=embedding,
        n_results=k
    )
    
    explicacoes = []
    for doc, meta in zip(resultados['documents'][0], resultados['metadatas'][0]):
        explicacoes.append({
            "termo": meta["termo"],
            "subcultura": meta["subcultura"],
            "explicacao": doc
        })
    
    return explicacoes

# Exemplo de uso
if __name__ == "__main__":
    entrada = "1488 é um número que representa a luta do povo branco."
    top_resultados = buscar_termos_relacionados(entrada, k=3)
    
    for i, r in enumerate(top_resultados, start=1):
        print(f"\n🔹 Resultado {i}")
        print(f"➡️ Termo: {r['termo']}")
        print(f"📚 Subcultura: {r['subcultura']}")
        print(f"🧠 Explicação: {r['explicacao']}")
