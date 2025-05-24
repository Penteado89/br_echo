# api/explain_risk.py

from processing.retriever import buscar_termos_relacionados
import subprocess

def gerar_explicacao_ollama(prompt, modelo="llama2"):
    comando = ["ollama", "run", modelo]
    processo = subprocess.Popen(comando, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    resposta, erro = processo.communicate(input=prompt.encode())
    return resposta.decode()

def explicar_risco_com_ollama(texto_input, modelo="llama2"):
    relacionados = buscar_termos_relacionados(texto_input, k=3)

    if not relacionados:
        return "⚠️ Nenhum termo relevante encontrado no glossário."

    contexto = "\n".join(
        [f"Termo: {r['termo']}\nSubcultura: {r['subcultura']}\nExplicação: {r['explicacao']}" for r in relacionados]
    )

    prompt = f"""
Você é um analista linguístico especializado em discurso extremista. O seguinte texto foi analisado por um sistema automatizado, que recuperou os seguintes conceitos de um glossário sobre subculturas do ódio no Brasil.

Texto analisado:
\"\"\"{texto_input}\"\"\"

Conceitos relacionados:
{contexto}

Escreva uma explicação objetiva e fundamentada justificando por que este conteúdo pode representar um risco linguístico-comportamental. Use vocabulário técnico, mas claro e conciso.
"""

    resposta = gerar_explicacao_ollama(prompt, modelo=modelo)
    return resposta

# Exemplo de uso
if __name__ == "__main__":
    texto = "Esses ratos globalistas controlam tudo. Precisamos de uma limpeza urgente. 1488."
    explicacao = explicar_risco_com_ollama(texto, modelo="llama2")  # ou "mistral"
    print("\n🧠 Explicação gerada localmente com Ollama:\n")
    print(explicacao)
