import pandas as pd
import hashlib
import blake3
from simhash import Simhash
from datetime import datetime

# Caminhos
CAMINHO_CORPUS = "resultados/triagem_BR-ECHO_verbose_2025-06-24.csv"
CAMINHO_SAIDA = f"dados/hashes_extremistas_br_echo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

# Carrega corpus
df = pd.read_csv(CAMINHO_CORPUS)

# Exclui linhas que contenham o rótulo '0' em 'riscos_multilabel'
df = df[~df["riscos_multilabel"].astype(str).str.contains(r"\b0\b")].copy()
print(f"✅ Textos com riscos (sem '0') mantidos: {len(df)}")

# Funções de hash
def gerar_sha256(texto):
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()

def gerar_blake3(texto):
    return blake3.blake3(texto.encode('utf-8')).hexdigest()

def gerar_simhash(texto):
    return str(Simhash(texto).value)

# Geração dos hashes
df["sha256_hash"] = df["text_clean"].astype(str).apply(gerar_sha256)
df["blake3_hash"] = df["text_clean"].astype(str).apply(gerar_blake3)
df["simhash"] = df["text_clean"].astype(str).apply(gerar_simhash)

# Exporta
df[["text_clean", "risco_binario", "riscos_multilabel", "sha256_hash", "blake3_hash", "simhash"]].to_csv(CAMINHO_SAIDA, index=False)
print(f"💾 Hashes salvos com sucesso em: {CAMINHO_SAIDA}")
