import pandas as pd
from sklearn.metrics import classification_report
from processing.classificador_regras import classificar_por_regras
from processing.predict_bert import carregar_modelo_bert, prever_com_bert

# Caminho do dataset anotado
CSV_PATH = "glossario/template_anotacao_br_echo.csv"

print("📊 Iniciando benchmark do BR-ECHO com dados anotados...")

# Carrega dataset com coluna 'texto' e 'risk_score'
df = pd.read_csv(CSV_PATH)
df = df[df["risk_score"].notnull()]
df["risk_score"] = df["risk_score"].astype(int)

# Carrega modelo supervisionado (BERT fine-tuned)
tokenizer, modelo = carregar_modelo_bert()

# Previsões
y_true = []
y_pred_regras = []
y_pred_bert = []

for _, row in df.iterrows():
    texto = row["texto"]
    y_true.append(row["risk_score"])

    score_r, _ = classificar_por_regras(texto)
    y_pred_regras.append(score_r)

    score_b = prever_com_bert(texto, tokenizer, modelo)
    y_pred_bert.append(score_b)

# Avaliação
print("\n📋 Avaliação do classificador por regras:")
print(classification_report(y_true, y_pred_regras, digits=3))

print("\n📋 Avaliação do modelo BERT fine-tuned:")
print(classification_report(y_true, y_pred_bert, digits=3))