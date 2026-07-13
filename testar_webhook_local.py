"""
📱 Script de teste do servidor WhatsApp local (whatsapp-web.js)

Verifica se o servidor Node.js está rodando e envia uma mensagem de teste.
"""

import os
import requests
import asyncio
from app.database import SessionLocal
from app.models import Membro
from app.whatsapp_service import whatsapp_service
from app.utils.telefone import formatar_telefone_exibicao


def verificar_servidor_local():
    """Verifica se o servidor WhatsApp local está rodando e conectado"""
    webhook_url = os.getenv("WHATSAPP_WEBHOOK_URL", "http://localhost:3001/send-message")
    status_url = webhook_url.replace('/send-message', '/status')

    print(f"🔍 Verificando servidor WhatsApp local em {status_url}")

    try:
        response = requests.get(status_url, timeout=10)
        data = response.json()

        print(f"📊 Status HTTP: {response.status_code}")
        print(f"📝 Resposta: {data}")

        if data.get('ready'):
            print("✅ WhatsApp local conectado e pronto!")
            return True
        elif data.get('qrCodeGenerated'):
            print("🔑 QR Code gerado! Escaneie com seu WhatsApp.")
            return False
        else:
            print("⏳ WhatsApp ainda não conectado. Aguarde ou escaneie o QR Code.")
            return False

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Não foi possível conectar ao servidor WhatsApp local em {status_url}")
        print("🔧 Inicie o servidor Node.js:")
        print("   cd whatsapp-server")
        print("   npm install")
        print("   npm start")
        return False
    except Exception as e:
        print(f"\n❌ Erro ao verificar servidor: {e}")
        return False


async def enviar_teste():
    """Envia mensagem de teste via servidor WhatsApp local"""

    print("🚀 TESTE DE ENVIO - WHATSAPP WEB.JS LOCAL")
    print("=" * 50)

    if not verificar_servidor_local():
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
            "🎉 *WHATSAPP WEB.JS FUNCIONANDO!*\n\n"
            "Olá Douglas!\n\n"
            "✅ Servidor WhatsApp local conectado\n"
            "📱 Esta mensagem foi enviada via whatsapp-web.js\n\n"
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
            print("🔍 Verifique os logs do servidor Node.js")
            return False

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(enviar_teste())
