from scripts.classificador_regras import classificar_por_regras
from processing.predict_bert import carregar_modelo_bert, prever_com_bert
from api.explain_risk import explicar_risco_com_ollama

# Texto de exemplo
texto = "Esses degenerados globalistas estão destruindo a civilização ocidental. 1488!"

print("🔍 Texto de teste:")
print(texto)
print("-" * 60)

# Teste de regras linguísticas
score_regras, ativadas = classificar_por_regras(texto)
print(f"🚨 Score por regras linguísticas: {score_regras}")
if ativadas:
    for r in ativadas:
        print(f"- {r['nome']} ({r['subcultura']}): {r['comentario']}")

# Teste do modelo BERT
tokenizer, modelo = carregar_modelo_bert()
score_bert = prever_com_bert(texto, tokenizer, modelo)
print(f"🤖 Score por BERT fine-tuned: {score_bert}")

# Teste da explicação com RAG + LLM
explicacao = explicar_risco_com_ollama(texto, modelo="llama2")
print("🧠 Explicação gerada com RAG + LLM:")
print(explicacao)