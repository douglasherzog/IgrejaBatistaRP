import re


def atualizar_env(chave, valor, conteudo):
    """Atualiza ou adiciona uma variável no .env sem expor segredos"""
    padrao = re.compile(rf"^{re.escape(chave)}\s*=\s*.*$", re.MULTILINE)

    if padrao.search(conteudo):
        conteudo = padrao.sub(f"{chave}={valor}", conteudo)
    else:
        conteudo = conteudo.rstrip() + f"\n\n{chave}={valor}\n"

    return conteudo


with open(".env", "r", encoding="utf-8") as f:
    conteudo = f.read()

conteudo = atualizar_env("WHATSAPP_PROVIDER", "webhook", conteudo)
conteudo = atualizar_env("WHATSAPP_WEBHOOK_URL", "http://localhost:3001/send-message", conteudo)

with open(".env", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✅ Configuração de webhook salva no .env")
