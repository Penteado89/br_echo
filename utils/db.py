# utils/db.py

import sqlite3
from datetime import datetime

DB_PATH = "triagens_br_echo.db"

def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS triagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT,
            score_regras INTEGER,
            score_bert INTEGER,
            explicacao TEXT,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

def salvar_triagem(texto, score_regras, score_bert, explicacao):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO triagens (texto, score_regras, score_bert, explicacao, data)
        VALUES (?, ?, ?, ?, ?)
    """, (texto, score_regras, score_bert, explicacao, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def listar_triagens():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM triagens ORDER BY data DESC")
    dados = cur.fetchall()
    conn.close()
    return dados
