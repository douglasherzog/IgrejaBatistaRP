from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import engine, Base, SessionLocal
from app.routers import publico, auth, membros, caixa, admin_dashboard, site, eventos, videos
from app.routers.site import get_all_configs

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


# Filtro global Jinja2: disponibiliza cfg em todos os templates
templates_instance = Jinja2Templates(directory="templates")
templates_instance.env.globals["get_cfg"] = lambda request: getattr(request.state, "cfg", {})


app.include_router(publico.router)
app.include_router(auth.router)
app.include_router(membros.router)
app.include_router(caixa.router)
app.include_router(admin_dashboard.router)
app.include_router(site.router)
app.include_router(eventos.router)
app.include_router(videos.router)
