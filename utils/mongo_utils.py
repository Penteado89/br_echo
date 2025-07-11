import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# 🔧 Carrega variáveis de ambiente
load_dotenv()

client = MongoClient("mongodb://localhost:27017/")
db = client["br_echo_hashes"]

# Coleções de hashes separadas por tipo
hash_collections = {
    "sha256": db["hashes_sha256"],
    "md5": db["hashes_md5"],
    "simhash": db["hashes_simhash"],
    "ssdeep": db["hashes_ssdeep"],
    "blake3": db["hashes_blake3"] 
}

# Coleção para anotações humanas
collection_anotacoes = db["anotacoes"]

# ✅ Função para salvar anotação manual
def salvar_anotacao(texto: str, riscos_multilabel: list, anotacao: str, validado: bool):
    entry = {
        "texto": texto,
        "riscos_multilabel": riscos_multilabel,
        "anotacao_humana": anotacao,
        "validado": validado,
        "data_validacao": datetime.utcnow()
    }
    collection_anotacoes.insert_one(entry)
    return {"status": "✅ Anotação salva com sucesso no MongoDB."}

# ✅ Função para gerar e armazenar hashes se validado
def salvar_hashes_se_validado(texto: str, sha: str, blake: str, sim: str):
    # Distribui os hashes individualmente para suas coleções
    hashes_dict = {
        "sha256": sha,
        "blake3": blake,
        "simhash": sim
    }
    return salvar_hashes_mongo(texto, hashes_dict)

# ✅ Função para verificar se um texto já foi anotado como validado
def texto_ja_validado(texto: str) -> bool:
    resultado = collection_anotacoes.find_one({
        "texto": texto,
        "validado": True
    })
    return resultado is not None

# ✅ Função genérica para salvar hashes em suas respectivas coleções
def salvar_hashes_mongo(texto: str, hashes_dict: dict):
    responses = {}
    for tipo_hash, valor_hash in hashes_dict.items():
        collection = hash_collections.get(tipo_hash)
        if collection:
            entry = {
                "_id": str(ObjectId()),
                "texto": texto,
                "hash": valor_hash,
                "tipo": tipo_hash,
                "timestamp_hash": datetime.utcnow()
            }
            collection.insert_one(entry)
            responses[tipo_hash] = valor_hash
    return {
        "status": "✅ Hashes gerados e armazenados com sucesso no MongoDB.",
        "hashes": responses
    }
