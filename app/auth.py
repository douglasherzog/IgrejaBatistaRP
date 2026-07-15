import os
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Cookie, Request
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app.database import get_db
from app.models import Admin, PermissaoAdmin

load_dotenv(override=True)
SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta-troque-em-producao")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8
TOTP_ISSUER = os.getenv("TOTP_ISSUER", "IgrejaBatistaNovaVida")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash: str) -> bool:
    return pwd_context.verify(senha, hash)


def criar_token(data: dict) -> str:
    payload = data.copy()
    if "sub" in payload:
        payload["sub"] = str(payload["sub"])
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def gerar_totp_secret() -> str:
    return pyotp.random_base32()


def gerar_qrcode_base64(secret: str, email: str) -> str:
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=email, issuer_name=TOTP_ISSUER)
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def verificar_totp(secret: str, codigo: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(codigo, valid_window=1)


def get_admin_atual(
    session_token: str = Cookie(default=None),
    db: Session = Depends(get_db)
) -> Admin:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
    payload = verificar_token(session_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida")
    admin = db.query(Admin).filter(Admin.id == int(payload.get("sub"))).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return admin


def area_do_path(path: str) -> str:
    """Extrai a area administrativa do path. Retorna None para rotas publicas/auth."""
    if not path.startswith("/admin/"):
        return None
    partes = path.strip("/").split("/")
    if len(partes) < 2:
        return None
    area = partes[1]
    # Rotas de autenticacao nao precisam de permissao
    if area in ("login", "logout", "totp", "setup-totp"):
        return None
    return area


def get_area_permissao(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
) -> Admin:
    if admin.is_superadmin:
        return admin
    area = area_do_path(request.url.path)
    if not area:
        return admin
    permissao = db.query(PermissaoAdmin).filter_by(admin_id=admin.id, area=area).first()
    if not permissao:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return admin


def get_admin_superadmin(
    admin: Admin = Depends(get_admin_atual)
) -> Admin:
    if not admin.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito ao administrador principal")
    return admin


def get_fingerprint(request: Request) -> str:
    import hashlib
    user_agent = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else ""
    return hashlib.sha256(f"{user_agent}|{ip}".encode()).hexdigest()


def dispositivo_otp_exento(db: Session, admin_id: int, request: Request) -> bool:
    from app.models import DispositivoOtpExento
    device_token = request.cookies.get("device_token")
    if device_token:
        if db.query(DispositivoOtpExento).filter_by(
            admin_id=admin_id, device_token=device_token, ativo=True
        ).first():
            return True
    fp = get_fingerprint(request)
    return db.query(DispositivoOtpExento).filter_by(
        admin_id=admin_id, fingerprint=fp, ativo=True
    ).first() is not None


def gerar_device_token() -> str:
    import secrets
    return secrets.token_urlsafe(32)
