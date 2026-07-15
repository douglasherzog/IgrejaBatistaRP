from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date
from decimal import Decimal
from app.database import get_db
from app.models import Lancamento, TipoLancamento, Admin, Membro
from app.auth import get_admin_atual

router = APIRouter()

CATEGORIAS_RECEITA = ["Dízimo", "Oferta", "Oferta Especial", "Doação", "Outros"]
CATEGORIAS_DESPESA = ["Água/Luz/Gás", "Aluguel", "Manutenção", "Material", "Missões", "Salário", "Outros"]


@router.get("/admin/caixa", response_class=HTMLResponse)
def listar_lancamentos(
    request: Request,
    mes: int = None,
    ano: int = None,
    data_inicio: str = None,
    data_fim: str = None,
    categoria: str = None,
    tipo: str = None,
    membro_id: int = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    hoje = date.today()
    
    # Montar query base
    query = db.query(Lancamento)
    
    # Filtros
    if data_inicio and data_fim:
        # Período personalizado
        try:
            inicio = date.fromisoformat(data_inicio)
            fim = date.fromisoformat(data_fim)
            query = query.filter(Lancamento.data >= inicio, Lancamento.data <= fim)
        except ValueError:
            pass  # Se datas inválidas, ignora
    elif mes and ano:
        # Filtro por mês/ano (mantido para compatibilidade)
        query = query.filter(
            extract("month", Lancamento.data) == mes,
            extract("year", Lancamento.data) == ano
        )
    else:
        # Padrão: mês atual
        query = query.filter(
            extract("month", Lancamento.data) == hoje.month,
            extract("year", Lancamento.data) == hoje.year
        )
    
    # Filtros adicionais
    if categoria:
        query = query.filter(Lancamento.categoria == categoria)
    
    if tipo and tipo in ['receita', 'despesa']:
        query = query.filter(Lancamento.tipo == TipoLancamento(tipo))
    
    if membro_id:
        query = query.filter(Lancamento.membro_id == membro_id)
    
    # Ordenar
    lancamentos = query.order_by(Lancamento.data.desc()).all()
    
    # Calcular totais
    total_receitas = sum(l.valor for l in lancamentos if l.tipo == TipoLancamento.receita)
    total_despesas = sum(l.valor for l in lancamentos if l.tipo == TipoLancamento.despesa)
    saldo = total_receitas - total_despesas
    
    # Obter lista de membros para filtro
    membros = db.query(Membro).filter(Membro.ativo == True).order_by(Membro.nome).all()
    
    # Preparar contexto para template
    context = {
        "request": request,
        "lancamentos": lancamentos,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
        "mes": mes or hoje.month,
        "ano": ano or hoje.year,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "categoria": categoria,
        "tipo": tipo,
        "membro_id": membro_id,
        "tipo_lancamento": TipoLancamento,
        "categorias_receita": CATEGORIAS_RECEITA,
        "categorias_despesa": CATEGORIAS_DESPESA,
        "membros": membros,
    }
    
    return templates.TemplateResponse("admin/caixa/lista.html", context)


@router.get("/admin/caixa/imprimir", response_class=HTMLResponse)
def imprimir_lancamentos(
    request: Request,
    mes: int = None,
    ano: int = None,
    data_inicio: str = None,
    data_fim: str = None,
    categoria: str = None,
    tipo: str = None,
    membro_id: int = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    hoje = date.today()
    
    # Montar query base (mesma lógica da listagem)
    query = db.query(Lancamento)
    
    # Filtros
    if data_inicio and data_fim:
        try:
            inicio = date.fromisoformat(data_inicio)
            fim = date.fromisoformat(data_fim)
            query = query.filter(Lancamento.data >= inicio, Lancamento.data <= fim)
        except ValueError:
            pass
    elif mes and ano:
        query = query.filter(
            extract("month", Lancamento.data) == mes,
            extract("year", Lancamento.data) == ano
        )
    else:
        query = query.filter(
            extract("month", Lancamento.data) == hoje.month,
            extract("year", Lancamento.data) == hoje.year
        )
    
    if categoria:
        query = query.filter(Lancamento.categoria == categoria)
    
    if tipo and tipo in ['receita', 'despesa']:
        query = query.filter(Lancamento.tipo == TipoLancamento(tipo))
    
    if membro_id:
        query = query.filter(Lancamento.membro_id == membro_id)
    
    # Ordenar por data
    lancamentos = query.order_by(Lancamento.data.asc()).all()  # ordem crescente para impressão
    
    # Calcular totais
    total_receitas = sum(l.valor for l in lancamentos if l.tipo == TipoLancamento.receita)
    total_despesas = sum(l.valor for l in lancamentos if l.tipo == TipoLancamento.despesa)
    saldo = total_receitas - total_despesas
    
    # Obter informações do membro se filtrado
    membro_filtrado = None
    if membro_id:
        membro_filtrado = db.query(Membro).filter(Membro.id == membro_id).first()
    
    # Preparar contexto para template de impressão
    context = {
        "request": request,
        "lancamentos": lancamentos,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
        "mes": mes or hoje.month,
        "ano": ano or hoje.year,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "categoria": categoria,
        "tipo": tipo,
        "membro_id": membro_id,
        "membro_filtrado": membro_filtrado,
        "tipo_lancamento": TipoLancamento,
        "hoje": hoje,
    }
    
    return templates.TemplateResponse("admin/caixa/imprimir.html", context)


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
