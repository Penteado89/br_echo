
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from api.explain_risk import explicar_risco_com_ollama
from scripts.classificador_regras import classificar_por_regras
from processing.predict_bert import carregar_modelo_bert, prever_com_bert
from utils.pdf_export import gerar_pdf
from utils.db import inicializar_db, salvar_triagem, listar_triagens
from web.upload_ingest_streamlit import upload_csv_para_ingestao


# Inicializa o banco de dados
inicializar_db()

st.set_page_config(page_title="BR-ECHO RAG", layout="wide")
st.title("🧠 BR-ECHO – Triagem Linguística de Risco com RAG + LLM")

# Menu lateral
aba = st.sidebar.radio("📂 Menu", ["🔍 Análise de um texto", "📁 Triagem em lote", "📤 Importar novo dataset", "📜 Histórico de triagens"])

# Carrega o modelo BERT
tokenizer_bert, modelo_bert = carregar_modelo_bert()

# 🔍 Modo de texto único
if aba == "🔍 Análise de um texto":
    texto = st.text_area("Insira o texto suspeito:", height=200)
    modelo_llm = st.selectbox("Modelo de LLM (Ollama) para explicação:", ["llama2", "mistral", "gemma"])

    if st.button("Analisar"):
        if not texto.strip():
            st.warning("Por favor, insira um texto.")
        else:
            with st.spinner("Analisando..."):

                score_regras, ativadas = classificar_por_regras(texto)
                score_bert = prever_com_bert(texto, tokenizer_bert, modelo_bert)
                explicacao = explicar_risco_com_ollama(texto, modelo=modelo_llm)

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🚨 Score por regras linguísticas:")
                    st.markdown(f"**{score_regras} / 5**")
                    if ativadas:
                        for r in ativadas:
                            st.markdown(f"- **{r['nome']}** (*{r['subcultura']}*) – {r['comentario']}")
                with col2:
                    st.subheader("🤖 Score por modelo BERT fine-tuned:")
                    st.markdown(f"**{score_bert} / 5**")
                    fig, ax = plt.subplots()
                    ax.bar(["Regras", "BERT"], [score_regras, score_bert])
                    ax.set_ylim(0, 5)
                    st.pyplot(fig)

                st.subheader("🧠 Explicação gerada com RAG + LLM:")
                st.markdown(f"```markdown\n{explicacao}\n```")

                salvar_triagem(texto, score_regras, score_bert, explicacao)
                path_pdf = gerar_pdf(texto, score_regras, score_bert, explicacao)
                with open(path_pdf, "rb") as f:
                    st.download_button("📄 Baixar relatório em PDF", data=f, file_name="relatorio_br_echo.pdf", mime="application/pdf")

# 📁 Modo de batch
elif aba == "📁 Triagem em lote":
    st.markdown("Envie um arquivo CSV com uma coluna chamada `texto`.")
    arquivo = st.file_uploader("Upload do CSV", type=["csv"])
    if arquivo:
        df = pd.read_csv(arquivo)
        if "texto" not in df.columns:
            st.error("❌ O arquivo deve conter uma coluna chamada `texto`.")
        else:
            resultados = []
            with st.spinner("Processando textos..."):
                for idx, row in df.iterrows():
                    texto = str(row["texto"])
                    score_regras, _ = classificar_por_regras(texto)
                    score_bert = prever_com_bert(texto, tokenizer_bert, modelo_bert)
                    resultados.append({
                        "texto": texto,
                        "score_regras": score_regras,
                        "score_bert": score_bert
                    })
            df_resultado = pd.DataFrame(resultados)
            st.subheader("📊 Resultados da Triagem:")
            st.dataframe(df_resultado)
            fig, ax = plt.subplots()
            df_resultado[["score_regras", "score_bert"]].plot(kind="hist", bins=6, alpha=0.7, ax=ax)
            plt.xlabel("Score de Risco")
            plt.ylabel("Frequência")
            st.pyplot(fig)
            csv_result = df_resultado.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar resultados CSV", data=csv_result, file_name="br-echo_resultados.csv", mime="text/csv")

# 📜 Histórico
elif aba == "📜 Histórico de triagens":
    st.subheader("📜 Histórico de análises anteriores")
    dados = listar_triagens()
    if not dados:
        st.info("Nenhuma triagem foi registrada ainda.")
    else:
        df_hist = pd.DataFrame(dados, columns=["ID", "Texto", "Score Regras", "Score BERT", "Explicação", "Data"])
        df_hist["Data"] = pd.to_datetime(df_hist["Data"])

        col1, col2 = st.columns(2)
        with col1:
            score_min = st.slider("🔍 Filtrar por score mínimo", 0, 5, 0)
        with col2:
            data_ini = st.date_input("📅 A partir de:", df_hist["Data"].min().date())

        termo = st.text_input("🔎 Buscar por palavra-chave no texto:")
        df_filtrado = df_hist[df_hist["Score Regras"] >= score_min]
        df_filtrado = df_filtrado[df_filtrado["Data"] >= pd.to_datetime(data_ini)]
        if termo:
            df_filtrado = df_filtrado[df_filtrado["Texto"].str.contains(termo, case=False)]

        st.dataframe(df_filtrado[["Texto", "Score Regras", "Score BERT", "Data"]], height=400)

        for idx, row in df_filtrado.iterrows():
            if st.button(f"↻ Reprocessar explicação (ID {row['ID']})", key=f"reprocessar_{row['ID']}"):
                nova_exp = explicar_risco_com_ollama(row["Texto"], modelo="llama2")
                st.success("Nova explicação gerada:")
                st.markdown(f"```markdown\n{nova_exp}\n```")

        csv_hist = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar histórico filtrado CSV", data=csv_hist, file_name="historico_filtrado.csv", mime="text/csv")

# 📤 Importação de novo dataset com anotação automatizada
elif aba == "📤 Importar novo dataset":
    upload_csv_para_ingestao()

