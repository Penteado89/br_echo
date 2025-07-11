# utils/modelos.py

import joblib
import pandas as pd

# Carregar modelos
modelo_binario = joblib.load("modelos/modelo_binario.pkl")
modelo_multiclasse = joblib.load("modelos/modelo_multiclasse.pkl")

def classificar_binario(textos):
    return modelo_binario.predict(textos)

def classificar_multiclasse(textos):
    return modelo_multiclasse.predict(textos)

def aplicar_modelos(df, coluna_texto):
    textos = df[coluna_texto].fillna("").astype(str).tolist()
    df["classe_binaria"] = classificar_binario(textos)
    df["classe_multiclasse"] = classificar_multiclasse(textos)
    return df
