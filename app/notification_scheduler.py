import asyncio
import logging
from datetime import datetime, date, time, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Evento
from app.whatsapp_service import whatsapp_service

logger = logging.getLogger(__name__)

class NotificationScheduler:
    """Agendador de notificações automáticas"""
    
    def __init__(self):
        self.running = False
        
    async def start_scheduler(self):
        """Inicia o agendador de notificações"""
        if self.running:
            return
            
        self.running = True
        logger.info("🚀 Agendador de notificações iniciado")
        
        while self.running:
            try:
                await self.check_notifications()
                await asyncio.sleep(300)  # Verificar a cada 5 minutos
            except Exception as e:
                logger.error(f"❌ Erro no agendador: {e}")
                await asyncio.sleep(60)  # Esperar 1 minuto em caso de erro
    
    async def check_notifications(self):
        """Verifica e envia notificações pendentes"""
        now = datetime.now()
        db = SessionLocal()
        
        try:
            # Verificar aniversariantes do dia (às 9h da manhã)
            if now.hour == 9 and now.minute < 5:
                await whatsapp_service.enviar_aniversario(db)
            
            # Verificar cultos de hoje (às 18h)
            if now.hour == 18 and now.minute < 5:
                await whatsapp_service.enviar_lembrete_culto(db)
            
            # Verificar eventos próximos (24h antes)
            await self.check_event_reminders(db, now)
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar notificações: {e}")
        finally:
            db.close()
    
    async def check_event_reminders(self, db: Session, now: datetime):
        """Verifica lembretes de eventos"""
        try:
            # Buscar eventos amanhã
            amanha = now.date() + timedelta(days=1)
            
            eventos_amanha = db.query(Evento).filter(
                Evento.data == amanha,
                Evento.ativo == True
            ).all()
            
            for evento in eventos_amanha:
                # Enviar lembrete se ainda não enviou hoje
                await whatsapp_service.enviar_lembrete_evento(db, evento, 24)
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar lembretes de eventos: {e}")
    
    def stop_scheduler(self):
        """Para o agendador"""
        self.running = False
        logger.info("⏹️ Agendador de notificações parado")

# Instância global
scheduler = NotificationScheduler()
