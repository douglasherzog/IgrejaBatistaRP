from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime, date, timedelta
from app.database import get_db
from app.models import Membro, Evento, Admin
from app.auth import get_admin_atual
from app.whatsapp_service import whatsapp_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/notificacoes", response_class=HTMLResponse)
def painel_notificacoes(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    """Painel de gerenciamento de notificações"""
    
    # Estatísticas
    total_membros = db.query(Membro).filter(Membro.ativo == True).count()
    membros_com_whatsapp = db.query(Membro).filter(
        Membro.ativo == True,
        Membro.telefone.isnot(None),
        Membro.telefone != ""
    ).count()
    
    # Aniversariantes de hoje
    hoje = date.today()
    aniversariantes_hoje = db.query(Membro).filter(
        Membro.ativo == True,
        extract('month', Membro.data_nascimento) == hoje.month,
        extract('day', Membro.data_nascimento) == hoje.day
    ).all()
    
    # Próximos eventos (7 dias)
    eventos_proximos = db.query(Evento).filter(
        Evento.data >= hoje,
        Evento.data <= hoje + timedelta(days=7),
        Evento.ativo == True
    ).order_by(Evento.data).all()
    
    return templates.TemplateResponse("admin/notificacoes/painel.html", {
        "request": request,
        "total_membros": total_membros,
        "membros_com_whatsapp": membros_com_whatsapp,
        "aniversariantes_hoje": aniversariantes_hoje,
        "eventos_proximos": eventos_proximos,
        "hoje": hoje
    })

@router.post("/admin/notificacoes/enviar-culto")
async def enviar_lembrete_culto(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    """Envia lembrete de culto imediato"""
    
    try:
        count = await whatsapp_service.enviar_lembrete_culto(db)
        logger.info(f"📱 Admin {admin.email} enviou lembrete de culto para {count} membros")
        
        # Redirecionar com mensagem de sucesso
        return RedirectResponse(
            url="/admin/notificacoes?msg=success&text=Lembrete de culto enviado com sucesso!",
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar lembrete de culto: {e}")
        return RedirectResponse(
            url="/admin/notificacoes?msg=error&text=Erro ao enviar lembrete de culto",
            status_code=302
        )

@router.post("/admin/notificacoes/enviar-aniversarios")
async def enviar_aniversarios(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    """Envia mensagens de aniversário"""
    
    try:
        count = await whatsapp_service.enviar_aniversario(db)
        logger.info(f"📱 Admin {admin.email} enviou mensagens de aniversário para {count} membros")
        
        return RedirectResponse(
            url="/admin/notificacoes?msg=success&text=Mensagens de aniversário enviadas com sucesso!",
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagens de aniversário: {e}")
        return RedirectResponse(
            url="/admin/notificacoes?msg=error&text=Erro ao enviar mensagens de aniversário",
            status_code=302
        )

@router.post("/admin/notificacoes/enviar-evento")
async def enviar_lembrete_evento(
    request: Request,
    evento_id: int = Form(...),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    """Envia lembrete de evento específico"""
    
    try:
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if not evento:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        count = await whatsapp_service.enviar_lembrete_evento(db, evento)
        logger.info(f"📱 Admin {admin.email} enviou lembrete do evento '{evento.titulo}' para {count} membros")
        
        return RedirectResponse(
            url="/admin/notificacoes?msg=success&text=Lembrete do evento enviado com sucesso!",
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar lembrete de evento: {e}")
        return RedirectResponse(
            url="/admin/notificacoes?msg=error&text=Erro ao enviar lembrete do evento",
            status_code=302
        )

@router.post("/admin/notificacoes/enviar-personalizada")
async def enviar_mensagem_personalizada(
    request: Request,
    mensagem: str = Form(...),
    filtro_ativos: bool = Form(True),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    """Envia mensagem personalizada"""
    
    try:
        if not mensagem.strip():
            return RedirectResponse(
                url="/admin/notificacoes?msg=error&text=A mensagem não pode estar vazia",
                status_code=302
            )
        
        count = await whatsapp_service.enviar_mensagem_personalizada(
            db, mensagem, filtro_ativos
        )
        
        logger.info(f"📱 Admin {admin.email} enviou mensagem personalizada para {count} membros")
        
        return RedirectResponse(
            url="/admin/notificacoes?msg=success&text=Mensagem personalizada enviada com sucesso!",
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem personalizada: {e}")
        return RedirectResponse(
            url="/admin/notificacoes?msg=error&text=Erro ao enviar mensagem personalizada",
            status_code=302
        )

@router.get("/admin/notificacoes/teste")
def teste_whatsapp(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    """Página de teste de WhatsApp"""
    
    # Buscar um membro para teste
    membro_teste = db.query(Membro).filter(
        Membro.ativo == True,
        Membro.telefone.isnot(None),
        Membro.telefone != ""
    ).first()
    
    return templates.TemplateResponse("admin/notificacoes/teste.html", {
        "request": request,
        "membro_teste": membro_teste
    })

@router.post("/admin/notificacoes/teste-envio")
async def teste_envio_whatsapp(
    request: Request,
    telefone: str = Form(...),
    mensagem: str = Form(...),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    """Testa envio de WhatsApp"""
    
    try:
        sucesso = await whatsapp_service.enviar_mensagem(telefone, mensagem)
        
        if sucesso:
            return RedirectResponse(
                url="/admin/notificacoes/teste?msg=success&text=Mensagem de teste enviada com sucesso!",
                status_code=302
            )
        else:
            return RedirectResponse(
                url="/admin/notificacoes/teste?msg=error&text=Falha ao enviar mensagem de teste",
                status_code=302
            )
            
    except Exception as e:
        logger.error(f"❌ Erro no teste de WhatsApp: {e}")
        return RedirectResponse(
            url="/admin/notificacoes/teste?msg=error&text=Erro no teste de envio",
            status_code=302
        )
