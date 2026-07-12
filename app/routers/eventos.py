from datetime import date
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Evento, Admin
from app.auth import get_admin_atual

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin/eventos", response_class=HTMLResponse)
def listar_eventos(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    eventos = db.query(Evento).order_by(Evento.data.desc()).all()
    return templates.TemplateResponse("admin/eventos/lista.html", {
        "request": request,
        "eventos": eventos,
    })


@router.get("/admin/eventos/novo", response_class=HTMLResponse)
def novo_evento_page(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    return templates.TemplateResponse("admin/eventos/form.html", {
        "request": request,
        "evento": None,
    })


@router.post("/admin/eventos/novo")
async def criar_evento(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    form = await request.form()
    evento = Evento(
        titulo=form.get("titulo", ""),
        descricao=form.get("descricao", "") or None,
        data=date.fromisoformat(form.get("data", "")),
        horario=form.get("horario", "") or None,
        local=form.get("local", "") or None,
        imagem_url=form.get("imagem_url", "") or None,
        destaque=form.get("destaque") == "on",
        ativo=form.get("ativo") != "off",
    )
    db.add(evento)
    db.commit()
    return RedirectResponse(url="/admin/eventos", status_code=302)


@router.get("/admin/eventos/{id}/editar", response_class=HTMLResponse)
def editar_evento_page(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    evento = db.query(Evento).filter(Evento.id == id).first()
    if not evento:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("admin/eventos/form.html", {
        "request": request,
        "evento": evento,
    })


@router.post("/admin/eventos/{id}/editar")
async def atualizar_evento(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    evento = db.query(Evento).filter(Evento.id == id).first()
    if not evento:
        raise HTTPException(status_code=404)
    form = await request.form()
    evento.titulo = form.get("titulo", "")
    evento.descricao = form.get("descricao", "") or None
    evento.data = date.fromisoformat(form.get("data", ""))
    evento.horario = form.get("horario", "") or None
    evento.local = form.get("local", "") or None
    evento.imagem_url = form.get("imagem_url", "") or None
    evento.destaque = form.get("destaque") == "on"
    evento.ativo = form.get("ativo") != "off"
    db.commit()
    return RedirectResponse(url="/admin/eventos", status_code=302)


@router.post("/admin/eventos/{id}/excluir")
def excluir_evento(
    id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    evento = db.query(Evento).filter(Evento.id == id).first()
    if not evento:
        raise HTTPException(status_code=404)
    db.delete(evento)
    db.commit()
    return RedirectResponse(url="/admin/eventos", status_code=302)
