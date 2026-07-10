from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import Membro, Admin
from app.auth import get_admin_atual

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin/membros", response_class=HTMLResponse)
def listar_membros(
    request: Request,
    busca: str = "",
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    query = db.query(Membro)
    if busca:
        query = query.filter(
            (Membro.nome.ilike(f"%{busca}%")) |
            (Membro.sobrenome.ilike(f"%{busca}%"))
        )
    membros = query.order_by(Membro.nome).all()
    return templates.TemplateResponse("admin/membros/lista.html", {
        "request": request, "membros": membros, "busca": busca
    })


@router.get("/admin/membros/novo", response_class=HTMLResponse)
def novo_membro_page(request: Request, admin: Admin = Depends(get_admin_atual)):
    return templates.TemplateResponse("admin/membros/form.html", {
        "request": request, "membro": None
    })


@router.post("/admin/membros/novo")
def criar_membro(
    request: Request,
    nome: str = Form(...),
    sobrenome: str = Form(...),
    data_nascimento: str = Form(default=""),
    data_batismo: str = Form(default=""),
    telefone: str = Form(default=""),
    email: str = Form(default=""),
    endereco: str = Form(default=""),
    bairro: str = Form(default=""),
    cidade: str = Form(default=""),
    estado: str = Form(default=""),
    cep: str = Form(default=""),
    observacoes: str = Form(default=""),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    membro = Membro(
        nome=nome,
        sobrenome=sobrenome,
        data_nascimento=date.fromisoformat(data_nascimento) if data_nascimento else None,
        data_batismo=date.fromisoformat(data_batismo) if data_batismo else None,
        telefone=telefone or None,
        email=email or None,
        endereco=endereco or None,
        bairro=bairro or None,
        cidade=cidade or None,
        estado=estado or None,
        cep=cep or None,
        observacoes=observacoes or None,
    )
    db.add(membro)
    db.commit()
    return RedirectResponse(url="/admin/membros", status_code=302)


@router.get("/admin/membros/{id}/editar", response_class=HTMLResponse)
def editar_membro_page(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    membro = db.query(Membro).filter(Membro.id == id).first()
    if not membro:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("admin/membros/form.html", {
        "request": request, "membro": membro
    })


@router.post("/admin/membros/{id}/editar")
def atualizar_membro(
    id: int,
    request: Request,
    nome: str = Form(...),
    sobrenome: str = Form(...),
    data_nascimento: str = Form(default=""),
    data_batismo: str = Form(default=""),
    telefone: str = Form(default=""),
    email: str = Form(default=""),
    endereco: str = Form(default=""),
    bairro: str = Form(default=""),
    cidade: str = Form(default=""),
    estado: str = Form(default=""),
    cep: str = Form(default=""),
    observacoes: str = Form(default=""),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    membro = db.query(Membro).filter(Membro.id == id).first()
    if not membro:
        raise HTTPException(status_code=404)
    membro.nome = nome
    membro.sobrenome = sobrenome
    membro.data_nascimento = date.fromisoformat(data_nascimento) if data_nascimento else None
    membro.data_batismo = date.fromisoformat(data_batismo) if data_batismo else None
    membro.telefone = telefone or None
    membro.email = email or None
    membro.endereco = endereco or None
    membro.bairro = bairro or None
    membro.cidade = cidade or None
    membro.estado = estado or None
    membro.cep = cep or None
    membro.observacoes = observacoes or None
    db.commit()
    return RedirectResponse(url="/admin/membros", status_code=302)


@router.post("/admin/membros/{id}/excluir")
def excluir_membro(
    id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    membro = db.query(Membro).filter(Membro.id == id).first()
    if not membro:
        raise HTTPException(status_code=404)
    db.delete(membro)
    db.commit()
    return RedirectResponse(url="/admin/membros", status_code=302)
