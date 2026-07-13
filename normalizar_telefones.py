from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Membro
from app.utils.telefone import normalizar_telefone, formatar_telefone_exibicao
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def atualizar_telefones_existentes():
    """Atualiza todos os números de telefone existentes no banco para o formato normalizado"""
    
    db = SessionLocal()
    
    try:
        # Buscar todos os membros com telefone
        membros = db.query(Membro).filter(
            Membro.telefone.isnot(None),
            Membro.telefone != ""
        ).all()
        
        logger.info(f"📱 Encontrados {len(membros)} membros com telefone para normalizar")
        
        atualizados = 0
        erros = 0
        
        for membro in membros:
            try:
                telefone_original = membro.telefone
                telefone_normalizado = normalizar_telefone(telefone_original)
                
                if telefone_normalizado:
                    membro.telefone = telefone_normalizado
                    atualizados += 1
                    
                    telefone_formatado = formatar_telefone_exibicao(telefone_normalizado)
                    logger.info(f"✅ {membro.nome}: {telefone_original} → {telefone_formatado}")
                else:
                    erros += 1
                    logger.warning(f"❌ {membro.nome}: '{telefone_original}' (inválido)")
                    
            except Exception as e:
                erros += 1
                logger.error(f"❌ Erro ao processar {membro.nome}: {e}")
        
        # Salvar alterações
        db.commit()
        
        logger.info(f"\n📊 RESUMO DA NORMALIZAÇÃO:")
        logger.info(f"✅ Total processados: {len(membros)}")
        logger.info(f"✅ Atualizados com sucesso: {atualizados}")
        logger.info(f"❌ Erros/inválidos: {erros}")
        
        return atualizados, erros
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        db.rollback()
        return 0, 0
    finally:
        db.close()

def verificar_telefones_normalizados():
    """Verifica o estado atual dos telefones no banco"""
    
    db = SessionLocal()
    
    try:
        membros = db.query(Membro).filter(
            Membro.telefone.isnot(None),
            Membro.telefone != ""
        ).all()
        
        logger.info(f"\n📋 VERIFICAÇÃO DE TELEFONES:")
        logger.info(f"Total de membros com telefone: {len(membros)}")
        
        validos = 0
        invalidos = 0
        
        for membro in membros:
            if len(membro.telefone) == 12 and membro.telefone.startswith('55'):
                validos += 1
                telefone_formatado = formatar_telefone_exibicao(membro.telefone)
                logger.info(f"✅ {membro.nome}: {telefone_formatado}")
            else:
                invalidos += 1
                logger.warning(f"❌ {membro.nome}: {membro.telefone}")
        
        logger.info(f"\n📊 RESUMO:")
        logger.info(f"✅ Válidos (formato 55DDDXXXXXXXX): {validos}")
        logger.info(f"❌ Inválidos: {invalidos}")
        
        return validos, invalidos
        
    except Exception as e:
        logger.error(f"❌ Erro na verificação: {e}")
        return 0, 0
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 NORMALIZAÇÃO DE TELEFONES - IGREJA BATISTA NOVA VIDA")
    print("=" * 60)
    
    # Verificar estado atual
    print("\n1️⃣ VERIFICANDO ESTADO ATUAL...")
    validos, invalidos = verificar_telefones_normalizados()
    
    if invalidos > 0:
        print(f"\n2️⃣ ATUALIZANDO {invalidos} TELEFONES INVÁLIDOS...")
        atualizados, erros = atualizar_telefones_existentes()
        
        print(f"\n3️⃣ VERIFICANDO PÓS-ATUALIZAÇÃO...")
        validos_final, invalidos_final = verificar_telefones_normalizados()
        
        print(f"\n🎉 RESULTADO FINAL:")
        print(f"✅ Válidos: {validos_final}")
        print(f"❌ Inválidos: {invalidos_final}")
        print(f"📈 Melhoria: {validos_final - validos} telefones normalizados")
    else:
        print(f"\n✅ Todos os {validos} telefones já estão normalizados!")
