from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import publico, auth, membros, caixa, admin_dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Igreja Batista Nova Vida - Rio Pardo/RS", docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(publico.router)
app.include_router(auth.router)
app.include_router(membros.router)
app.include_router(caixa.router)
app.include_router(admin_dashboard.router)
