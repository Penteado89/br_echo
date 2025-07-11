import os
import streamlit as st
import requests
import pandas as pd
from PIL import Image
import json
from pymongo import MongoClient
import pandas as pd

# 🌐 URL da API
API_URL = "http://127.0.0.1:8000"

# 🎨 Configuração da interface
st.set_page_config(page_title="BR-ECHO", layout="wide")

# 🎨 CSS customizado
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        border-radius: 6px;
        padding: 0.4em 1.2em;
        background-color: #2563eb;
        color: white;
        border: none;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Logo + título
col1, col2 = st.columns([1, 8])
with col1:
    logo = Image.open("logo_br_echo.png")
    st.image(logo, width=250)
with col2:
    st.markdown(
        "<h1 style='margin-top: 20px;'>🔍 BR-ECHO: Brazilian Extremist Content Hashing Observatory</h1>",
        unsafe_allow_html=True
    )

st.markdown("---")

# 🧭 Abas principais
tabs = st.tabs([
    "📂 Upload de CSV",
    "🔍 Revisão Manual + Justificativa RAG",
    "🔐 Geração de Hashes e Armazenamento",
    "📚 Glossário BR-ECHO",
    "📦 Banco de Dados de Hashes"
])

# === 📂 Aba 1: Upload CSV ===
with tabs[0]:
    st.subheader("📂 Classificação em lote via CSV")
    uploaded_file = st.file_uploader("Envie um arquivo CSV com uma coluna chamada 'texto'", type=["csv"])

    if uploaded_file:
        try:
            df_csv = pd.read_csv(uploaded_file)
            if "texto" not in df_csv.columns:
                st.error("❌ O arquivo deve conter uma coluna chamada 'texto'")
            else:
                textos = df_csv["texto"].dropna().astype(str).tolist()

                if st.button("Classificar CSV") or "resultados_df" in st.session_state:
                    if "resultados_df" not in st.session_state:
                        with st.spinner("🔎 Classificando textos..."):
                            response = requests.post(f"{API_URL}/classificar_lote", json={"textos": textos})
                            if response.status_code == 200:
                                resultados = response.json()
                                resultados_df = pd.DataFrame(resultados)
                                st.session_state["resultados_df"] = resultados_df
                            else:
                                st.error(f"Erro na classificação: {response.text}")
                                st.stop()

                    resultados_df = st.session_state["resultados_df"]
                    st.success("✅ Classificação disponível!")
                    st.dataframe(resultados_df[["texto", "risco_binario", "riscos_multilabel", "tokens_ativados"]])

                    st.download_button(
                        label="📥 Baixar resultados como CSV",
                        data=resultados_df.to_csv(index=False).encode("utf-8"),
                        file_name="resultados_br_echo.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.exception(f"Erro ao processar o arquivo: {e}")

# === 🔍 Aba 2: Revisão Manual com Justificativa RAG ===
with tabs[1]:
    st.subheader("🔍 Revisão Manual com Justificativa RAG")

    if "resultados_df" in st.session_state:
        df = st.session_state["resultados_df"]

        # 🔎 Filtrar apenas os textos classificados como extremistas (1 a 4)
        df_extremos = df[df["risco_binario"] > 0]

        if df_extremos.empty:
            st.info("Nenhum texto extremista foi detectado até o momento.")
        else:
            # Inicializa armazenamento de justificativas, se ainda não houver
            if "justificativas" not in st.session_state:
                st.session_state["justificativas"] = {}

            for original_idx in df_extremos.index:
                row = df.loc[original_idx]
                with st.expander(f"Texto #{original_idx}"):
                    st.write(row["texto"])

                    # Sugestão automática de pergunta
                    sugestao = f"Por que o texto a seguir foi classificado como extremista? {row['texto'][:200]}"
                    chave_entrada = f"pergunta_{original_idx}"
                    chave_btn = f"btn_rag_{original_idx}"
                    chave_check = f"aprovado_{original_idx}"

                    pergunta = st.text_input(
                        f"Digite sua pergunta ou use a sugestão para o texto #{original_idx}",
                        value=sugestao,
                        key=chave_entrada
                    )

                    if st.button(f"🔍 Gerar Justificativa #{original_idx}", key=chave_btn):
                        if not pergunta.strip():
                            st.warning("Por favor, digite uma pergunta válida.")
                        else:
                            with st.spinner("Consultando RAG..."):
                                try:
                                    response = requests.post(
                                        f"{API_URL}/justificativa_rag",
                                        json={"pergunta": pergunta.strip()}
                                    )
                                    if response.status_code == 200:
                                        result = response.json()
                                        st.session_state["justificativas"][original_idx] = {
                                            "texto": row["texto"],
                                            "pergunta": pergunta.strip(),
                                            "justificativa": result["justificativa"],
                                            "fonte": result["fonte"],
                                            "aprovado": False  # Inicialmente desmarcado
                                        }
                                        st.success("✅ Justificativa gerada com sucesso!")
                                    else:
                                        st.error(f"Erro na resposta da API: {response.text}")
                                except Exception as e:
                                    st.error(f"Erro ao consultar o servidor: {e}")

                    # Mostrar justificativa se existir
                    if original_idx in st.session_state["justificativas"]:
                        justificativa_data = st.session_state["justificativas"][original_idx]
                        st.markdown(justificativa_data["justificativa"])
                        st.caption(justificativa_data["fonte"])

                    # ✅ Checkbox de aprovação (sempre exibido, mesmo sem justificativa)
                    aprovado = st.checkbox("✅ Aprovar para geração de hashes", key=chave_check)
                    if original_idx not in st.session_state["justificativas"]:
                        st.session_state["justificativas"][original_idx] = {
                            "texto": row["texto"],
                            "pergunta": pergunta.strip(),
                            "justificativa": "",
                            "fonte": "",
                            "aprovado": aprovado
                        }
                    else:
                        st.session_state["justificativas"][original_idx]["aprovado"] = aprovado

            # 📥 Botão para exportar justificativas aprovadas (ou todas, se preferir)
            justificativas_df = pd.DataFrame.from_dict(
                st.session_state["justificativas"], orient="index"
            )
            st.download_button(
                label="📥 Baixar justificativas como CSV",
                data=justificativas_df.to_csv(index_label="indice_texto"),
                file_name="justificativas_rag_br_echo.csv",
                mime="text/csv"
            )

    else:
        st.warning("⚠️ Primeiro, envie e classifique um CSV na aba anterior.")

# === 🔐 Aba 3: Geração de Hashes e Armazenamento ===
with tabs[2]:
    st.subheader("🔐 Geração de Hashes e Armazenamento")

    if "resultados_df" in st.session_state:
        df = st.session_state["resultados_df"]

        # Usar apenas textos aprovados na aba 2
        justificativas = st.session_state.get("justificativas", {})
        aprovados_idx = [idx for idx, info in justificativas.items() if info.get("aprovado")]

        df_aprovados = df.loc[aprovados_idx].copy() if aprovados_idx else pd.DataFrame()

        if df_aprovados.empty:
            st.warning("⚠️ Nenhum conteúdo aprovado foi identificado para gerar hashes.")
        else:
            st.info(f"🔎 {len(df_aprovados)} textos aprovados para hash.")
            aprovados = []

            for i, (idx, row) in enumerate(df_aprovados.iterrows(), start=1):
                with st.expander(f"Texto #{idx}"):
                    st.markdown(row["texto"])
                    # Nova key para evitar conflito com aba 2
                    aprovar_hash = st.checkbox("✅ Confirmar envio para hashing", key=f"hash_aprovado_{idx}")
                    if aprovar_hash:
                        aprovados.append(row.to_dict())

            if len(aprovados) == 0:
                st.warning("⚠️ Nenhum texto confirmado. Selecione ao menos um para gerar hashes.")
            else:
                if st.button("🔒 Gerar Hashes e Salvar no Banco"):
                    with st.spinner("🔐 Gerando hashes e salvando..."):
                        try:
                            response = requests.post(
                                f"{API_URL}/gerar_hashes_e_salvar",
                                json={"resultados": aprovados}
                            )
                            if response.status_code == 200:
                                st.success("✅ Hashes gerados e dados salvos com sucesso.")
                            else:
                                st.error(f"Erro ao salvar: {response.text}")
                        except Exception as e:
                            st.error(f"Erro na conexão com a API: {e}")
    else:
        st.warning("⚠️ Primeiro, envie e classifique um CSV na aba anterior.")

# === 📚 Aba 4: Visualização do Glossário ===
with tabs[3]:
    st.subheader("📚 Glossário BR-ECHO: Termos Extremistas")

    # Carregar glossário do JSON
    try:
        with open("glossario/Glossario_BR-ECHO_Classificado.json", encoding="utf-8") as f:
            glossario_dict = json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar glossário: {e}")
        st.stop()

    # Converter para DataFrame
    glossario_df = pd.DataFrame.from_dict(glossario_dict, orient="index")

    # 🔍 Filtros interativos
    with st.sidebar:
        st.markdown("### 🔍 Filtros do Glossário")

        termo_busca = st.text_input("Buscar termo ou definição:", "")
        tipo_termo = st.selectbox(
            "Filtrar por tipo de termo",
            options=["Todos"] + sorted(glossario_df["tipo_termo"].dropna().unique().tolist())
        )
        filiacao = st.selectbox(
            "Filtrar por filiação ideológica",
            options=["Todos"] + sorted(glossario_df["filiacao_ideologica"].dropna().unique().tolist())
        )

    # Aplicar filtros
    filtro = glossario_df.copy()

    if termo_busca:
        termo_lower = termo_busca.lower()
        filtro = filtro[
            filtro["token_pt"].str.lower().str.contains(termo_lower) |
            filtro["definicao_pt"].str.lower().str.contains(termo_lower, na=False)
        ]

    if tipo_termo != "Todos":
        filtro = filtro[filtro["tipo_termo"] == tipo_termo]

    if filiacao != "Todos":
        filtro = filtro[filtro["filiacao_ideologica"] == filiacao]

    # 📋 Apresentação dos resultados
    if filtro.empty:
        st.info("Nenhum termo encontrado com os critérios selecionados.")
    else:
        for idx, row in filtro.iterrows():
            with st.expander(f"🔖 {row['token_pt']} — *{row['tipo_termo']}*"):
                st.markdown(f"**📌 Definição (PT):** {row['definicao_pt']}")
                st.markdown(f"**📚 Tipo de termo:** {row['tipo_termo']}")
                st.markdown(f"**🧠 Filiação ideológica:** {row['filiacao_ideologica']}")
                st.markdown(f"**🧬 Subcultura associada:** {row.get('filiacao_subcultural', '—')}")
                st.markdown(f"**🧾 Referência:** {row.get('referencia', '—')}")

                with st.container():
                    st.markdown("#### 🔎 Regex e Definição em Inglês")
                    st.code(row.get("regex_pt", ""), language="regex")
                    st.code(row.get("regex_en", ""), language="regex")
                    st.markdown(f"**Definição (EN):** {row.get('definicao_en', '—')}")

    # 📥 Botão de download
    st.download_button(
        label="📥 Baixar glossário filtrado (CSV)",
        data=filtro.to_csv(index=False).encode("utf-8"),
        file_name="glossario_filtrado_br_echo.csv",
        mime="text/csv"
    )

# === 📦 Aba 5: Banco de Dados de Hashes ===
with tabs[4]:
    st.subheader("📦 Banco de Dados de Hashes Gerados")

    # Botão para atualizar os dados do MongoDB
    atualizar = st.button("🔄 Atualizar dados do MongoDB")

    if "df_hashes" not in st.session_state or atualizar:
        try:
            # Conectar ao MongoDB local
            client = MongoClient("mongodb://localhost:27017/")
            db = client["br_echo_hashes"]

            # Coleções a serem lidas
            colecoes = ["hashes_sha256", "hashes_blake3", "hashes_simhash", "hashes_md5", "hashes_ssdeep"]

            dados = []
            for nome_col in colecoes:
                if nome_col in db.list_collection_names():
                    col = db[nome_col]
                    for doc in col.find():
                        dados.append({
                            "texto": doc.get("texto", ""),
                            "hash": doc.get("hash", ""),
                            "tipo": doc.get("tipo", nome_col.replace("hashes_", "").upper()),
                            "timestamp": doc.get("timestamp_hash", "")
                        })

            if not dados:
                st.warning("⚠️ Nenhum hash foi encontrado nas coleções do MongoDB.")
            else:
                df_hashes = pd.DataFrame(dados)
                st.session_state["df_hashes"] = df_hashes

        except Exception as e:
            st.error(f"Erro ao conectar ou consultar o MongoDB: {e}")
            st.stop()

    if "df_hashes" in st.session_state:
        df_hashes = st.session_state["df_hashes"]

        # 🎯 Filtros laterais
        with st.sidebar:
            st.markdown("### 🎯 Filtros de Hashes")
            tipo_filtro = st.selectbox(
                "Filtrar por tipo de hash",
                options=["Todos"] + sorted(df_hashes["tipo"].unique())
            )
            busca_texto = st.text_input("🔍 Buscar por trecho do texto ou hash")

        # 🔎 Aplicar filtros
        filtro_df = df_hashes.copy()

        if tipo_filtro != "Todos":
            filtro_df = filtro_df[filtro_df["tipo"] == tipo_filtro]

        if busca_texto:
            termo = busca_texto.lower()
            filtro_df = filtro_df[
                filtro_df["texto"].str.lower().str.contains(termo) |
                filtro_df["hash"].str.lower().str.contains(termo)
            ]

        # 📋 Exibição
        if filtro_df.empty:
            st.info("Nenhum hash encontrado com os critérios selecionados.")
        else:
            for i, row in filtro_df.iterrows():
                with st.expander(f"Texto #{i} — Tipo {row['tipo']}"):
                    st.markdown(f"**Texto:** {row['texto']}")
                    st.code(f"{row['tipo']}: {row['hash']}")
                    st.caption(f"🕒 Gerado em: {row['timestamp']}")

            # 📥 Botão de download
            st.download_button(
                label="📥 Baixar tabela filtrada (CSV)",
                data=filtro_df.to_csv(index=False).encode("utf-8"),
                file_name="hashes_filtrados_br_echo.csv",
                mime="text/csv"
            )