# Makefile - BR-ECHO

# === COMANDOS LOCAIS ===

install:
	@echo "📦 Instalando dependências..."
	pip install -r requirements.txt

train:
	@echo "🧠 Treinando modelo BERT com base nos dados anotados..."
	python processing/fine_tune_hate_speech.py

run:
	@echo "🚀 Iniciando o painel Streamlit localmente..."
	streamlit run web/streamlit_app.py

db:
	@echo "🗃️ Inicializando banco SQLite..."
	python -c "from utils.db import inicializar_db; inicializar_db()"

shell:
	@echo "🐚 Abrindo shell interativa..."
	python

# === COMANDOS COM DOCKER ===

docker-up:
	@echo "🐳 Subindo containers com Docker Compose..."
	docker-compose up --build

docker-down:
	@echo "🧹 Parando e removendo containers..."
	docker-compose down

docker-shell:
	@echo "🐚 Acessando shell do container..."
	docker exec -it br-echo-app bash