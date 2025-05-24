# processing/classificador_ml.py

import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import joblib
import os

MODELO_PATH = "modelos/modelo_risco.joblib"

def treinar_modelo(csv_path="glossario/template_anotacao_br_echo.csv"):
    df = pd.read_csv(csv_path)

    # Vetor + modelo
    X = df["texto"]
    y = df["risk_score"]

    pipeline = make_pipeline(
        TfidfVectorizer(max_features=1500, ngram_range=(1, 2)),
        RandomForestClassifier(n_estimators=100, random_state=42)
    )

    pipeline.fit(X, y)
    os.makedirs("modelos", exist_ok=True)
    joblib.dump(pipeline, MODELO_PATH)
    print("✅ Modelo treinado e salvo com sucesso.")

def carregar_modelo():
    return joblib.load(MODELO_PATH)

def prever_score(texto, modelo=None):
    if modelo is None:
        modelo = carregar_modelo()
    return int(modelo.predict([texto])[0])

# Exemplo
if __name__ == "__main__":
    treinar_modelo()
    modelo = carregar_modelo()
    print(prever_score("Ela só quer saber de alfa. Eu sou um fracassado."))
