from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Admin
from app import auth as auth_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")


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
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "erro": "Email ou senha incorretos"}
        )
    if not admin.totp_ativo:
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "erro": "Configure o autenticador antes de fazer login"}
        )
    token_temp = auth_service.criar_token({"sub": admin.id, "etapa": "totp"})
    resp = RedirectResponse(url="/admin/totp", status_code=302)
    resp.set_cookie("totp_token", token_temp, httponly=True, max_age=300)
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
        return templates.TemplateResponse(
            "admin/totp.html",
            {"request": request, "erro": "Código inválido ou expirado"}
        )
    token = auth_service.criar_token({"sub": admin.id})
    resp = RedirectResponse(url="/admin/dashboard", status_code=302)
    resp.set_cookie("session_token", token, httponly=True, max_age=3600 * 8)
    resp.delete_cookie("totp_token")
    return resp


@router.get("/admin/logout")
def logout():
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
