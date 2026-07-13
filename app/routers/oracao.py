from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import PedidoOracao, Admin
from app.auth import get_admin_atual
from app.routers.site import get_all_configs
from app.security import csrf_valid

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/pedidos-oracao")
async def criar_pedido(
    request: Request,
    db: Session = Depends(get_db),
    csrf_ok: bool = Depends(csrf_valid),
    nome: str = Form(...),
    pedido: str = Form(...),
    publico: Optional[str] = Form(None),
):
    novo = PedidoOracao(
        nome=nome.strip(),
        pedido=pedido.strip(),
        publico=publico == "on",
        status="novo",
    )
    db.add(novo)
    db.commit()
    return RedirectResponse(url="/pedidos-oracao?ok=1", status_code=302)


@router.get("/pedidos-oracao", response_class=HTMLResponse)
def pedidos_oracao_page(
    request: Request,
    db: Session = Depends(get_db)
):
    configs = get_all_configs(db)
    pedidos_publicos = db.query(PedidoOracao).filter(
        PedidoOracao.publico == True, PedidoOracao.status == "aprovado"
    ).order_by(PedidoOracao.criado_em.desc()).limit(20).all()
    return templates.TemplateResponse("publico/oracao.html", {
        "request": request,
        "cfg": configs,
        "pedidos_publicos": pedidos_publicos,
    })


@router.get("/admin/oracao", response_class=HTMLResponse)
def listar_pedidos(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    pedidos = db.query(PedidoOracao).order_by(PedidoOracao.criado_em.desc()).all()
    return templates.TemplateResponse("admin/oracao/lista.html", {
        "request": request,
        "pedidos": pedidos,
    })


@router.post("/admin/oracao/{id}/status")
async def atualizar_status(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    pedido = db.query(PedidoOracao).filter(PedidoOracao.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404)
    form = await request.form()
    pedido.status = form.get("status", "lido")
    db.commit()
    return RedirectResponse(url="/admin/oracao", status_code=302)


@router.post("/admin/oracao/{id}/excluir")
def excluir_pedido(
    id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    pedido = db.query(PedidoOracao).filter(PedidoOracao.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404)
    db.delete(pedido)
    db.commit()
    return RedirectResponse(url="/admin/oracao", status_code=302)
