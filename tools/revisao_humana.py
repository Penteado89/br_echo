import streamlit as st
import pandas as pd
import ast

# Carrega os dados de triagem
df = pd.read_csv("resultados/triagem_BR-ECHO_verbose_2025-06-24.csv")

# Converte listas de string para listas reais
if isinstance(df.loc[0, "riscos_multilabel"], str):
    df["riscos_multilabel"] = df["riscos_multilabel"].apply(ast.literal_eval)
if isinstance(df.loc[0, "tokens_ativados"], str):
    df["tokens_ativados"] = df["tokens_ativados"].apply(ast.literal_eval)

st.set_page_config(layout="wide")
st.title("🧠 Painel de Triagem BR-ECHO")

st.sidebar.header("🎯 Filtros")

# Filtros
termo = st.sidebar.text_input("🔎 Buscar termo no texto")
risk_bin = st.sidebar.selectbox("🧮 Classificação Binária", ["Todos"] + sorted(df["risco_binario"].unique().astype(str)))
risk_multi = st.sidebar.multiselect("🏷️ Rótulos Multilabel", options=sorted({r for sub in df["riscos_multilabel"] for r in sub}))
token_glossario = st.sidebar.text_input("📘 Termo do glossário")

# Aplicação dos filtros
filtro = df.copy()
if termo:
    filtro = filtro[filtro["text_clean"].str.contains(termo, case=False, na=False)]
if risk_bin != "Todos":
    filtro = filtro[filtro["risco_binario"] == int(risk_bin)]
if risk_multi:
    filtro = filtro[filtro["riscos_multilabel"].apply(lambda x: any(tag in x for tag in risk_multi))]
if token_glossario:
    filtro = filtro[filtro["tokens_ativados"].apply(lambda x: token_glossario.lower() in [t.lower() for t in x])]

st.markdown(f"### 📄 {len(filtro)} registros filtrados")

# Interface de anotação manual
for i, row in filtro.iterrows():
    with st.expander(f"🔍 Exemplo {i+1}"):
        st.markdown(f"**Texto:** {row['text_clean']}")
        st.markdown(f"**Binário:** `{row['risco_binario']}`")
        st.markdown(f"**Multilabel:** `{row['riscos_multilabel']}`")
        st.markdown(f"**Glossário:** `{row['tokens_ativados']}`")
        anotacao = st.text_input("✍️ Comentário / sugestão de correção", key=f"anotacao_{i}")
        salvar = st.checkbox("💾 Salvar anotação", key=f"salvar_{i}")
        if salvar and anotacao:
            with open("resultados/anotacoes_humanas.tsv", "a", encoding="utf-8") as f:
                f.write(f"{i}\t{row['text_clean']}\t{row['riscos_multilabel']}\t{anotacao}\n")
            st.success("✅ Anotação salva com sucesso!")
