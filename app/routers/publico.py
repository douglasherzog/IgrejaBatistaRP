from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("publico/index.html", {"request": request})


@router.get("/sobre", response_class=HTMLResponse)
def sobre(request: Request):
    return templates.TemplateResponse("publico/sobre.html", {"request": request})


@router.get("/cultos", response_class=HTMLResponse)
def cultos(request: Request):
    return templates.TemplateResponse("publico/cultos.html", {"request": request})


@router.get("/eventos", response_class=HTMLResponse)
def eventos(request: Request):
    return templates.TemplateResponse("publico/eventos.html", {"request": request})


@router.get("/contato", response_class=HTMLResponse)
def contato(request: Request):
    return templates.TemplateResponse("publico/contato.html", {"request": request})
