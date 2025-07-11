#!/bin/bash

echo "🔧 Iniciando ambiente BR-ECHO..."

# Ativar venv se existir
if [ -d "venv" ]; then
    echo "⚙️ Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Inicializar banco de dados
echo "🗂️ Verificando banco de dados..."
python3 -c "from utils.db import inicializar_db; inicializar_db()"

# Rodar Streamlit
echo "🚀 Iniciando painel Streamlit..."
streamlit run web/streamlit_app.py
