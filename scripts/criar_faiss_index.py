# criar_faiss_index.py

import os
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document

# Caminhos
CAMINHO_CORPUS = "dados/corpus_br_echo_v4_cleaned.csv"
CAMINHO_INDEX = "dados/faiss_index_br_echo.index"

# Verificação
if not os.path.exists(CAMINHO_CORPUS):
    raise FileNotFoundError(f"Corpus não encontrado em: {CAMINHO_CORPUS}")

# Carregando corpus
print("📥 Lendo o corpus...")
df = pd.read_csv(CAMINHO_CORPUS)
textos = df["text"].dropna().astype(str).tolist()
print(f"📊 Total de textos válidos: {len(textos)}")

# Convertendo para objetos Document
documentos = [Document(page_content=texto) for texto in textos]

# Gerando embeddings
print("🔢 Gerando embeddings com BERTimbau...")
embeddings = HuggingFaceEmbeddings(model_name="neuralmind/bert-base-portuguese-cased")

# Criando índice FAISS
print("⚙️ Criando índice FAISS...")
faiss_index = FAISS.from_documents(documentos, embeddings)

# Salvando índice FAISS
print(f"💾 Salvando índice em: {CAMINHO_INDEX}")
faiss_index.save_local(CAMINHO_INDEX)

print("✅ Índice FAISS criado com sucesso!")
