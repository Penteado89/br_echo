# utils/pdf_export.py

from fpdf import FPDF
import os
import textwrap

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Relatório de Triagem BR-ECHO", ln=True, align="C")

    def chapter_title(self, title):
        self.set_font("Arial", "B", 11)
        self.cell(0, 10, title, ln=True)

    def chapter_body(self, body):
        self.set_font("Arial", "", 10)
        for line in textwrap.wrap(body, width=90):
            self.multi_cell(0, 5, line)
        self.ln()

def gerar_pdf(texto, score_regras, score_bert, explicacao, path="relatorios/relatorio_br_echo.pdf"):
    os.makedirs("relatorios", exist_ok=True)
    pdf = PDF()
    pdf.add_page()

    pdf.chapter_title("Texto analisado:")
    pdf.chapter_body(texto)

    pdf.chapter_title("Score por regras linguísticas:")
    pdf.chapter_body(f"{score_regras} / 5")

    pdf.chapter_title("Score por modelo BERT fine-tuned:")
    pdf.chapter_body(f"{score_bert} / 5")

    pdf.chapter_title("Explicação linguística via RAG + LLM:")
    pdf.chapter_body(explicacao)

    pdf.output(path)
    return path
