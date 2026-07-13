"""
📱 Script de teste da Meta Cloud API (WhatsApp Oficial)

Verifica se as credenciais estão configuradas e envia uma mensagem de teste.
"""

import os
import asyncio
from app.database import SessionLocal
from app.models import Membro
from app.whatsapp_service import whatsapp_service
from app.utils.telefone import formatar_telefone_exibicao


def verificar_configuracao():
    """Verifica se as variáveis de ambiente estão configuradas"""
    print("🔍 VERIFICANDO CONFIGURAÇÃO META CLOUD API")
    print("=" * 50)

    phone_id = os.getenv("META_PHONE_NUMBER_ID", "")
    token = os.getenv("META_ACCESS_TOKEN", "")
    provider = os.getenv("WHATSAPP_PROVIDER", "meta-cloud")

    print(f"🔳 Provedor configurado: {provider}")
    print(f"🔑 Phone Number ID: {phone_id if phone_id else 'NÃO CONFIGURADO'}")
    print(f"🔐 Access Token: {'CONFIGURADO' if token else 'NÃO CONFIGURADO'} ({len(token)} caracteres)")

    if not phone_id or phone_id == "SEU_PHONE_NUMBER_ID":
        print("\n❌ META_PHONE_NUMBER_ID não configurado")
        print("📖 Siga o guia GUARDAR_META_CLOUD_API.md")
        return False

    if not token or token == "SEU_ACCESS_TOKEN":
        print("\n❌ META_ACCESS_TOKEN não configurado")
        print("📖 Siga o guia GUARDAR_META_CLOUD_API.md")
        return False

    print("\n✅ Configuração presente")
    return True


async def enviar_teste():
    """Envia mensagem de teste via Meta Cloud API"""

    if not verificar_configuracao():
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
            "🎉 *META CLOUD API - IBINOVI*\n\n"
            "Olá Douglas!\n\n"
            "✅ API oficial do WhatsApp configurada\n"
            "📱 Esta mensagem foi enviada pela Meta Cloud API\n\n"
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
            print("🔍 Verifique:")
            print("   • Se o número de destino está autorizado no modo teste")
            print("   • Se a conta business está verificada")
            print("   • Se o token ainda é válido")
            return False

    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 TESTE DE ENVIO - META CLOUD API")
    print("=" * 50)
    asyncio.run(enviar_teste())
