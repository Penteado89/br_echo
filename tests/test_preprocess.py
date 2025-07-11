import pandas as pd
from utils.preprocess import carregar_glossario, ativar_tokens, aplicar_schema_padrao

glossario = carregar_glossario()
print("🔍 Iniciando teste de pré-processamento...")

if not glossario:
    print("⚠️ Glossário vazio ou não carregado. Verifique o caminho.")
    exit()

print(f"📘 Glossário carregado com {len(glossario)} entradas.")

df = pd.DataFrame({
    "texto": [
        "Os globalistas do Fórum de Davos estão dominando tudo.",
        "A Jihad vai continuar. Allahu Akbar.",
        "As feministas radicais estão destruindo a família."
    ]
})

df["tokens_ativados"] = df["texto"].apply(lambda t: ativar_tokens(t, glossario))
df = aplicar_schema_padrao(df)

print("✅ Saída final:")
print(df[["texto", "tokens_ativados"]])
