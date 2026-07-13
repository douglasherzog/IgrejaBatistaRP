import secrets
from typing import Optional
from fastapi import Request, Cookie, Form, HTTPException
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware para proteção CSRF - Versão Simplificada"""
    
    def __init__(self, app, secret_key: str = None):
        super().__init__(app)
        self.secret_key = secret_key or secrets.token_urlsafe(32)
    
    async def dispatch(self, request: Request, call_next):
        # Gerar token CSRF para requisições GET
        if request.method == "GET":
            token = self.generate_csrf_token()
            request.state.csrf_token = token
            response = await call_next(request)
            response.set_cookie(
                key="csrf_token",
                value=token,
                httponly=True,
                secure=False,  # Mudar para True em produção com HTTPS
                samesite="strict",
                max_age=3600
            )
            return response
        
        # Manter token disponível em request.state para requisições de escrita
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            if "/admin/" in str(request.url):
                return await call_next(request)
            token = request.cookies.get("csrf_token")
            if token:
                request.state.csrf_token = token

        return await call_next(request)
    
    def generate_csrf_token(self) -> str:
        """Gera um token CSRF seguro"""
        return secrets.token_urlsafe(32)

def get_csrf_token(request: Request) -> str:
    """Obtém o token CSRF da requisição"""
    return getattr(request.state, "csrf_token", None) or request.cookies.get("csrf_token", "")


async def csrf_valid(
    request: Request,
    csrf_token: Optional[str] = Form(None),
    cookie_token: Optional[str] = Cookie(None, alias="csrf_token"),
):
    """Dependência FastAPI para validar CSRF em formulários públicos."""
    if not cookie_token or not csrf_token or cookie_token != csrf_token:
        raise HTTPException(status_code=403, detail="CSRF token inválido")
    return True
