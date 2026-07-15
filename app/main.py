from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse
from app.database import engine, Base, SessionLocal
from app.routers import publico, auth, membros, caixa, admin_dashboard, site, eventos, videos, oracao, inscricoes, fotos, relatorios, importar
from app.routers.site import get_all_configs
from app.security import CSRFMiddleware, get_csrf_token
from app.auth import verificar_token, area_do_path
from app.models import Admin, PermissaoAdmin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Igreja Batista Nova Vida - Rio Pardo/RS", docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")


# Middleware: injeta configurações do site em todos os templates
class ConfigSiteMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        db = SessionLocal()
        try:
            request.state.cfg = get_all_configs(db)
        finally:
            db.close()
        response = await call_next(request)
        return response


app.add_middleware(ConfigSiteMiddleware)


# Middleware: verifica permissões de acesso ao painel admin
class PermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        area = area_do_path(request.url.path)
        if area:
            token = request.cookies.get("session_token")
            admin = None
            if token:
                payload = verificar_token(token)
                if payload:
                    db = SessionLocal()
                    try:
                        admin_id = int(payload.get("sub")) if payload.get("sub") else None
                        admin = db.query(Admin).filter(Admin.id == admin_id).first()
                    finally:
                        db.close()
            if admin and not admin.is_superadmin:
                db = SessionLocal()
                try:
                    permissao = db.query(PermissaoAdmin).filter_by(admin_id=admin.id, area=area).first()
                    if not permissao:
                        return PlainTextResponse("Acesso negado", status_code=403)
                finally:
                    db.close()
        return await call_next(request)


app.add_middleware(PermissionMiddleware)


# Filtro global Jinja2: disponibiliza cfg e helpers em todos os templates
templates_instance = Jinja2Templates(directory="templates")
templates_instance.env.globals["get_cfg"] = lambda request: getattr(request.state, "cfg", {})
templates_instance.env.globals["get_csrf_token"] = get_csrf_token


app.include_router(publico.router)
app.include_router(auth.router)
app.include_router(membros.router)
app.include_router(caixa.router)
app.include_router(admin_dashboard.router)
app.include_router(site.router)
app.include_router(eventos.router)
app.include_router(videos.router)
app.include_router(oracao.router)
app.include_router(inscricoes.router)
app.include_router(fotos.router)
app.include_router(relatorios.router)
app.include_router(importar.router)

# Middleware CSRF para proteção contra ataques
app.add_middleware(CSRFMiddleware)
