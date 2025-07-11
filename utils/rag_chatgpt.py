import os
import pandas as pd
from dotenv import load_dotenv

# ✅ LangChain - versões atualizadas
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document

# === Carregar variáveis de ambiente ===
print("🔧 Carregando variáveis de ambiente do .env...")
load_dotenv()

# === Caminhos ===
CAMINHO_TEXTOS = "dados/corpus_br_echo_v4_cleaned.csv"
CAMINHO_INDEX = "dados/faiss_index_br_echo.index"

# === Carregar corpus base (para fallback, revisão manual ou debug) ===
print(f"📂 Lendo corpus: {CAMINHO_TEXTOS}")
df = pd.read_csv(CAMINHO_TEXTOS)
print(f"✅ Total de entradas carregadas: {len(df)}")

if "text" not in df.columns:
    raise ValueError("❌ A coluna 'text' não foi encontrada no CSV.")

textos = df["text"].dropna().astype(str).tolist()
print(f"📝 Textos válidos para indexação: {len(textos)}")

# === Carregar Embeddings ===
print("📐 Carregando embeddings com 'BERTimbau' (neuralmind/bert-base-portuguese-cased)...")
embeddings = HuggingFaceEmbeddings(model_name="neuralmind/bert-base-portuguese-cased")

# === Carregar índice FAISS ===
if os.path.exists(CAMINHO_INDEX):
    print(f"📦 Carregando índice FAISS existente: {CAMINHO_INDEX}")
    vectorstore = FAISS.load_local(CAMINHO_INDEX, embeddings, allow_dangerous_deserialization=True)
else:
    raise FileNotFoundError("🚧 Arquivo de índice FAISS não encontrado. Abortando execução.")

# === Carregar LLM ===
print("🤖 Carregando modelo da OpenAI (gpt-3.5-turbo)...")
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# === Pipeline RAG ===
print("🔗 Construindo pipeline RAG com LangChain...")
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    chain_type="stuff"
)

# === Função exportável ===
def consultar_rag(pergunta: str) -> str:
    resposta = rag_chain.run(pergunta)
    return resposta

# === Execução interativa local ===
if __name__ == "__main__":
    print("\n🚀 Pronto! Você pode começar a fazer perguntas ao sistema com base no corpus BR-ECHO.")
    while True:
        pergunta = input("\n❓ Digite sua pergunta (ou 'sair' para encerrar): ")
        if pergunta.strip().lower() == "sair":
            print("🛑 Encerrando o sistema.")
            break

        print(f"🔎 Processando pergunta: {pergunta}")
        resposta = consultar_rag(pergunta)
        print("\n📘 Resposta baseada no corpus + LLM:")
        print("-" * 50)
        print(resposta)
        print("-" * 50)
