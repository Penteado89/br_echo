import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime
import requests
import time

# === Autenticação simples com token ===
TOKEN = "admin123"  # Trocar por variável de ambiente em produção

st.set_page_config(page_title="BR-ECHO Dashboard", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("\U0001F512 BR-ECHO Login")
    token = st.text_input("Digite seu token de acesso:", type="password")
    if st.button("Entrar"):
        if token == TOKEN:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Token inválido.")
    st.stop()

# === Conexão com MongoDB ===
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["br_echo"]
collection = db["hashes"]

st.sidebar.title("\U0001F39B️ Filtros de Triagem")
tipo = st.sidebar.selectbox("Tipo de conteúdo", ["Todos", "image_tlsh", "ocr_tlsh", "audio_tlsh", "video_tlsh", "pdf_tlsh"])

# === Upload de arquivos ===
st.sidebar.title("\U0001F4E4 Enviar Arquivo")
upload_type = st.sidebar.selectbox("Tipo de upload", ["Imagem", "Áudio", "Vídeo", "PDF"])
uploaded_files = st.sidebar.file_uploader("Selecione um ou mais arquivos", accept_multiple_files=True)

if uploaded_files:
    api_endpoint = {
        "Imagem": "http://localhost:8000/upload/image",
        "Áudio": "http://localhost:8000/upload/audio",
        "Vídeo": "http://localhost:8000/upload/video",
        "PDF": "http://localhost:8000/upload/pdf"
    }[upload_type]

    if st.sidebar.button("\U0001F4E4 Enviar para API"):
        progress = st.sidebar.progress(0)
        status_area = st.sidebar.empty()
        total = len(uploaded_files)
        for i, file in enumerate(uploaded_files):
            files = {"file": (file.name, file.getvalue())}
            try:
                response = requests.post(api_endpoint, files=files)
                if response.status_code == 200:
                    status_area.success(f"✅ {file.name} enviado com sucesso!")
                else:
                    status_area.error(f"❌ {file.name} falhou: {response.status_code}")
            except Exception as e:
                status_area.error(f"Erro ao conectar com a API: {e}")
            progress.progress((i + 1) / total)
            time.sleep(0.1)
        time.sleep(1)
        progress.empty()

# === Consulta ao banco ===
query = {} if tipo == "Todos" else {"type": tipo}
data = list(collection.find(query).sort("created_at", -1))

# === Função de classificação de risco simples ===
def classificar_risco(texto):
    palavras_chave = ["nazismo", "terror", "ódio", "arma", "matar", "violência", "supremacia"]
    score = sum(1 for p in palavras_chave if p.lower() in texto.lower())
    if score >= 3:
        return "\U0001F6A8 Alto"
    elif score == 2:
        return "⚠️ Médio"
    elif score == 1:
        return "🟡 Baixo"
    else:
        return "🟢 Nenhum"

# === Interface ===
st.title("\U0001F6E0️ BR-ECHO Painel de Triagem")

if data:
    registros = []
    for item in data:
        texto = item["metadata"].get("text") or item["metadata"].get("transcript") or item["metadata"].get("extracted_text") or ""
        risco = classificar_risco(texto)
        registros.append({
            "Hash": item["hash"],
            "Tipo": item["type"],
            "Arquivo": item["metadata"].get("filename", "-"),
            "Texto": texto,
            "Risco": risco,
            "Data": item["created_at"]
        })

    df = pd.DataFrame(registros)

    st.dataframe(df[["Hash", "Tipo", "Arquivo", "Risco", "Data"]], use_container_width=True)

    st.markdown("### \U0001F4C3 Ver conteúdo textual e detalhes")
    for i, row in df.iterrows():
        with st.expander(f"{row['Tipo']} | {row['Arquivo']} | {row['Data']}"):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**Hash:** `{row['Hash']}`")
                st.markdown(f"**Classificação de Risco:** {row['Risco']}")
                st.markdown(f"**Data:** `{row['Data']}`")
            with col2:
                st.text_area("Texto detectado:", row["Texto"], height=200, key=f"texto_detectado_{i}")

    st.markdown("### \U0001F4C4 Exportar resultados")
    col1, col2 = st.columns(2)
    col1.download_button("\U0001F4C3 Exportar como CSV", data=df.to_csv(index=False), file_name="br-echo-export.csv", mime="text/csv")
    col2.download_button("\U0001F4C3 Exportar como JSON", data=df.to_json(orient="records", indent=2), file_name="br-echo-export.json", mime="application/json")
else:
    st.warning("Nenhum item encontrado.")

st.markdown("---")
st.caption("Versão beta do BR-ECHO - Brazilian Extremism Content Hashing Observatory · Desenvolvido por Ricardo Cabral Penteado")
