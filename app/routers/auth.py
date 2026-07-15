from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Admin, AcessoLog, DispositivoOtpExento, PermissaoAdmin
from app import auth as auth_service

router = APIRouter()

AREAS_ADMIN = [
    ("dashboard", "Dashboard"),
    ("membros", "Membros"),
    ("caixa", "Caixa"),
    ("eventos", "Eventos"),
    ("videos", "Vídeos"),
    ("fotos", "Fotos"),
    ("oracao", "Oração"),
    ("contribuicoes", "Contribuições"),
    ("inscricoes", "Inscrições"),
    ("importar", "Importar"),
    ("relatorios", "Relatórios"),
    ("site", "Configurações do Site"),
    ("usuarios", "Usuários Admin"),
    ("logs", "Logs de Acesso"),
]


def log_acesso(db: Session, acao: str, admin: Admin = None, email: str = None, path: str = None, request: Request = None, detalhes: str = None, device_token: str = None):
    log = AcessoLog(
        admin_id=admin.id if admin else None,
        email=email or (admin.email if admin else None),
        acao=acao,
        path=path,
        ip=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
        device_token=device_token,
        detalhes=detalhes,
    )
    db.add(log)
    db.commit()


@router.get("/admin/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/admin/login")
def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin or not auth_service.verificar_senha(senha, admin.senha_hash):
        log_acesso(db, acao="login_falha", email=email, path="/admin/login", request=request)
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "erro": "Email ou senha incorretos"}
        )

    device_token = request.cookies.get("device_token") or auth_service.gerar_device_token()
    isento = auth_service.dispositivo_otp_exento(db, admin.id, request)

    log_acesso(db, acao="login_sucesso", admin=admin, path="/admin/login", request=request, device_token=device_token, detalhes=f"isento={isento}")

    if admin.totp_ativo and not isento:
        token_temp = auth_service.criar_token({"sub": admin.id, "etapa": "totp"})
        resp = RedirectResponse(url="/admin/totp", status_code=302)
        resp.set_cookie("totp_token", token_temp, httponly=True, max_age=300)
        resp.set_cookie("device_token", device_token, httponly=True, max_age=3600 * 24 * 365)
        return resp

    token = auth_service.criar_token({"sub": admin.id})
    resp = RedirectResponse(url="/admin/dashboard", status_code=302)
    resp.set_cookie("session_token", token, httponly=True, max_age=3600 * 8)
    resp.set_cookie("device_token", device_token, httponly=True, max_age=3600 * 24 * 365)
    return resp


@router.get("/admin/totp", response_class=HTMLResponse)
def totp_page(request: Request):
    return templates.TemplateResponse("admin/totp.html", {"request": request})


@router.post("/admin/totp")
def totp_verificar(
    request: Request,
    codigo: str = Form(...),
    totp_token: str = None,
    db: Session = Depends(get_db)
):
    totp_token = request.cookies.get("totp_token")
    if not totp_token:
        return RedirectResponse(url="/admin/login", status_code=302)
    payload = auth_service.verificar_token(totp_token)
    if not payload or payload.get("etapa") != "totp":
        return RedirectResponse(url="/admin/login", status_code=302)
    admin = db.query(Admin).filter(Admin.id == int(payload["sub"])).first()
    if not admin or not auth_service.verificar_totp(admin.totp_secret, codigo):
        log_acesso(db, acao="totp_falha", admin=admin, path="/admin/totp", request=request)
        return templates.TemplateResponse(
            "admin/totp.html",
            {"request": request, "erro": "Código inválido ou expirado"}
        )
    device_token = request.cookies.get("device_token") or auth_service.gerar_device_token()
    log_acesso(db, acao="totp_sucesso", admin=admin, path="/admin/totp", request=request, device_token=device_token, detalhes=f"fingerprint={auth_service.get_fingerprint(request)}")
    token = auth_service.criar_token({"sub": admin.id})
    resp = RedirectResponse(url="/admin/dashboard", status_code=302)
    resp.set_cookie("session_token", token, httponly=True, max_age=3600 * 8)
    resp.set_cookie("device_token", device_token, httponly=True, max_age=3600 * 24 * 365)
    resp.delete_cookie("totp_token")
    return resp


@router.get("/admin/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_atual)
):
    log_acesso(db, acao="logout", admin=admin, path="/admin/logout", request=request)
    resp = RedirectResponse(url="/admin/login", status_code=302)
    resp.delete_cookie("session_token")
    return resp


@router.get("/admin/setup-totp", response_class=HTMLResponse)
def setup_totp_page(request: Request, token: str = None, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=400, detail="Token inválido")
    payload = auth_service.verificar_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    admin = db.query(Admin).filter(Admin.id == int(payload["sub"])).first()
    if not admin:
        raise HTTPException(status_code=404)
    if not admin.totp_secret:
        admin.totp_secret = auth_service.gerar_totp_secret()
        db.commit()
    qrcode_b64 = auth_service.gerar_qrcode_base64(admin.totp_secret, admin.email)
    return templates.TemplateResponse("admin/setup_totp.html", {
        "request": request,
        "qrcode": qrcode_b64,
        "token": token
    })


@router.post("/admin/setup-totp")
def setup_totp_confirmar(
    request: Request,
    token: str = Form(...),
    codigo: str = Form(...),
    db: Session = Depends(get_db)
):
    payload = auth_service.verificar_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Token inválido")
    admin = db.query(Admin).filter(Admin.id == int(payload["sub"])).first()
    if not auth_service.verificar_totp(admin.totp_secret, codigo):
        qrcode_b64 = auth_service.gerar_qrcode_base64(admin.totp_secret, admin.email)
        return templates.TemplateResponse("admin/setup_totp.html", {
            "request": request,
            "qrcode": qrcode_b64,
            "token": token,
            "erro": "Código incorreto. Tente novamente."
        })
    admin.totp_ativo = True
    db.commit()
    return RedirectResponse(url="/admin/login?setup=ok", status_code=302)


@router.get("/admin/usuarios", response_class=HTMLResponse)
def listar_usuarios(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    usuarios = db.query(Admin).order_by(Admin.id).all()
    return templates.TemplateResponse("admin/usuarios/lista.html", {
        "request": request,
        "usuarios": usuarios,
        "admin_atual": admin,
    })


@router.get("/admin/usuarios/novo", response_class=HTMLResponse)
def novo_usuario_page(
    request: Request,
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    return templates.TemplateResponse("admin/usuarios/form.html", {
        "request": request,
        "usuario": None,
        "erro": None,
    })


@router.post("/admin/usuarios/novo")
def criar_usuario(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    confirmar_senha: str = Form(...),
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    if senha != confirmar_senha:
        return templates.TemplateResponse("admin/usuarios/form.html", {
            "request": request,
            "usuario": None,
            "erro": "As senhas não conferem.",
        }, status_code=400)

    if db.query(Admin).filter(Admin.email == email).first():
        return templates.TemplateResponse("admin/usuarios/form.html", {
            "request": request,
            "usuario": None,
            "erro": "Já existe um admin com esse e-mail.",
        }, status_code=400)

    novo = Admin(
        email=email,
        senha_hash=auth_service.hash_senha(senha),
        totp_ativo=False,
    )
    db.add(novo)
    db.commit()

    # Concede todas as permissoes por padrao, exceto usuarios e logs (superadmin only)
    for area, _ in AREAS_ADMIN:
        if area not in ("usuarios", "logs"):
            db.add(PermissaoAdmin(admin_id=novo.id, area=area))
    db.commit()

    log_acesso(db, acao="admin_criado", admin=admin, path="/admin/usuarios/novo", request=request, detalhes=f"Novo admin: {email}")
    return RedirectResponse(url="/admin/usuarios?ok=1", status_code=302)


@router.get("/admin/usuarios/{id}/editar", response_class=HTMLResponse)
def editar_usuario_page(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    usuario = db.query(Admin).filter(Admin.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("admin/usuarios/form.html", {
        "request": request,
        "usuario": usuario,
        "erro": None,
    })


@router.post("/admin/usuarios/{id}/editar")
def atualizar_usuario(
    id: int,
    request: Request,
    senha: str = Form(...),
    confirmar_senha: str = Form(...),
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    usuario = db.query(Admin).filter(Admin.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404)

    if senha != confirmar_senha:
        return templates.TemplateResponse("admin/usuarios/form.html", {
            "request": request,
            "usuario": usuario,
            "erro": "As senhas não conferem.",
        }, status_code=400)

    usuario.senha_hash = auth_service.hash_senha(senha)
    db.commit()
    log_acesso(db, acao="senha_alterada", admin=admin, path=f"/admin/usuarios/{id}/editar", request=request, detalhes=f"Admin: {usuario.email}")
    return RedirectResponse(url="/admin/usuarios?ok=1", status_code=302)


@router.post("/admin/usuarios/{id}/resetar-totp")
def resetar_totp(
    id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    usuario = db.query(Admin).filter(Admin.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404)
    usuario.totp_secret = None
    usuario.totp_ativo = False
    db.commit()
    log_acesso(db, acao="totp_resetado", admin=admin, path=f"/admin/usuarios/{id}/resetar-totp", request=request, detalhes=f"Admin: {usuario.email}")
    return RedirectResponse(url="/admin/usuarios?ok=1", status_code=302)


@router.post("/admin/usuarios/{id}/excluir")
def excluir_usuario(
    id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    usuario = db.query(Admin).filter(Admin.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404)
    if usuario.id == admin.id:
        return RedirectResponse(url="/admin/usuarios?erro=nao-pode-excluir-proprio", status_code=302)
    db.query(PermissaoAdmin).filter(PermissaoAdmin.admin_id == usuario.id).delete()
    db.query(DispositivoOtpExento).filter(DispositivoOtpExento.admin_id == usuario.id).delete()
    db.delete(usuario)
    db.commit()
    log_acesso(db, acao="admin_excluido", admin=admin, path=f"/admin/usuarios/{id}/excluir", request=request, detalhes=f"Admin: {usuario.email}")
    return RedirectResponse(url="/admin/usuarios?ok=1", status_code=302)


@router.get("/admin/usuarios/{id}/permissoes", response_class=HTMLResponse)
def permissoes_page(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    usuario = db.query(Admin).filter(Admin.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404)
    permissoes = {p.area for p in usuario.permissoes}
    return templates.TemplateResponse("admin/usuarios/permissoes.html", {
        "request": request,
        "usuario": usuario,
        "areas": AREAS_ADMIN,
        "permissoes": permissoes,
    })


@router.post("/admin/usuarios/{id}/permissoes-salvar")
async def salvar_permissoes_async(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    usuario = db.query(Admin).filter(Admin.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404)
    db.query(PermissaoAdmin).filter(PermissaoAdmin.admin_id == usuario.id).delete()
    form_data = await request.form()
    for chave in form_data.keys():
        if chave.startswith("area_"):
            area = chave[5:]
            if area not in ("usuarios", "logs"):
                db.add(PermissaoAdmin(admin_id=usuario.id, area=area))
    db.commit()
    log_acesso(db, acao="permissoes_alteradas", admin=admin, path=f"/admin/usuarios/{id}/permissoes", request=request, detalhes=f"Admin: {usuario.email}")
    return RedirectResponse(url=f"/admin/usuarios/{id}/permissoes?ok=1", status_code=302)


@router.get("/admin/usuarios/{id}/dispositivos", response_class=HTMLResponse)
def dispositivos_page(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    usuario = db.query(Admin).filter(Admin.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404)
    dispositivos = db.query(DispositivoOtpExento).filter(DispositivoOtpExento.admin_id == id).order_by(DispositivoOtpExento.id.desc()).all()
    return templates.TemplateResponse("admin/usuarios/dispositivos.html", {
        "request": request,
        "usuario": usuario,
        "dispositivos": dispositivos,
    })


@router.post("/admin/usuarios/{id}/dispositivos")
async def adicionar_dispositivo(
    id: int,
    request: Request,
    nome: str = Form(...),
    fingerprint: str = Form(""),
    device_token: str = Form(""),
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    usuario = db.query(Admin).filter(Admin.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404)
    if not fingerprint and not device_token:
        return RedirectResponse(url=f"/admin/usuarios/{id}/dispositivos?erro=1", status_code=302)
    disp = DispositivoOtpExento(
        admin_id=usuario.id,
        fingerprint=fingerprint or auth_service.get_fingerprint(request),
        device_token=device_token or None,
        nome=nome,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        ativo=True,
    )
    db.add(disp)
    db.commit()
    log_acesso(db, acao="dispositivo_otp_adicionado", admin=admin, path=f"/admin/usuarios/{id}/dispositivos", request=request, detalhes=f"Admin: {usuario.email}")
    return RedirectResponse(url=f"/admin/usuarios/{id}/dispositivos?ok=1", status_code=302)


@router.post("/admin/usuarios/{id}/dispositivos/{disp_id}/toggle")
def toggle_dispositivo(
    id: int,
    disp_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    disp = db.query(DispositivoOtpExento).filter(DispositivoOtpExento.id == disp_id, DispositivoOtpExento.admin_id == id).first()
    if not disp:
        raise HTTPException(status_code=404)
    disp.ativo = not disp.ativo
    db.commit()
    log_acesso(db, acao="dispositivo_otp_toggle", admin=admin, path=f"/admin/usuarios/{id}/dispositivos/{disp_id}/toggle", request=request, detalhes=f"Dispositivo {disp_id} ativo={disp.ativo}")
    return RedirectResponse(url=f"/admin/usuarios/{id}/dispositivos?ok=1", status_code=302)


@router.post("/admin/usuarios/{id}/dispositivos/{disp_id}/excluir")
def excluir_dispositivo(
    id: int,
    disp_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    disp = db.query(DispositivoOtpExento).filter(DispositivoOtpExento.id == disp_id, DispositivoOtpExento.admin_id == id).first()
    if not disp:
        raise HTTPException(status_code=404)
    db.delete(disp)
    db.commit()
    log_acesso(db, acao="dispositivo_otp_excluido", admin=admin, path=f"/admin/usuarios/{id}/dispositivos/{disp_id}/excluir", request=request, detalhes=f"Dispositivo {disp_id}")
    return RedirectResponse(url=f"/admin/usuarios/{id}/dispositivos?ok=1", status_code=302)


@router.post("/admin/logs/{log_id}/isentir")
def isentir_dispositivo_pelo_log(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    log = db.query(AcessoLog).filter(AcessoLog.id == log_id).first()
    if not log or not log.admin_id or not log.device_token:
        raise HTTPException(status_code=400, detail="Log inválido ou sem device token")

    existing = db.query(DispositivoOtpExento).filter_by(
        admin_id=log.admin_id, device_token=log.device_token
    ).first()
    if existing:
        existing.ativo = True
        existing.fingerprint = log.fingerprint
        existing.ip = log.ip
        existing.user_agent = log.user_agent
    else:
        db.add(DispositivoOtpExento(
            admin_id=log.admin_id,
            fingerprint=log.fingerprint,
            device_token=log.device_token,
            nome=f"Dispositivo isentado em {log.criado_em.strftime('%d/%m/%Y %H:%M') if log.criado_em else 'log'}",
            ip=log.ip,
            user_agent=log.user_agent,
            ativo=True,
        ))
    db.commit()
    log_acesso(db, acao="dispositivo_otp_isentado", admin=admin, path=f"/admin/logs/{log_id}/isentir", request=request, detalhes=f"Admin: {log.email}; token: {log.device_token}")
    return RedirectResponse(url="/admin/logs?ok=1", status_code=302)


@router.get("/admin/logs", response_class=HTMLResponse)
def logs_page(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(auth_service.get_admin_superadmin)
):
    logs = db.query(AcessoLog).order_by(AcessoLog.id.desc()).limit(500).all()
    return templates.TemplateResponse("admin/logs.html", {
        "request": request,
        "logs": logs,
    })
