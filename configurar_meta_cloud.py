"""
🔧 CONFIGURADOR DE CREDENCIAIS META CLOUD API

Use este script após obter as credenciais no Meta Developers.

PASSOS PARA OBTER CREDENCIAIS:
1. Acesse https://developers.facebook.com/apps/
2. Crie um aplicativo do tipo "Empresa"
3. Adicione o produto "WhatsApp"
4. Obtenha:
   - Phone Number ID (ex: 123456789012345)
   - Access Token (começa com EAA...)
5. Execute este script e cole as credenciais

COMO USAR:
   venv\Scripts\python.exe configurar_meta_cloud.py
"""

import os
import re
import shutil


def atualizar_env(chave, valor, conteudo):
    """Atualiza ou adiciona uma variável no conteúdo do .env"""
    padrao = re.compile(rf"^{re.escape(chave)}\s*=\s*.*$", re.MULTILINE)

    if padrao.search(conteudo):
        conteudo = padrao.sub(f"{chave}={valor}", conteudo)
    else:
        conteudo += f"\n{chave}={valor}"

    return conteudo


def configurar():
    print("🔧 CONFIGURADOR META CLOUD API")
    print("=" * 50)
    print()

    # Verificar se .env existe, senão copiar do .env.example
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("📄 Criando .env a partir do .env.example...")
            shutil.copy(".env.example", ".env")
        else:
            print("❌ Arquivo .env.example não encontrado. Criando .env vazio...")
            open(".env", "w").close()

    with open(".env", "r", encoding="utf-8") as f:
        conteudo = f.read()

    print("📱 Digite as credenciais da Meta Cloud API:")
    print("(Encontre esses dados no painel do Meta Developers > WhatsApp)")
    print()

    phone_id = input("🔑 Phone Number ID: ").strip()
    access_token = input("🔐 Access Token: ").strip()
    api_version = input("⚙️  API Version (padrão v18.0): ").strip() or "v18.0"

    if not phone_id or not access_token:
        print("\n❌ Phone Number ID e Access Token são obrigatórios!")
        return False

    # Atualizar variáveis
    conteudo = atualizar_env("WHATSAPP_PROVIDER", "meta-cloud", conteudo)
    conteudo = atualizar_env("META_API_VERSION", api_version, conteudo)
    conteudo = atualizar_env("META_PHONE_NUMBER_ID", phone_id, conteudo)
    conteudo = atualizar_env("META_ACCESS_TOKEN", access_token, conteudo)

    # Remover linhas em branco excessivas
    conteudo = re.sub(r"\n{3,}", "\n\n", conteudo)

    with open(".env", "w", encoding="utf-8") as f:
        f.write(conteudo)

    print("\n✅ Credenciais salvas com sucesso no arquivo .env")
    print()
    print("🚀 PRÓXIMOS PASSOS:")
    print("1. Reinicie o servidor FastAPI")
    print("2. Execute: venv\\Scripts\\python.exe testar_meta_cloud.py")
    print("3. Verifique seu WhatsApp!")
    print()
    print("📖 Leia o guia GUARDAR_META_CLOUD_API.md para mais detalhes")

    return True


if __name__ == "__main__":
    configurar()
