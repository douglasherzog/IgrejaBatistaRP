import os
import requests
import json
import asyncio
from datetime import datetime, date, time, timedelta
from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.models import Membro, Evento, ConfiguracaoSite
from app.database import get_db

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Serviço para envio de notificações por WhatsApp"""
    
    def __init__(self):
        # Provedor da API de WhatsApp: "webhook" (padrão), "meta-cloud", "evolution-api", "z-api" ou "simulacao"
        self.provider = os.getenv("WHATSAPP_PROVIDER", "webhook").lower()

        # Configurações Webhook (servidor WhatsApp local via whatsapp-web.js)
        self.webhook_url = os.getenv("WHATSAPP_WEBHOOK_URL", "http://localhost:3001/send-message")

        # Configurações Meta Cloud API (WhatsApp Oficial)
        self.meta_api_version = os.getenv("META_API_VERSION", "v18.0")
        self.meta_phone_number_id = os.getenv("META_PHONE_NUMBER_ID", "")
        self.meta_access_token = os.getenv("META_ACCESS_TOKEN", "")

        # Configurações Z-API (caso use)
        self.z_api_url = os.getenv("Z_API_URL", "")
        self.z_api_key = os.getenv("Z_API_KEY", "")

        # Configurações Evolution API (open-source, self-hosted e gratuita)
        self.evolution_base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.evolution_instance = os.getenv("EVOLUTION_INSTANCE_NAME", "ibinovi")
        self.evolution_apikey = os.getenv("EVOLUTION_API_KEY", "")

        self.phone_number = os.getenv("WHATSAPP_PHONE_NUMBER", "5551999999999")  # Número do WhatsApp da igreja

        logger.info(f"🚀 WhatsAppService iniciado com provedor: {self.provider}")

        # Versículos da Bíblia por faixa de idade
        self.versiculos_por_idade = {
            "crianca": [
                "Porque eu bem sei os pensamentos que penso de vós, diz o Senhor; pensamentos de paz, e não de mal, para vos dar o fim que esperais. - Jeremias 29:11",
                "E disse-lhes: Vinde após mim, e eu vos farei pescadores de homens. - Mateus 4:19",
                "Não temas, porque eu sou contigo; não te assombres, porque eu sou teu Deus. - Isaías 41:10"
            ],
            "adolescente": [
                "Lembra-te do teu Criador nos dias da tua mocidade. - Eclesiastes 12:1",
                "Como purificará o jovem o seu caminho? Observando-o conforme a tua palavra. - Salmos 119:9",
                "Confia no Senhor de todo o teu coração, e não te estribes no teu próprio entendimento. - Provérbios 3:5"
            ],
            "jovem": [
                "Tudo posso naquele que me fortalece. - Filipenses 4:13",
                "Os que esperam no Senhor renovarão as suas forças. - Isaías 40:31",
                "Não vos sobreveio tentação, senão humana; mas Deus é fiel. - 1 Coríntios 10:13"
            ],
            "adulto": [
                "O Senhor é o meu pastor; nada me faltará. - Salmos 23:1",
                "Tudo quanto Deus faz durará eternamente; nada se lhe pode acrescentar. - Eclesiastes 3:14",
                "Bem-aventurado o homem que não anda segundo o conselho dos ímpios. - Salmos 1:1"
            ],
            "idoso": [
                "Até a minha velhice e as cãs, ó Deus, não me desampares. - Salmos 71:18",
                "Coroa de honra são as cãs, quando se acham no caminho da justiça. - Provérbios 16:31",
                "Na presença de Deus há plenitude de alegria. - Salmos 16:11"
            ]
        }
    
    async def enviar_mensagem(self, telefone: str, mensagem: str) -> bool:
        """Envia mensagem por WhatsApp usando o provedor configurado"""
        if not telefone:
            logger.warning("⚠️ Telefone vazio. Mensagem não enviada.")
            return False

        telefone_limpo = self.formatar_telefone(telefone).replace('@c.us', '')
        logger.info(f"📱 Enviando WhatsApp para {telefone_limpo}: {mensagem[:50]}...")

        try:
            if self.provider == "webhook":
                return self._enviar_webhook(telefone_limpo, mensagem)
            elif self.provider == "meta-cloud":
                return self._enviar_meta_cloud(telefone_limpo, mensagem)
            elif self.provider == "evolution-api":
                return self._enviar_evolution_api(telefone_limpo, mensagem)
            elif self.provider == "z-api":
                return self._enviar_z_api(telefone_limpo, mensagem)
            else:
                logger.info("🔶 MODO SIMULAÇÃO: mensagem não enviada para WhatsApp real")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao enviar WhatsApp: {e}")
            return False

    def _enviar_webhook(self, telefone: str, mensagem: str) -> bool:
        """Envia mensagem via webhook para servidor WhatsApp local"""
        if not self.webhook_url:
            logger.error("❌ WHATSAPP_WEBHOOK_URL não configurado")
            return False

        payload = {
            "number": telefone,
            "message": mensagem
        }

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=120)

            if response.status_code in (200, 201):
                logger.info(f"✅ Mensagem enviada via webhook: {response.text}")
                return True
            else:
                logger.error(f"❌ Erro webhook {response.status_code}: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Não foi possível conectar ao servidor WhatsApp local em {self.webhook_url}")
            logger.error("📱 Verifique se o servidor Node.js está rodando")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar webhook: {e}")
            return False

    def _enviar_meta_cloud(self, telefone: str, mensagem: str) -> bool:
        """Envia mensagem via Meta Cloud API (WhatsApp Oficial)"""
        if not self.meta_phone_number_id or not self.meta_access_token:
            logger.error("❌ META_PHONE_NUMBER_ID e META_ACCESS_TOKEN precisam ser configurados no .env")
            return False

        url = f"https://graph.facebook.com/{self.meta_api_version}/{self.meta_phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.meta_access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": telefone,
            "type": "text",
            "text": {"body": mensagem}
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code in (200, 201):
            logger.info(f"✅ Mensagem enviada via Meta Cloud API: {response.text}")
            return True
        else:
            logger.error(f"❌ Erro Meta Cloud API {response.status_code}: {response.text}")
            return False

    def _enviar_evolution_api(self, telefone: str, mensagem: str) -> bool:
        """Envia mensagem via Evolution API (open-source)"""
        url = f"{self.evolution_base_url}/message/sendText/{self.evolution_instance}"
        headers = {"Content-Type": "application/json"}

        if self.evolution_apikey:
            headers["apikey"] = self.evolution_apikey

        payload = {
            "number": telefone,
            "text": mensagem,
            "options": {
                "delay": 1200,
                "presence": "composing"
            }
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code in (200, 201):
            logger.info(f"✅ Mensagem enviada via Evolution API: {response.text}")
            return True
        else:
            logger.error(f"❌ Erro Evolution API {response.status_code}: {response.text}")
            return False

    def _enviar_z_api(self, telefone: str, mensagem: str) -> bool:
        """Envia mensagem via Z-API (paga)"""
        url = f"{self.z_api_url}/send-text"
        headers = {"Content-Type": "application/json"}
        payload = {"phone": telefone, "message": mensagem}

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            logger.info(f"✅ Mensagem enviada via Z-API: {response.text}")
            return True
        else:
            logger.error(f"❌ Erro Z-API {response.status_code}: {response.text}")
            return False
    
    def formatar_telefone(self, telefone: str) -> str:
        """Formata número de telefone para WhatsApp"""
        # Remove caracteres não numéricos
        numero = ''.join(filter(str.isdigit, telefone))

        # Adiciona código do Brasil se necessário
        if not numero.startswith('55'):
            numero = '55' + numero

        return numero + '@c.us'
    
    def obter_versiculo_por_idade(self, idade: int) -> str:
        """Obtém versículo bíblico baseado na idade"""
        if idade <= 12:
            categoria = "crianca"
        elif idade <= 17:
            categoria = "adolescente"
        elif idade <= 25:
            categoria = "jovem"
        elif idade <= 60:
            categoria = "adulto"
        else:
            categoria = "idoso"
        
        import random
        versiculos = self.versiculos_por_idade[categoria]
        return random.choice(versiculos)
    
    async def enviar_lembrete_culto(self, db: Session):
        """Envia lembrete de culto para todos os membros"""
        try:
            # Obter membros ativos com telefone
            membros = db.query(Membro).filter(
                Membro.ativo == True,
                Membro.telefone.isnot(None),
                Membro.telefone != ""
            ).all()
            
            mensagem_culto = (
                "🙏 *LEMBRETE DE CULTO - IGREJA BATISTA NOVA VIDA* 🙏\n\n"
                "📅 *Hoje*: Culto de Adoração\n"
                "⏰ *Horário*: 19h30min\n"
                "📍 *Local*: Rua Principal, 123 - Centro\n\n"
                "Venha adorar ao Senhor conosco! "
                "Sua presença faz toda a diferença! 🙌\n\n"
                "📱 *Igreja Batista Nova Vida - Rio Pardo*"
            )
            
            sucesso_count = 0
            for membro in membros:
                if await self.enviar_mensagem(membro.telefone, mensagem_culto):
                    sucesso_count += 1
                    await asyncio.sleep(1)  # Evitar spam da API
            
            logger.info(f"✅ Lembretes de culto enviados: {sucesso_count}/{len(membros)}")
            return sucesso_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar lembretes de culto: {e}")
            return 0
    
    async def enviar_aniversario(self, db: Session):
        """Envia mensagens de aniversário"""
        try:
            hoje = date.today()
            
            # Obter aniversariantes do dia
            aniversariantes = db.query(Membro).filter(
                Membro.ativo == True,
                Membro.telefone.isnot(None),
                Membro.telefone != "",
                extract('month', Membro.data_nascimento) == hoje.month,
                extract('day', Membro.data_nascimento) == hoje.day
            ).all()
            
            for membro in aniversariantes:
                idade = hoje.year - membro.data_nascimento.year
                versiculo = self.obter_versiculo_por_idade(idade)
                
                mensagem_aniversario = (
                    f"🎉 *FELIZ ANIVERSÁRIO, {membro.nome.upper()}!* 🎂\n\n"
                    f"🙏 *Que Deus te abençoe ricamente neste dia especial!*\n\n"
                    f"📖 *Versículo do dia:*\n"
                    f"_{versiculo}_\n\n"
                    f"🎁 *Presente de Deus*: Mais um ano de vida e caminhada na fé!\n"
                    f"🌟 *Sua família da IBINOVI te ama muito!*\n\n"
                    f"📱 *Igreja Batista Nova Vida - Rio Pardo*"
                )
                
                await self.enviar_mensagem(membro.telefone, mensagem_aniversario)
                await asyncio.sleep(1)
            
            logger.info(f"✅ Mensagens de aniversário enviadas: {len(aniversariantes)}")
            return len(aniversariantes)
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagens de aniversário: {e}")
            return 0
    
    async def enviar_lembrete_evento(self, db: Session, evento: Evento, horas_antes: int = 24):
        """Envia lembrete de evento específico"""
        try:
            # Obter membros ativos
            membros = db.query(Membro).filter(
                Membro.ativo == True,
                Membro.telefone.isnot(None),
                Membro.telefone != ""
            ).all()
            
            data_evento = evento.data.strftime('%d/%m/%Y')
            hora_evento = evento.hora.strftime('%H:%M') if evento.hora else "a definir"
            
            mensagem_evento = (
                f"📅 *LEMBRETE DE EVENTO - IGREJA BATISTA NOVA VIDA* 📅\n\n"
                f"🎯 *{evento.titulo.upper()}*\n"
                f"📅 *Data*: {data_evento}\n"
                f"⏰ *Horário*: {hora_evento}\n"
                f"📍 *Local*: {evento.local or 'Igreja'}\n\n"
                f"{evento.descricao or ''}\n\n"
                f"🙌 *Participe conosco! Sua presença é muito importante!*\n\n"
                f"📱 *Igreja Batista Nova Vida - Rio Pardo*"
            )
            
            sucesso_count = 0
            for membro in membros:
                if await self.enviar_mensagem(membro.telefone, mensagem_evento):
                    sucesso_count += 1
                    await asyncio.sleep(1)
            
            logger.info(f"✅ Lembretes de evento '{evento.titulo}' enviados: {sucesso_count}/{len(membros)}")
            return sucesso_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar lembretes de evento: {e}")
            return 0
    
    async def enviar_mensagem_personalizada(self, db: Session, mensagem: str, filtro_ativos: bool = True):
        """Envia mensagem personalizada para membros"""
        try:
            query = db.query(Membro).filter(
                Membro.telefone.isnot(None),
                Membro.telefone != ""
            )
            
            if filtro_ativos:
                query = query.filter(Membro.ativo == True)
            
            membros = query.all()
            
            sucesso_count = 0
            for membro in membros:
                # Personalizar mensagem com nome do membro
                mensagem_personalizada = mensagem.replace("{nome}", membro.nome)
                
                if await self.enviar_mensagem(membro.telefone, mensagem_personalizada):
                    sucesso_count += 1
                    await asyncio.sleep(1)
            
            logger.info(f"✅ Mensagem personalizada enviada: {sucesso_count}/{len(membros)}")
            return sucesso_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem personalizada: {e}")
            return 0

# Instância global do serviço
whatsapp_service = WhatsAppService()
