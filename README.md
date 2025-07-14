
# 🔍 BR-ECHO: Brazilian Extremist Content Hashing Observatory

O **BR-ECHO** é uma aplicação de monitoramento e classificação de conteúdo extremista em língua portuguesa. Através de uma interface interativa em [Streamlit](https://streamlit.io/), integra múltiplos componentes de NLP, classificação de risco, geração de hashes e justificativas semânticas com RAG (Retrieval-Augmented Generation).

> Última atualização: 2025-07-11

---

## 🚀 Funcionalidades Principais

### 📂 1. Classificação em Lote via CSV
- Upload de arquivos `.csv` contendo uma coluna `texto`
- Classificação automática usando API local (`/classificar_lote`)
- Geração de labels binários, multilabels e tokens ativados
- Download dos resultados em CSV

### 🔍 2. Revisão Manual + Justificativa RAG
- Permite gerar justificativas semânticas automáticas via RAG
- Interface interativa para aprovar/reprovar justificativas
- Exportação das justificativas para CSV

### 🔐 3. Geração de Hashes e Armazenamento
- Geração de múltiplos tipos de hash (SHA256, BLAKE3, SimHash, MD5, SSDEEP)
- Armazenamento dos resultados em banco MongoDB
- Controle de envio manual com checkboxes

### 📚 4. Glossário BR-ECHO
- Glossário anotado de termos extremistas com filtros por ideologia, tipo e regex
- Visualização expandida e download do glossário filtrado

### 📦 5. Banco de Dados de Hashes
- Consulta interativa ao MongoDB com filtros por tipo e busca textual
- Exibição dos textos associados e hashes gerados
- Download da tabela filtrada

---

## 📦 Instalação

```bash
# Clonar o repositório
git clone https://github.com/Penteado89/br_echo.git
cd br_echo

# Criar e ativar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows

# Instalar dependências
pip install -r requirements.txt
```

---

## ▶️ Executar a Aplicação

```bash
# Rodar a API:
uvicorn main:app --reload
```

```bash
# Inicializar a aplicação Streamlit
streamlit run web/streamlit_app.py
```

---

## 🧠 Sobre o Projeto

Este projeto faz parte de uma pesquisa de doutorado em Linguística Linguística (Processamento Computacional de Linguagem Natural) aplicada à detecção de conteúdo extremista em língua portuguesa. O sistema visa oferecer uma plataforma de triagem, anotação e armazenamento de risco linguístico, com foco em transparência e reprodutibilidade.

---
## ✍️ Autor

Projeto desenvolvido por [**Ricardo Cabral Penteado**](https://www.linkedin.com/in/ricardo-cabral-penteado-45144b19/)  
Doutorando em Linguística (Processamento Computacional de Linguagem Natural) — Universidade de São Paulo (USP)

---

## 📄 Licença

MIT License
