# Dockerfile

FROM python:3.10-slim

# Instala dependências básicas
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    ffmpeg \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Diretório da aplicação
WORKDIR /app

# Copia os arquivos
COPY . .

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Comando padrão
CMD ["streamlit", "run", "web/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]