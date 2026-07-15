from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import Membro, Admin, Lancamento, TipoLancamento
from app.auth import get_admin_atual

router = APIRouter()


@router.get("/admin/membros", response_class=HTMLResponse)
def listar_membros(
    request: Request,
    busca: str = "",
    status: str = None,
    cidade: str = None,
    estado: str = None,
    data_nascimento_inicio: str = None,
    data_nascimento_fim: str = None,
    data_batismo_inicio: str = None,
    data_batismo_fim: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    query = db.query(Membro)
    
    # Filtro de busca por nome
    if busca:
        query = query.filter(
            (Membro.nome.ilike(f"%{busca}%")) |
            (Membro.sobrenome.ilike(f"%{busca}%"))
        )
    
    # Filtro por status
    if status and status in ['ativo', 'inativo']:
        query = query.filter(Membro.ativo == (status == 'ativo'))
    
    # Filtro por cidade
    if cidade:
        query = query.filter(Membro.cidade.ilike(f"%{cidade}%"))
    
    # Filtro por estado
    if estado:
        query = query.filter(Membro.estado.ilike(f"%{estado}%"))
    
    # Filtro por período de nascimento
    if data_nascimento_inicio and data_nascimento_fim:
        try:
            inicio = date.fromisoformat(data_nascimento_inicio)
            fim = date.fromisoformat(data_nascimento_fim)
            query = query.filter(Membro.data_nascimento >= inicio, Membro.data_nascimento <= fim)
        except ValueError:
            pass
    elif data_nascimento_inicio:
        try:
            inicio = date.fromisoformat(data_nascimento_inicio)
            query = query.filter(Membro.data_nascimento >= inicio)
        except ValueError:
            pass
    elif data_nascimento_fim:
        try:
            fim = date.fromisoformat(data_nascimento_fim)
            query = query.filter(Membro.data_nascimento <= fim)
        except ValueError:
            pass
    
    # Filtro por período de batismo
    if data_batismo_inicio and data_batismo_fim:
        try:
            inicio = date.fromisoformat(data_batismo_inicio)
            fim = date.fromisoformat(data_batismo_fim)
            query = query.filter(Membro.data_batismo >= inicio, Membro.data_batismo <= fim)
        except ValueError:
            pass
    elif data_batismo_inicio:
        try:
            inicio = date.fromisoformat(data_batismo_inicio)
            query = query.filter(Membro.data_batismo >= inicio)
        except ValueError:
            pass
    elif data_batismo_fim:
        try:
            fim = date.fromisoformat(data_batismo_fim)
            query = query.filter(Membro.data_batismo <= fim)
        except ValueError:
            pass
    
    membros = query.order_by(Membro.nome).all()
    
    # Calcular receita total para cada membro
    for membro in membros:
        receitas = db.query(Lancamento).filter(
            Lancamento.membro_id == membro.id,
            Lancamento.tipo == TipoLancamento.receita
        ).all()
        membro.receita_total = sum(r.valor for r in receitas)
    
    # Obter lista única de cidades e estados para filtros
    cidades = db.query(Membro.cidade).filter(Membro.cidade.isnot(None)).distinct().order_by(Membro.cidade).all()
    estados = db.query(Membro.estado).filter(Membro.estado.isnot(None)).distinct().order_by(Membro.estado).all()
    
    return templates.TemplateResponse("admin/membros/lista.html", {
        "request": request, 
        "membros": membros, 
        "busca": busca,
        "status": status,
        "cidade": cidade,
        "estado": estado,
        "data_nascimento_inicio": data_nascimento_inicio,
        "data_nascimento_fim": data_nascimento_fim,
        "data_batismo_inicio": data_batismo_inicio,
        "data_batismo_fim": data_batismo_fim,
        "cidades": [c[0] for c in cidades if c[0]],
        "estados": [e[0] for e in estados if e[0]],
    })


@router.get("/admin/membros/imprimir", response_class=HTMLResponse)
def imprimir_membros(
    request: Request,
    busca: str = "",
    status: str = None,
    cidade: str = None,
    estado: str = None,
    data_nascimento_inicio: str = None,
    data_nascimento_fim: str = None,
    data_batismo_inicio: str = None,
    data_batismo_fim: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    # Reutilizar a mesma lógica de filtros da listagem
    query = db.query(Membro)
    
    if busca:
        query = query.filter(
            (Membro.nome.ilike(f"%{busca}%")) |
            (Membro.sobrenome.ilike(f"%{busca}%"))
        )
    
    if status and status in ['ativo', 'inativo']:
        query = query.filter(Membro.ativo == (status == 'ativo'))
    
    if cidade:
        query = query.filter(Membro.cidade.ilike(f"%{cidade}%"))
    
    if estado:
        query = query.filter(Membro.estado.ilike(f"%{estado}%"))
    
    if data_nascimento_inicio and data_nascimento_fim:
        try:
            inicio = date.fromisoformat(data_nascimento_inicio)
            fim = date.fromisoformat(data_nascimento_fim)
            query = query.filter(Membro.data_nascimento >= inicio, Membro.data_nascimento <= fim)
        except ValueError:
            pass
    elif data_nascimento_inicio:
        try:
            inicio = date.fromisoformat(data_nascimento_inicio)
            query = query.filter(Membro.data_nascimento >= inicio)
        except ValueError:
            pass
    elif data_nascimento_fim:
        try:
            fim = date.fromisoformat(data_nascimento_fim)
            query = query.filter(Membro.data_nascimento <= fim)
        except ValueError:
            pass
    
    if data_batismo_inicio and data_batismo_fim:
        try:
            inicio = date.fromisoformat(data_batismo_inicio)
            fim = date.fromisoformat(data_batismo_fim)
            query = query.filter(Membro.data_batismo >= inicio, Membro.data_batismo <= fim)
        except ValueError:
            pass
    elif data_batismo_inicio:
        try:
            inicio = date.fromisoformat(data_batismo_inicio)
            query = query.filter(Membro.data_batismo >= inicio)
        except ValueError:
            pass
    elif data_batismo_fim:
        try:
            fim = date.fromisoformat(data_batismo_fim)
            query = query.filter(Membro.data_batismo <= fim)
        except ValueError:
            pass
    
    membros = query.order_by(Membro.nome).all()
    
    # Calcular receita total para cada membro
    for membro in membros:
        receitas = db.query(Lancamento).filter(
            Lancamento.membro_id == membro.id,
            Lancamento.tipo == TipoLancamento.receita
        ).all()
        membro.receita_total = sum(r.valor for r in receitas)
    
    # Estatísticas
    total = len(membros)
    ativos = sum(1 for m in membros if m.ativo)
    inativos = total - ativos
    
    return templates.TemplateResponse("admin/membros/imprimir.html", {
        "request": request,
        "membros": membros,
        "busca": busca,
        "status": status,
        "cidade": cidade,
        "estado": estado,
        "data_nascimento_inicio": data_nascimento_inicio,
        "data_nascimento_fim": data_nascimento_fim,
        "data_batismo_inicio": data_batismo_inicio,
        "data_batismo_fim": data_batismo_fim,
        "total": total,
        "ativos": ativos,
        "inativos": inativos,
        "hoje": date.today(),
    })


@router.get("/admin/membros/{id}/detalhes", response_class=HTMLResponse)
def detalhes_membro(
    id: int,
    request: Request,
    data_inicio: str = None,
    data_fim: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    membro = db.query(Membro).filter(Membro.id == id).first()
    if not membro:
        raise HTTPException(status_code=404)
    
    # Buscar receitas do membro
    query = db.query(Lancamento).filter(
        Lancamento.membro_id == membro.id,
        Lancamento.tipo == TipoLancamento.receita
    )
    
    # Aplicar filtro de período se fornecido
    if data_inicio and data_fim:
        try:
            inicio = date.fromisoformat(data_inicio)
            fim = date.fromisoformat(data_fim)
            query = query.filter(Lancamento.data >= inicio, Lancamento.data <= fim)
        except ValueError:
            pass
    
    receitas = query.order_by(Lancamento.data.desc()).all()
    
    # Calcular estatísticas
    total_receitas = sum(r.valor for r in receitas)
    
    # Agrupar por categoria
    categorias = {}
    for r in receitas:
        if r.categoria not in categorias:
            categorias[r.categoria] = 0
        categorias[r.categoria] += r.valor
    
    # Agrupar por ano/mês
    mensal = {}
    for r in receitas:
        chave = f"{r.data.year}-{r.data.month:02d}"
        if chave not in mensal:
            mensal[chave] = 0
        mensal[chave] += r.valor
    
    return templates.TemplateResponse("admin/membros/detalhes.html", {
        "request": request,
        "membro": membro,
        "receitas": receitas,
        "total_receitas": total_receitas,
        "categorias": dict(sorted(categorias.items())),
        "mensal": dict(sorted(mensal.items(), reverse=True)),
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "hoje": date.today(),
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
