import asyncio
from app.database import SessionLocal
from app.models import Membro
from app.whatsapp_service import whatsapp_service
from app.utils.telefone import formatar_telefone_exibicao
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def testar_envio_real():
    """Testa envio real de mensagem via Z-API"""
    
    db = SessionLocal()
    
    try:
        print("📱 TESTE DE ENVIO REAL - Z-API CONFIGURADA")
        print("=" * 50)
        
        # Buscar membros com telefone
        membros = db.query(Membro).filter(
            Membro.telefone.isnot(None),
            Membro.telefone != ""
        ).all()
        
        if not membros:
            print("❌ Nenhum membro com telefone encontrado")
            return
        
        print(f"📋 Membros encontrados: {len(membros)}")
        for i, membro in enumerate(membros, 1):
            telefone_formatado = formatar_telefone_exibicao(membro.telefone)
            print(f"  {i}. {membro.nome} - {telefone_formatado}")
        
        print("\n🧪 Enviando mensagem de teste REAL...")
        print("📱 Esta mensagem será enviada para o WhatsApp REAL!")
        print()
        
        # Mensagem de teste
        mensagem_teste = (
            "🧪 *TESTE REAL - IBINOVI*\n\n"
            "Olá! Esta é uma mensagem de teste REAL do sistema de notificações da Igreja Batista Nova Vida.\n\n"
            "✅ Sistema configurado com Z-API!\n"
            "✅ WhatsApp funcionando!\n"
            "🙏 Deus te abençoe!\n\n"
            "📱 *Igreja Batista Nova Vida - Rio Pardo*"
        )
        
        # Enviar para o primeiro membro (teste)
        membro_teste = membros[0]
        print(f"📤 Enviando para {membro_teste.nome} ({formatar_telefone_exibicao(membro_teste.telefone)})...")
        
        sucesso = await whatsapp_service.enviar_mensagem(membro_teste.telefone, mensagem_teste)
        
        if sucesso:
            print("✅ Mensagem enviada com SUCESSO!")
            print("📱 Verifique seu WhatsApp agora!")
            print("🎉 Sistema Z-API funcionando perfeitamente!")
        else:
            print("❌ Falha ao enviar mensagem")
            print("🔍 Verifique:")
            print("   • Seu WhatsApp está conectado na Z-API?")
            print("   • As credenciais estão corretas?")
            print("   • Seu plano Z-API está ativo?")
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        print(f"\n❌ Erro no teste: {e}")
        print("\n🔍 Possíveis causas:")
        print("   • WhatsApp não conectado na Z-API")
        print("   • Credenciais inválidas")
        print("   • Problema de rede")
        print("   • Plano Z-API inativo")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Iniciando teste de envio REAL via Z-API...")
    asyncio.run(testar_envio_real())
