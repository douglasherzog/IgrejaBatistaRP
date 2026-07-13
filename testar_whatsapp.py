import asyncio
from app.database import SessionLocal
from app.models import Membro
from app.whatsapp_service import whatsapp_service
from app.utils.telefone import formatar_telefone_exibicao
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def testar_whatsapp():
    """Testa envio de mensagens WhatsApp com diferentes cenários"""
    
    db = SessionLocal()
    
    try:
        # Buscar membros com telefone
        membros = db.query(Membro).filter(
            Membro.telefone.isnot(None),
            Membro.telefone != ""
        ).all()
        
        print("📱 TESTE DE ENVIO WHATSAPP - IGREJA BATISTA NOVA VIDA")
        print("=" * 60)
        
        if not membros:
            print("❌ Nenhum membro com telefone encontrado para teste")
            return
        
        print(f"📋 Encontrados {len(membros)} membros com telefone:")
        for i, membro in enumerate(membros, 1):
            telefone_formatado = formatar_telefone_exibicao(membro.telefone)
            print(f"  {i}. {membro.nome} - {telefone_formatado}")
        
        print("\n🧪 Teste 1: Mensagem Personalizada")
        print("-" * 40)
        
        # Teste 1: Mensagem personalizada
        mensagem_teste = (
            "🧪 *Mensagem de Teste - IBINOVI*\n\n"
            "Olá {nome}, esta é uma mensagem de teste do sistema de notificações por WhatsApp da Igreja Batista Nova Vida.\n\n"
            "📱 Sistema funcionando perfeitamente!\n"
            "🙏 Deus te abençoe!\n\n"
            "📱 *Igreja Batista Nova Vida - Rio Pardo*"
        )
        
        sucesso_count = 0
        for membro in membros:
            mensagem_personalizada = mensagem_teste.replace("{nome}", membro.nome)
            print(f"📤 Enviando para {membro.nome} ({formatar_telefone_exibicao(membro.telefone)})...")
            
            sucesso = await whatsapp_service.enviar_mensagem(membro.telefone, mensagem_personalizada)
            if sucesso:
                print(f"  ✅ Sucesso!")
                sucesso_count += 1
            else:
                print(f"  ❌ Falha!")
            
            # Pequena pausa entre envios
            await asyncio.sleep(1)
        
        print(f"\n📊 Resultado Teste 1: {sucesso_count}/{len(membros)} mensagens enviadas com sucesso")
        
        print("\n🧪 Teste 2: Lembrete de Culto")
        print("-" * 40)
        
        # Teste 2: Lembrete de culto
        print("📤 Enviando lembrete de culto para todos...")
        culto_count = await whatsapp_service.enviar_lembrete_culto(db)
        print(f"📊 Resultado Teste 2: {culto_count} lembretes de culto enviados")
        
        print("\n🧪 Teste 3: Mensagem de Aniversário (Simulação)")
        print("-" * 40)
        
        # Teste 3: Aniversário (simulação para os membros existentes)
        print("📤 Enviando mensagens de aniversário (simulação)...")
        aniversario_count = await whatsapp_service.enviar_aniversario(db)
        print(f"📊 Resultado Teste 3: {aniversario_count} mensagens de aniversário enviadas")
        
        print("\n🎉 TESTES CONCLUÍDOS!")
        print("=" * 60)
        print("📊 Resumo Final:")
        print(f"  ✅ Mensagens personalizadas: {sucesso_count}/{len(membros)}")
        print(f"  ✅ Lembretes de culto: {culto_count}")
        print(f"  ✅ Mensagens de aniversário: {aniversario_count}")
        
        if sucesso_count > 0:
            print("\n🎯 O sistema de notificações WhatsApp está funcionando!")
            print("📱 Em produção, as mensagens seriam enviadas para os números reais.")
        else:
            print("\n⚠️ Nenhuma mensagem foi enviada (modo simulação)")
        
    except Exception as e:
        logger.error(f"❌ Erro durante os testes: {e}")
        print(f"\n❌ Erro durante os testes: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Iniciando testes de WhatsApp...")
    asyncio.run(testar_whatsapp())
