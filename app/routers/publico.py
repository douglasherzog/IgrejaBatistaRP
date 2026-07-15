from typing import Optional
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal, InvalidOperation
from app.database import get_db
from app.models import ConfiguracaoSite, Culto, Evento, Video, Contribuicao, Admin
from app.routers.site import get_all_configs
from app.auth import get_admin_atual
from app.security import csrf_valid

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    configs = get_all_configs(db)
    cultos = db.query(Culto).filter(Culto.ativo == True).order_by(Culto.ordem).all()
    return templates.TemplateResponse("publico/index.html", {
        "request": request,
        "cfg": configs,
        "cultos": cultos,
    })


@router.get("/sobre", response_class=HTMLResponse)
def sobre(request: Request, db: Session = Depends(get_db)):
    configs = get_all_configs(db)
    return templates.TemplateResponse("publico/sobre.html", {
        "request": request,
        "cfg": configs,
    })


@router.get("/cultos", response_class=HTMLResponse)
def cultos(request: Request, db: Session = Depends(get_db)):
    configs = get_all_configs(db)
    cultos = db.query(Culto).filter(Culto.ativo == True).order_by(Culto.ordem).all()
    return templates.TemplateResponse("publico/cultos.html", {
        "request": request,
        "cfg": configs,
        "cultos": cultos,
    })


@router.get("/eventos", response_class=HTMLResponse)
def eventos(request: Request, db: Session = Depends(get_db)):
    configs = get_all_configs(db)
    hoje = date.today()
    eventos_futuros = db.query(Evento).filter(
        Evento.ativo == True, Evento.data >= hoje
    ).order_by(Evento.data.asc()).all()
    eventos_passados = db.query(Evento).filter(
        Evento.ativo == True, Evento.data < hoje
    ).order_by(Evento.data.desc()).limit(6).all()
    return templates.TemplateResponse("publico/eventos.html", {
        "request": request,
        "cfg": configs,
        "eventos_futuros": eventos_futuros,
        "eventos_passados": eventos_passados,
    })


@router.get("/contato", response_class=HTMLResponse)
def contato(request: Request, db: Session = Depends(get_db)):
    configs = get_all_configs(db)
    return templates.TemplateResponse("publico/contato.html", {
        "request": request,
        "cfg": configs,
    })


@router.get("/videos", response_class=HTMLResponse)
def videos(request: Request, db: Session = Depends(get_db)):
    configs = get_all_configs(db)
    video_destaque = db.query(Video).filter(
        Video.ativo == True, Video.destaque == True
    ).order_by(Video.criado_em.desc()).first()
    outros = db.query(Video).filter(
        Video.ativo == True
    ).order_by(Video.criado_em.desc()).all()
    if video_destaque:
        outros = [v for v in outros if v.id != video_destaque.id]
    return templates.TemplateResponse("publico/videos.html", {
        "request": request,
        "cfg": configs,
        "video_destaque": video_destaque,
        "outros_videos": outros,
    })


@router.get("/contribuicoes", response_class=HTMLResponse)
def contribuicoes(request: Request, db: Session = Depends(get_db)):
    configs = get_all_configs(db)
    return templates.TemplateResponse("publico/contribuicoes.html", {
        "request": request,
        "cfg": configs,
    })


@router.post("/contribuicoes")
async def salvar_contribuicao(
    request: Request,
    db: Session = Depends(get_db),
    csrf_ok: bool = Depends(csrf_valid),
    nome: str = Form(...),
    email: Optional[str] = Form(None),
    telefone: Optional[str] = Form(None),
    valor: Optional[str] = Form(None),
    mensagem: Optional[str] = Form(None),
):
    email = email.strip() if email else None
    telefone = telefone.strip() if telefone else None
    mensagem = mensagem.strip() if mensagem else None
    valor_str = valor.strip() if valor else None

    valor_decimal = None
    if valor_str:
        try:
            valor_decimal = Decimal(valor_str.replace(".", "").replace(",", "."))
        except (InvalidOperation, ValueError):
            pass

    nome = nome.strip()
    if not nome:
        return templates.TemplateResponse("publico/contribuicoes.html", {
            "request": request,
            "cfg": get_all_configs(db),
            "erro": "Por favor, informe seu nome."
        }, status_code=400)

    contribuicao = Contribuicao(
        nome=nome,
        email=email,
        telefone=telefone,
        valor=valor_decimal,
        mensagem=mensagem,
        status="pendente",
    )
    db.add(contribuicao)
    db.commit()

    return RedirectResponse(url="/contribuicoes?ok=1", status_code=302)


@router.get("/admin/contribuicoes", response_class=HTMLResponse)
def listar_contribuicoes(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    contribuicoes = db.query(Contribuicao).order_by(Contribuicao.criado_em.desc()).all()
    return templates.TemplateResponse("admin/contribuicoes/lista.html", {
        "request": request,
        "contribuicoes": contribuicoes,
    })
