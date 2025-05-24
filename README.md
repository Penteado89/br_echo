# BR-ECHO
**Brazilian Extremism Content Hashing Observatory**

Este projeto visa construir um observatório linguístico-comportamental e um banco de hashes para rastrear, classificar e analisar conteúdo extremista em português brasileiro.

---

## 🧠 Funcionalidades principais

- 🌐 Painel interativo com Streamlit
- 🔎 Classificação de risco linguístico por:
  - Regras linguísticas
  - Modelo supervisionado (BERT fine-tuned com discurso de ódio)
- 🧠 Explicações automáticas via RAG + LLM (Ollama)
- 📄 Geração de relatórios em PDF
- 🗃️ Histórico completo salvo via SQLite
- 📂 Triagem em lote de textos via CSV
- 🔍 Filtros por data, score e palavra-chave
- 🔁 Reprocessamento de explicações com LLM

---

## ⚙️ Tecnologias utilizadas

- Python
- Streamlit + FastAPI
- SQLite + MongoDB
- Whisper + Tesseract OCR
- OpenAI Whisper
- ImageHash (pHash)
- SimHash
- TLSH (opcional)
- Transformers (BERTimbau, Mistral, etc.)
- Ollama (LLM local)

---

## 🚀 Como executar localmente

1. Clone o repositório:

```bash
git clone https://github.com/seuusuario/br-echo.git
cd br-echo
```

2. (Opcional) Crie e ative um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Inicie o painel BR-ECHO:

```bash
chmod +x deploy_br_echo.sh
./deploy_br_echo.sh
```

---

## 📁 Estrutura do projeto

```
br-echo/
├── api/                      # FastAPI endpoints (em desenvolvimento)
├── processing/               # Classificadores, embeddings, pré-processamento
├── utils/                    # Geração de PDF e banco SQLite
├── web/                      # Painel Streamlit principal
├── modelos/                  # Modelos fine-tuned salvos
├── glossario/                # Dados linguísticos e anotações
├── relatorios/               # Relatórios PDF gerados
├── deploy_br_echo.sh         # Script de inicialização
├── requirements.txt
└── README.md
```

---

## ✨ Contribuição

Pull requests são bem-vindos! Este projeto é parte de uma pesquisa acadêmica em linguística computacional, radicalização online e inteligência artificial.

---

## 📚 Licença

Este projeto está licenciado sob os termos da Licença MIT.