from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date
from decimal import Decimal
from app.database import get_db
from app.models import Lancamento, TipoLancamento, Admin, Membro
from app.auth import get_admin_atual

router = APIRouter()
templates = Jinja2Templates(directory="templates")

CATEGORIAS_RECEITA = ["Dízimo", "Oferta", "Oferta Especial", "Doação", "Outros"]
CATEGORIAS_DESPESA = ["Água/Luz/Gás", "Aluguel", "Manutenção", "Material", "Missões", "Salário", "Outros"]


@router.get("/admin/caixa", response_class=HTMLResponse)
def listar_lancamentos(
    request: Request,
    mes: int = None,
    ano: int = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    hoje = date.today()
    mes = mes or hoje.month
    ano = ano or hoje.year

    query = db.query(Lancamento).filter(
        extract("month", Lancamento.data) == mes,
        extract("year", Lancamento.data) == ano
    ).order_by(Lancamento.data.desc())

    lancamentos = query.all()

    total_receitas = sum(l.valor for l in lancamentos if l.tipo == TipoLancamento.receita)
    total_despesas = sum(l.valor for l in lancamentos if l.tipo == TipoLancamento.despesa)
    saldo = total_receitas - total_despesas

    return templates.TemplateResponse("admin/caixa/lista.html", {
        "request": request,
        "lancamentos": lancamentos,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
        "mes": mes,
        "ano": ano,
        "tipo_lancamento": TipoLancamento
    })


@router.get("/admin/caixa/novo", response_class=HTMLResponse)
def novo_lancamento_page(
    request: Request,
    tipo: str = "receita",
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    membros = db.query(Membro).filter(Membro.ativo == True).order_by(Membro.nome).all()
    return templates.TemplateResponse("admin/caixa/form.html", {
        "request": request,
        "lancamento": None,
        "tipo_pre": tipo,
        "categorias_receita": CATEGORIAS_RECEITA,
        "categorias_despesa": CATEGORIAS_DESPESA,
        "membros": membros,
    })


@router.post("/admin/caixa/novo")
def criar_lancamento(
    tipo: str = Form(...),
    categoria: str = Form(...),
    descricao: str = Form(...),
    valor: str = Form(...),
    data: str = Form(...),
    observacoes: str = Form(default=""),
    membro_id: str = Form(default=""),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    lancamento = Lancamento(
        tipo=TipoLancamento(tipo),
        categoria=categoria,
        descricao=descricao,
        valor=Decimal(valor.replace(",", ".")),
        data=date.fromisoformat(data),
        observacoes=observacoes or None,
        membro_id=int(membro_id) if membro_id else None,
    )
    db.add(lancamento)
    db.commit()
    return RedirectResponse(url="/admin/caixa", status_code=302)


@router.get("/admin/caixa/{id}/editar", response_class=HTMLResponse)
def editar_lancamento_page(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    lancamento = db.query(Lancamento).filter(Lancamento.id == id).first()
    if not lancamento:
        raise HTTPException(status_code=404)
    membros = db.query(Membro).filter(Membro.ativo == True).order_by(Membro.nome).all()
    return templates.TemplateResponse("admin/caixa/form.html", {
        "request": request,
        "lancamento": lancamento,
        "tipo_pre": lancamento.tipo.value,
        "categorias_receita": CATEGORIAS_RECEITA,
        "categorias_despesa": CATEGORIAS_DESPESA,
        "membros": membros,
    })


@router.post("/admin/caixa/{id}/editar")
def atualizar_lancamento(
    id: int,
    tipo: str = Form(...),
    categoria: str = Form(...),
    descricao: str = Form(...),
    valor: str = Form(...),
    data: str = Form(...),
    observacoes: str = Form(default=""),
    membro_id: str = Form(default=""),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    lancamento = db.query(Lancamento).filter(Lancamento.id == id).first()
    if not lancamento:
        raise HTTPException(status_code=404)
    lancamento.tipo = TipoLancamento(tipo)
    lancamento.categoria = categoria
    lancamento.descricao = descricao
    lancamento.valor = Decimal(valor.replace(",", "."))
    lancamento.data = date.fromisoformat(data)
    lancamento.observacoes = observacoes or None
    lancamento.membro_id = int(membro_id) if membro_id else None
    db.commit()
    return RedirectResponse(url="/admin/caixa", status_code=302)


@router.post("/admin/caixa/{id}/excluir")
def excluir_lancamento(
    id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    lancamento = db.query(Lancamento).filter(Lancamento.id == id).first()
    if not lancamento:
        raise HTTPException(status_code=404)
    db.delete(lancamento)
    db.commit()
    return RedirectResponse(url="/admin/caixa", status_code=302)
