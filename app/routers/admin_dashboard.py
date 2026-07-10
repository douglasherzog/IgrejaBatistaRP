from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import date
from app.database import get_db
from app.models import Membro, Lancamento, TipoLancamento, Admin
from app.auth import get_admin_atual

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    hoje = date.today()
    total_membros = db.query(Membro).count()

    lancamentos_mes = db.query(Lancamento).filter(
        extract("month", Lancamento.data) == hoje.month,
        extract("year", Lancamento.data) == hoje.year
    ).all()

    total_receitas = sum(l.valor for l in lancamentos_mes if l.tipo == TipoLancamento.receita)
    total_despesas = sum(l.valor for l in lancamentos_mes if l.tipo == TipoLancamento.despesa)
    saldo = total_receitas - total_despesas

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "total_membros": total_membros,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
    })
