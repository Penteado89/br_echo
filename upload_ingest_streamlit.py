import streamlit as st
import pandas as pd
import json
import re
from utils.db import salvar_triagem
from datetime import datetime

def upload_csv_para_ingestao(glossario_path="glossario/glossario_br_echo_expanded.jsonl"):
    st.subheader("📥 Importar novo dataset anotado")
    st.markdown("Envie um `.csv` com os campos `texto`, `risk_score`, `subcultura`, etc.")

    uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success(f"{len(df)} registros carregados.")

        # Carrega glossário
        glossario = []
        with open(glossario_path, "r", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                glossario.append({
                    "token": item["token"],
                    "aliases": item.get("aliases", [])
                })

        # Função para ativar tokens
        def ativar_tokens(texto):
            texto = str(texto).lower()
            ativados = []
            for item in glossario:
                termos = [item["token"]] + item["aliases"]
                termos = [t.lower() for t in termos]
                for termo in termos:
                    if re.search(rf"\b{re.escape(termo)}\b", texto):
                        ativados.append(item["token"])
                        break
            return ativados

        with st.spinner("Processando tokens ativados..."):
            df["tokens_ativados"] = df["texto"].apply(ativar_tokens)

        st.dataframe(df.head())

        # Salva no banco de dados
        with st.spinner("Salvando no banco de dados..."):
            for _, row in df.iterrows():
                texto = row["texto"]
                score_regras = row.get("risk_score", 0)
                score_bert = row.get("risk_score", 0)  # opcionalmente duplicado
                explicacao = f"Tokens ativados: {', '.join(row['tokens_ativados'])}"
                salvar_triagem(texto, score_regras, score_bert, explicacao, data=datetime.now())

        st.success("Todos os registros foram processados e salvos com sucesso!")

        # Exportar CSV
        csv_result = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar dataset processado", data=csv_result, file_name="br_echo_processado.csv", mime="text/csv")