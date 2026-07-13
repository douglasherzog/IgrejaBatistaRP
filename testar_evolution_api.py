"""
📱 Script de teste da Evolution API

Verifica se a Evolution API está rodando e envia uma mensagem de teste.
"""

import os
import requests
import asyncio
from app.database import SessionLocal
from app.models import Membro
from app.whatsapp_service import whatsapp_service
from app.utils.telefone import formatar_telefone_exibicao

def verificar_evolution_api():
    """Verifica se a Evolution API está rodando"""
    base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
    apikey = os.getenv("EVOLUTION_API_KEY", "ibinovi_global_apikey")
    instance = os.getenv("EVOLUTION_INSTANCE_NAME", "ibinovi")

    url = f"{base_url}/instance/connectionState/{instance}"
    headers = {"apikey": apikey}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📊 Status da Evolution API: {response.status_code}")
        print(f"📝 Resposta: {response.text}")

        if response.status_code == 200:
            return True
        else:
            print("❌ Evolution API retornou erro. Verifique a instância.")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ Não foi possível conectar à Evolution API em {base_url}")
        print("🔧 Certifique-se de que o Docker está rodando:")
        print("   docker-compose -f docker-compose.evolution.yml up -d")
        return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False


async def enviar_teste():
    """Envia mensagem de teste via Evolution API"""

    print("🚀 TESTE DE ENVIO - EVOLUTION API")
    print("=" * 50)

    if not verificar_evolution_api():
        return False

    db = SessionLocal()
    try:
        douglas = db.query(Membro).filter(Membro.nome.like('%Douglas%')).first()

        if not douglas:
            print("❌ Membro Douglas não encontrado")
            return False

        print(f"\n📌 Destinatário: {douglas.nome}")
        print(f"📱 Telefone: {douglas.telefone}")
        print(f"📱 Exibição: {formatar_telefone_exibicao(douglas.telefone)}")

        mensagem = (
            "🎉 *EVOLUTION API FUNCIONANDO!*\n\n"
            "Olá Douglas!\n\n"
            "✅ API gratuita e open-source configurada\n"
            "📱 Esta mensagem foi enviada pela Evolution API\n\n"
            "🙏 Deus te abençoe!\n\n"
            "📱 *Igreja Batista Nova Vida - Rio Pardo*"
        )

        print(f"\n📤 Enviando mensagem...")
        sucesso = await whatsapp_service.enviar_mensagem(douglas.telefone, mensagem)

        if sucesso:
            print("✅ Mensagem enviada com sucesso!")
            print("📱 Verifique seu WhatsApp!")
            return True
        else:
            print("❌ Falha ao enviar mensagem")
            print("🔍 Verifique se o WhatsApp está conectado na instância")
            return False

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(enviar_teste())
