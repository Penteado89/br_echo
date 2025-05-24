# BR-ECHO (Brazilian Extremism Content Hashing Observatory)
# Projeto base para criação de uma hash database de conteúdo extremista em português brasileiro

# === Requisitos (instalar via requirements.txt ou manualmente) ===
# pip install fastapi uvicorn pymongo pillow pytesseract imagehash simhash whisper ffmpeg-python opencv-python PyMuPDF

import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File
from bson.objectid import ObjectId
from pymongo import MongoClient
from PIL import Image
import pytesseract
import imagehash
import simhash
import whisper
import ffmpeg
import fitz  # PyMuPDF

import os
os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/5/tessdata/"

# === Configuração do MongoDB ===
client = MongoClient("mongodb://mongo:27017/")
db = client["br_echo"]
collection = db["hashes"]

# === Inicialização do modelo Whisper ===
model = whisper.load_model("base")

# === Inicialização da API ===
app = FastAPI()

# === Funções utilitárias ===

def store_hash(hash_value: str, hash_type: str, metadata: dict):
    try:
        entry = {
            "_id": str(ObjectId()),
            "hash": hash_value,
            "type": hash_type,
            "metadata": metadata,
            "created_at": datetime.utcnow()
        }
        collection.insert_one(entry)
        print(f"📝 Hash armazenado com sucesso: {hash_type} | {metadata.get('filename', '-')}" )
    except Exception as e:
        print("❌ Erro ao armazenar hash no MongoDB:", e)

def generate_image_hash(image_path):
    image = Image.open(image_path)
    return str(imagehash.phash(image))

def generate_text_hash_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='por')
    return str(simhash.Simhash(text).value), text

def generate_audio_hash(audio_path):
    result = model.transcribe(audio_path, language="pt")
    text = result["text"]
    return str(simhash.Simhash(text).value), text

def generate_video_hash(video_path):
    audio_output = video_path.replace(".mp4", ".wav")
    ffmpeg.input(video_path).output(audio_output).run(overwrite_output=True)
    return generate_audio_hash(audio_output)

def generate_pdf_hash(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = "\n".join([page.get_text() for page in doc])
    return str(simhash.Simhash(full_text).value), full_text

# === Rotas da API ===

@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_path = f"temp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        image = Image.open(file_path).convert("RGB")
        phash = str(imagehash.phash(image))

        # Tenta extrair texto via OCR
        try:
            extracted_text = pytesseract.image_to_string(image, lang='por')
        except pytesseract.TesseractError as ocr_error:
            extracted_text = ""
            print("⚠️ Erro no OCR:", ocr_error)

        # Armazena o hash perceptual da imagem
        store_hash(phash, "image_phash", {"filename": file.filename})

        # Se o OCR funcionou, armazena o simhash do texto
        if extracted_text.strip():
            simhash_text = str(simhash.Simhash(extracted_text).value)
            store_hash(simhash_text, "ocr_simhash", {
                "filename": file.filename,
                "text": extracted_text
            })
        else:
            simhash_text = None

        print("✅ Upload de imagem processado:", file.filename)
        return {
            "status": "ok",
            "image_hash": phash,
            "text_hash": simhash_text,
            "ocr": "ok" if simhash_text else "falhou"
        }

    except Exception as e:
        print("❌ Erro ao processar imagem:", file.filename, "->", e)
        return {"error": str(e)}

@app.post("/upload/audio")
async def upload_audio(file: UploadFile = File(...)):
    try:
        file_path = f"temp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        simhash_audio, transcript = generate_audio_hash(file_path)
        store_hash(simhash_audio, "audio_simhash", {"filename": file.filename, "transcript": transcript})
        return {"status": "ok", "audio_hash": simhash_audio}
    except Exception as e:
        print("❌ Erro ao processar áudio:", file.filename, "->", e)
        return {"error": str(e)}

@app.post("/upload/video")
async def upload_video(file: UploadFile = File(...)):
    try:
        file_path = f"temp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        simhash_video, transcript = generate_video_hash(file_path)
        store_hash(simhash_video, "video_simhash", {"filename": file.filename, "transcript": transcript})
        return {"status": "ok", "video_hash": simhash_video}
    except Exception as e:
        print("❌ Erro ao processar vídeo:", file.filename, "->", e)
        return {"error": str(e)}

@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        file_path = f"temp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        simhash_pdf, text = generate_pdf_hash(file_path)
        store_hash(simhash_pdf, "pdf_simhash", {"filename": file.filename, "text": text})
        return {"status": "ok", "pdf_hash": simhash_pdf}
    except Exception as e:
        print("❌ Erro ao processar PDF:", file.filename, "->", e)
        return {"error": str(e)}

# === Garante que a pasta temp/ exista ===
os.makedirs("temp", exist_ok=True)

# Para rodar localmente:
# uvicorn app.main:app --reload