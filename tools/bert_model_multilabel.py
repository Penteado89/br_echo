import torch
from transformers import BertTokenizer, BertForSequenceClassification

MODELO_PATH = "modelos/bert-model-multilabel"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Carregar modelo e tokenizer
tokenizer = BertTokenizer.from_pretrained(MODELO_PATH)
model = BertForSequenceClassification.from_pretrained(MODELO_PATH)
model.to(DEVICE)
model.eval()

# Labels conforme seu codebook
LABELS = {
    0: "Não extremista",
    1: "Glorificação da violência",
    2: "Incitação ao extremismo",
    3: "Material instrucional",
    4: "Ameaça iminente"
}

def classificar_multilabel(texto):
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True).to(DEVICE)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.sigmoid(logits).squeeze().cpu().numpy()
    # threshold padrão 0.5
    resultados = [(LABELS[i], float(probs[i])) for i in range(len(probs)) if probs[i] >= 0.5]
    return resultados

# Exemplo
if __name__ == "__main__":
    texto = "A Jihad é nossa missão. Preparem-se para o levante final."
    print("📥 Entrada:", texto)
    resultado = classificar_multilabel(texto)
    print("🏷️ Resultado:", resultado)