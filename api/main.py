from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging
logging.basicConfig(level=logging.INFO)
from utils.mongo_utils import salvar_anotacao, salvar_hashes_se_validado, texto_ja_validado, salvar_hashes_mongo 
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Body
from typing import List, Dict, Any

from flashtext import KeywordProcessor

# Carregar variáveis de ambiente
load_dotenv()

import os
import re
import json
import hashlib
import blake3
from datetime import datetime

import torch
from simhash import Simhash
from transformers import BertTokenizerFast, BertForSequenceClassification
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import Body
from utils.rag_chatgpt import consultar_rag

# === Configurações iniciais ===
MODEL_BIN_PATH = "modelos/bertimbau_classificador"
MODEL_MULTI_PATH = "modelos/multilabel"
GLOSSARIO_PATH = "glossario/Glossario_BR-ECHO_Classificado.json"

LABELS = [
    "0 - Não Extremista",
    "1 - Glorificação da Violência",
    "2 - Incitação ao Extremismo",
    "3 - Material Instrucional",
    "4 - Ameaça Iminente"
]

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# === Inicialização de modelos ===
print("🔄 Carregando modelos...")
tokenizer_bin = BertTokenizerFast.from_pretrained(MODEL_BIN_PATH)
model_bin = BertForSequenceClassification.from_pretrained(MODEL_BIN_PATH).to(DEVICE).eval()

tokenizer_multi = BertTokenizerFast.from_pretrained(MODEL_MULTI_PATH)
model_multi = BertForSequenceClassification.from_pretrained(MODEL_MULTI_PATH)
model_multi.to(DEVICE).eval()

# === Carregar glossário ===
def carregar_glossario(path):
    with open(path, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return [item["token_pt"].lower() for item in dados.values() if item.get("token_pt")]

glossario = carregar_glossario(GLOSSARIO_PATH)

# === FastAPI init ===
app = FastAPI(title="BR-ECHO API", version="1.0")

# === Schemas ===
class PerguntaRAG(BaseModel):
    pergunta: str
class TextoEntrada(BaseModel):
    texto: str

class LoteEntrada(BaseModel):
    textos: List[str]

class ResultadoClassificacao(BaseModel):
    texto: str
    risco_binario: int
    riscos_multilabel: List[str]
    tokens_ativados: List[str]
    sha256_hash: str
    blake3_hash: str
    simhash: str

# === Funções ===
def gerar_hashes(texto: str):
    sha = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    blake = blake3.blake3(texto.encode("utf-8")).hexdigest()
    sim = str(Simhash(texto).value)
    return sha, blake, sim



# Carrega tokens no processador
keyword_processor = KeywordProcessor()
for token in glossario:
    keyword_processor.add_keyword(token)

def verificar_glossario(texto: str):
    return keyword_processor.extract_keywords(texto.lower())

def prever_binario(texto: str):
    inputs = tokenizer_bin(texto, return_tensors="pt", truncation=True, padding=True, max_length=512).to(DEVICE)
    with torch.no_grad():
        outputs = model_bin(**inputs)
    return torch.argmax(outputs.logits, dim=1).item()

def prever_multilabel(texto: str, threshold: float = 0.5):
    inputs = tokenizer_multi(texto, return_tensors="pt", truncation=True, padding=True, max_length=512).to(DEVICE)
    with torch.no_grad():
        outputs = model_multi(**inputs)
    probs = torch.sigmoid(outputs.logits).cpu().numpy()[0]
    return [LABELS[i] for i, p in enumerate(probs) if p >= threshold]


def processar_texto(texto: str) -> ResultadoClassificacao:
    texto = texto.strip()
    if not texto:
        raise HTTPException(status_code=400, detail="Texto vazio.")

    risco_binario = prever_binario(texto)
    riscos_multilabel = prever_multilabel(texto)
    tokens_ativados = verificar_glossario(texto)
    sha, blake, sim = gerar_hashes(texto)

    return ResultadoClassificacao(
        texto=texto,
        risco_binario=risco_binario,
        riscos_multilabel=riscos_multilabel,
        tokens_ativados=tokens_ativados,
        sha256_hash=sha,
        blake3_hash=blake,
        simhash=sim
    )


# === Endpoints ===
@app.post("/classificar", response_model=ResultadoClassificacao)
def classificar_texto(dados: TextoEntrada):
    return processar_texto(dados.texto)

@app.post("/classificar_lote", response_model=List[ResultadoClassificacao])
def classificar_lote(dados: LoteEntrada):
    return [processar_texto(txt) for txt in dados.textos if txt.strip()]

@app.post("/anotacao_humana")
def salvar_anotacao_endpoint(
    texto: str = Body(...),
    riscos_multilabel: List[str] = Body(...),
    anotacao: str = Body(...),
    validado: bool = Body(...)
):
    return salvar_anotacao(texto, riscos_multilabel, anotacao, validado)


@app.post("/justificativa_rag")
def gerar_justificativa_rag(dados: PerguntaRAG):
    if not dados.pergunta.strip():
        raise HTTPException(status_code=400, detail="Pergunta vazia.")
    try:
        resposta = consultar_rag(dados.pergunta)
        return {
            "pergunta": dados.pergunta,
            "justificativa": resposta,
            "fonte": "RAG + Corpus BR-ECHO"
        }
    except Exception as e:
        logging.exception("Erro ao consultar RAG:")
        return {"erro": str(e)}

@app.post("/gerar_hashes_aprovado")
def gerar_hashes_apenas_validado(texto: str = Body(...)):
    if not texto_ja_validado(texto):
        raise HTTPException(status_code=403, detail="Texto ainda não validado como extremista.")

    sha = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    blake = blake3.blake3(texto.encode("utf-8")).hexdigest()
    sim = str(Simhash(texto).value)

    return salvar_hashes_se_validado(texto, sha, blake, sim)


class TextoItem(BaseModel):
    texto: str

@app.post("/gerar_hashes_e_salvar")
def gerar_hashes_e_salvar(payload: Dict[str, Any]):
    resultados = payload.get("resultados", [])
    
    if not resultados:
        raise HTTPException(status_code=400, detail="Lista de resultados vazia.")

    total_salvos = 0

    for item in resultados:
        texto = item.get("texto")
        if not texto or not isinstance(texto, str):
            continue

        try:
            hashes = gerar_hashes(texto)
            salvar_hashes_mongo(texto, {
                "sha256": hashes[0],
                "blake3": hashes[1],
                "simhash": hashes[2]
            })
            total_salvos += 1
        except Exception as e:
            logging.error(f"[ERRO] Falha ao processar texto: {texto[:30]}... | Erro: {e}")

    return {
        "mensagem": f"✅ {total_salvos} hashes gerados e salvos com sucesso.",
        "total_processado": total_salvos
    }

@app.get("/ping")
def ping():
    return {"status": "BR-ECHO API online"}
