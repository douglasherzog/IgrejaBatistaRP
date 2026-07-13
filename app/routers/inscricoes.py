from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import InscricaoEvento, Evento, Admin
from app.auth import get_admin_atual
from app.routers.site import get_all_configs
from app.security import csrf_valid

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/eventos/{id}/inscrever")
async def inscrever_evento(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    csrf_ok: bool = Depends(csrf_valid),
    nome: str = Form(...),
    telefone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
):
    evento = db.query(Evento).filter(Evento.id == id).first()
    if not evento:
        raise HTTPException(status_code=404)
    insc = InscricaoEvento(
        evento_id=id,
        nome=nome.strip(),
        telefone=telefone.strip() if telefone else None,
        email=email.strip() if email else None,
    )
    db.add(insc)
    db.commit()
    return RedirectResponse(url=f"/eventos?inscricao=1", status_code=302)


@router.get("/admin/inscricoes", response_class=HTMLResponse)
def listar_inscricoes(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    eventos_com_inscricoes = db.query(Evento).filter(
        Evento.data >= date.today()
    ).order_by(Evento.data.asc()).all()
    return templates.TemplateResponse("admin/inscricoes/lista.html", {
        "request": request,
        "eventos": eventos_com_inscricoes,
    })


@router.get("/admin/inscricoes/{evento_id}", response_class=HTMLResponse)
def ver_inscricoes_evento(
    evento_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404)
    inscricoes = db.query(InscricaoEvento).filter(
        InscricaoEvento.evento_id == evento_id
    ).order_by(InscricaoEvento.criado_em.desc()).all()
    return templates.TemplateResponse("admin/inscricoes/detalhe.html", {
        "request": request,
        "evento": evento,
        "inscricoes": inscricoes,
    })


@router.post("/admin/inscricoes/{id}/excluir")
def excluir_inscricao(
    id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    insc = db.query(InscricaoEvento).filter(InscricaoEvento.id == id).first()
    if not insc:
        raise HTTPException(status_code=404)
    evento_id = insc.evento_id
    db.delete(insc)
    db.commit()
    return RedirectResponse(url=f"/admin/inscricoes/{evento_id}", status_code=302)
