import sys
import os
import traceback
from transformers import BertTokenizer, BertForSequenceClassification
import torch

print("🚀 Iniciando test_binario.py")
print("📦 Python version:", sys.version)

# Verifica o diretório de trabalho atual
print("📁 Diretório atual:", os.getcwd())

# Caminho para o modelo binário
MODEL_DIR = "modelos/bertimbau_classificador"

try:
    print(f"🔍 Verificando arquivos no diretório '{MODEL_DIR}':")
    print(os.listdir(MODEL_DIR))
except Exception as e:
    print("❌ Erro ao listar diretório:", e)
    sys.exit(1)

# Carregar tokenizer e modelo
try:
    print("🔄 Carregando tokenizer...")
    tokenizer = BertTokenizer.from_pretrained(MODEL_DIR)
    print("✅ Tokenizer carregado.")

    print("🔄 Carregando modelo BERT binário...")
    model = BertForSequenceClassification.from_pretrained(MODEL_DIR)
    print("✅ Modelo carregado.")
except Exception as e:
    print("❌ Erro ao carregar modelo/tokenizer:")
    traceback.print_exc()
    sys.exit(1)

# Colocar o modelo em modo de avaliação
model.eval()

# Exemplo de texto para teste
texto = "Vamos atacar os infiéis. Allahu Akbar!"
print(f"📝 Texto de entrada: {texto}")

# Tokenização
try:
    print("🧪 Tokenizando o texto...")
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True)
    print("✅ Tokenização realizada.")
except Exception as e:
    print("❌ Erro na tokenização:")
    traceback.print_exc()
    sys.exit(1)

# Predição
try:
    print("⚙️ Realizando predição...")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()

    print("🎯 Resultado da predição:", predicted_class)
except Exception as e:
    print("❌ Erro na predição:")
    traceback.print_exc()
    sys.exit(1)

print("✅ Teste finalizado com sucesso.")
