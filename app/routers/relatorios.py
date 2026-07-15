import csv
import io
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from app.templates import templates
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from datetime import date
from collections import defaultdict
from app.database import get_db
from app.models import Lancamento, TipoLancamento, Membro, Evento, InscricaoEvento, PedidoOracao, Admin
from app.auth import get_admin_atual

router = APIRouter()

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
MESES_FULL = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
              "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


@router.get("/admin/relatorios/caixa", response_class=HTMLResponse)
def relatorio_caixa(
    request: Request,
    ano: int = Query(default=None),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    hoje = date.today()
    ano = ano or hoje.year

    lancamentos_ano = db.query(Lancamento).filter(
        extract("year", Lancamento.data) == ano
    ).all()

    receitas_mes = [0.0] * 12
    despesas_mes = [0.0] * 12
    cat_receitas = defaultdict(float)
    cat_despesas = defaultdict(float)

    for l in lancamentos_ano:
        m = l.data.month - 1
        if l.tipo == TipoLancamento.receita:
            receitas_mes[m] += float(l.valor)
            cat_receitas[l.categoria] += float(l.valor)
        else:
            despesas_mes[m] += float(l.valor)
            cat_despesas[l.categoria] += float(l.valor)

    total_receitas = sum(receitas_mes)
    total_despesas = sum(despesas_mes)
    saldo_ano = total_receitas - total_despesas

    return templates.TemplateResponse("admin/relatorios/caixa.html", {
        "request": request,
        "ano": ano,
        "receitas_mes": receitas_mes,
        "despesas_mes": despesas_mes,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo_ano": saldo_ano,
        "cat_receitas": dict(cat_receitas),
        "cat_despesas": dict(cat_despesas),
        "meses": MESES,
    })


@router.get("/admin/relatorios/caixa/csv")
def relatorio_caixa_csv(
    ano: int = Query(default=None),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    hoje = date.today()
    ano = ano or hoje.year

    lancamentos = db.query(Lancamento).filter(
        extract("year", Lancamento.data) == ano
    ).order_by(Lancamento.data).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Data", "Tipo", "Categoria", "Descricao", "Valor", "Dizimista"])
    for l in lancamentos:
        dizimista = ""
        if l.categoria == "Dízimo" and l.membro:
            dizimista = f"{l.membro.nome} {l.membro.sobrenome}"
        writer.writerow([
            l.data.strftime("%d/%m/%Y"),
            l.tipo.value,
            l.categoria,
            l.descricao,
            f"R$ {float(l.valor):.2f}",
            dizimista,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=caixa_{ano}.csv"}
    )


@router.get("/admin/relatorios/membros", response_class=HTMLResponse)
def relatorio_membros(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    hoje = date.today()
    total = db.query(Membro).count()
    ativos = db.query(Membro).filter(Membro.ativo == True).count()
    inativos = total - ativos

    batismos_ano = db.query(Membro).filter(
        extract("year", Membro.data_batismo) == hoje.year
    ).count()

    novos_ano = db.query(Membro).filter(
        extract("year", Membro.criado_em) == hoje.year
    ).count()

    batismos_por_mes = [0] * 12
    for m in db.query(Membro).filter(Membro.data_batismo.isnot(None)).all():
        if m.data_batismo.year == hoje.year:
            batismos_por_mes[m.data_batismo.month - 1] += 1

    novos_por_mes = [0] * 12
    for m in db.query(Membro).all():
        if m.criado_em and m.criado_em.year == hoje.year:
            novos_por_mes[m.criado_em.month - 1] += 1

    aniversariantes = db.query(Membro).filter(
        Membro.ativo == True,
        Membro.data_nascimento.isnot(None),
        extract("month", Membro.data_nascimento) == hoje.month
    ).order_by(extract("day", Membro.data_nascimento)).all()

    return templates.TemplateResponse("admin/relatorios/membros.html", {
        "request": request,
        "total": total,
        "ativos": ativos,
        "inativos": inativos,
        "batismos_ano": batismos_ano,
        "novos_ano": novos_ano,
        "batismos_por_mes": batismos_por_mes,
        "novos_por_mes": novos_por_mes,
        "aniversariantes": aniversariantes,
        "meses": MESES,
        "mes_atual": MESES_FULL[hoje.month - 1],
    })


@router.get("/admin/relatorios/membros/csv")
def relatorio_membros_csv(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    membros = db.query(Membro).order_by(Membro.nome).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nome", "Sobrenome", "Nascimento", "Batismo", "Telefone", "Email", "Cidade", "Status"])
    for m in membros:
        writer.writerow([
            m.nome,
            m.sobrenome,
            m.data_nascimento.strftime("%d/%m/%Y") if m.data_nascimento else "",
            m.data_batismo.strftime("%d/%m/%Y") if m.data_batismo else "",
            m.telefone or "",
            m.email or "",
            m.cidade or "",
            "Ativo" if m.ativo else "Inativo",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=membros.csv"}
    )


@router.get("/admin/relatorios/geral", response_class=HTMLResponse)
def relatorio_geral(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    hoje = date.today()

    total_membros = db.query(Membro).count()
    novos_mes = db.query(Membro).filter(
        extract("month", Membro.criado_em) == hoje.month,
        extract("year", Membro.criado_em) == hoje.year
    ).count()

    lanc_ano = db.query(Lancamento).filter(extract("year", Lancamento.data) == hoje.year).all()
    rec_mes = [0.0] * 12
    desp_mes = [0.0] * 12
    for l in lanc_ano:
        idx = l.data.month - 1
        if l.tipo == TipoLancamento.receita:
            rec_mes[idx] += float(l.valor)
        else:
            desp_mes[idx] += float(l.valor)

    eventos_futuros = db.query(Evento).filter(Evento.data >= hoje, Evento.ativo == True).count()
    total_inscricoes = db.query(InscricaoEvento).count()
    pedidos_novos = db.query(PedidoOracao).filter(PedidoOracao.status == "novo").count()
    total_pedidos = db.query(PedidoOracao).count()

    return templates.TemplateResponse("admin/relatorios/geral.html", {
        "request": request,
        "total_membros": total_membros,
        "novos_mes": novos_mes,
        "rec_mes": rec_mes,
        "desp_mes": desp_mes,
        "eventos_futuros": eventos_futuros,
        "total_inscricoes": total_inscricoes,
        "pedidos_novos": pedidos_novos,
        "total_pedidos": total_pedidos,
        "meses": MESES,
        "ano": hoje.year,
    })
