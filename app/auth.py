import os
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Admin

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
    admin = db.query(Admin).filter(Admin.id == payload.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return admin
