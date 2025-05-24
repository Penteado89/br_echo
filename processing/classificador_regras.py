# processing/classificador_regras.py

import json

# Carregar regras do arquivo
def carregar_regras(path="glossario/regras_brecho.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

REGRAS = carregar_regras()

def classificar_por_regras(texto):
    texto_lower = texto.lower()
    score_max = 0
    regras_ativadas = []

    for regra in REGRAS:
        palavras = regra["palavras_chave"]
        padroes = regra["padrões_sintáticos"]

        ativada = any(p.lower() in texto_lower for p in palavras) or \
                  any(p.lower() in texto_lower for p in padroes)

        if ativada:
            score_max = max(score_max, regra["score_base"])
            regras_ativadas.append({
                "nome": regra["nome"],
                "subcultura": regra["subcultura"],
                "comentario": regra["comentario"],
                "score": regra["score_base"]
            })

    return score_max, regras_ativadas

# Exemplo
if __name__ == "__main__":
    texto = "A raça ariana está sendo ameaçada. Precisamos reagir. 1488!"
    score, ativadas = classificar_por_regras(texto)
    print(f"Score de risco: {score}")
    for r in ativadas:
        print(f"→ {r['nome']} | Score: {r['score']}")
