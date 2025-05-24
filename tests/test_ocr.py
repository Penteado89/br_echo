import os
from PIL import Image
import pytesseract

# Aponta explicitamente para o executável do Tesseract instalado via Homebrew
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# Define corretamente o caminho do modelo de idiomas (Mac com Homebrew)
os.environ["TESSDATA_PREFIX"] = "/opt/homebrew/share/tessdata/"

def test_ocr_portugues():
    image_path = "tests/463px-IsaacChagasSiege9.jpg"
    assert os.path.exists(image_path), f"Imagem de teste não encontrada: {image_path}"

    image = Image.open(image_path)
    texto = pytesseract.image_to_string(image, lang="por")

    assert texto.strip() != "", "OCR falhou: nenhum texto foi extraído."
    print("\nTexto extraído:\n", texto)
