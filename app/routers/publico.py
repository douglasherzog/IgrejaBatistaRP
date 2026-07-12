from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import ConfiguracaoSite, Culto, Evento, Video
from app.routers.site import get_all_configs

router = APIRouter()
templates = Jinja2Templates(directory="templates")


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
