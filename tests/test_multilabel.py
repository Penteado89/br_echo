import torch
from transformers import BertTokenizerFast, BertForSequenceClassification
import pandas as pd
import numpy as np
import platform
import os

# Informações de ambiente
print("🚀 Iniciando test_multilabel.py")
print(f"📦 Python version: {platform.python_version()} — {platform.platform()}")
print(f"📁 Diretório atual: {os.getcwd()}")

# Caminho para o modelo treinado
MODELO_PATH = "modelos/multilabel"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🖥️ Dispositivo usado para inferência: {DEVICE}")

# Rótulos do modelo multilabel
LABELS = [
    "0 - Não Extremista",
    "1 - Glorificação da Violência",
    "2 - Incitação ao Extremismo",
    "3 - Material Instrucional",
    "4 - Ameaça Iminente"
]

# Carregamento do modelo
print("\n🔄 Carregando tokenizer e modelo multilabel...")
try:
    tokenizer = BertTokenizerFast.from_pretrained(MODELO_PATH)
    model = BertForSequenceClassification.from_pretrained(
        MODELO_PATH, problem_type="multi_label_classification"
    )
    model.to(DEVICE)
    model.eval()
    print("✅ Tokenizer e modelo carregados com sucesso.")
except Exception as e:
    print("❌ Erro ao carregar modelo/tokenizer:", e)
    exit()

# Exemplos de teste
exemplos = [
    "A luta deve continuar, só a força salvará nossa pátria.",
    "Você será o próximo, já sabemos onde mora.",
    "Aprenda a montar um dispositivo artesanal com essas peças simples.",
    "Glória aos irmãos que deram suas vidas na jihad contra os infiéis.",
    "A nova geração precisa acordar e resistir ao sistema corrupto.",
    "Vamos ao cinema amanhã. Está em cartaz um ótimo filme europeu."
]

# Função de predição
def prever_labels(frase, threshold=0.5):
    print(f"\n🔍 Frase: {frase}")
    inputs = tokenizer(frase, return_tensors="pt", truncation=True, padding=True).to(DEVICE)
    print("🧪 Tokenização realizada.")
    with torch.no_grad():
        outputs = model(**inputs)
        print("⚙️ Logits obtidos do modelo.")
    sigmoid = torch.nn.Sigmoid()
    probs = sigmoid(outputs.logits).cpu().numpy()[0]
    print(f"📈 Probabilidades: {probs}")
    labels_ativos = [LABELS[i] for i, prob in enumerate(probs) if prob >= threshold]
    print(f"🎯 Categorias acima do threshold ({threshold}): {labels_ativos if labels_ativos else ['0 - Não Extremista']}")
    return labels_ativos if labels_ativos else ["0 - Não Extremista"]

# Predição de todas as frases
print("\n📊 Iniciando testes com frases de exemplo:")
for i, frase in enumerate(exemplos):
    print(f"\n============================\n📄 Exemplo {i+1}")
    categorias = prever_labels(frase)
    print(f"✅ Resultado Final: {categorias}")

print("\n🏁 Teste multilabel finalizado.")
