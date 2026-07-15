import os
import shutil
from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Foto, Admin
from app.auth import get_admin_atual
from app.routers.site import get_all_configs

router = APIRouter()


@router.get("/fotos", response_class=HTMLResponse)
def galeria_publica(
    request: Request,
    db: Session = Depends(get_db)
):
    configs = get_all_configs(db)
    fotos = db.query(Foto).filter(Foto.ativo == True).order_by(Foto.criado_em.desc()).all()
    albuns = sorted(set(f.album for f in fotos if f.album))
    return templates.TemplateResponse("publico/fotos.html", {
        "request": request,
        "cfg": configs,
        "fotos": fotos,
        "albuns": albuns,
    })


@router.get("/admin/fotos", response_class=HTMLResponse)
def listar_fotos(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    fotos = db.query(Foto).order_by(Foto.criado_em.desc()).all()
    return templates.TemplateResponse("admin/fotos/lista.html", {
        "request": request,
        "fotos": fotos,
    })


@router.get("/admin/fotos/novo", response_class=HTMLResponse)
def nova_foto_page(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    albuns = sorted(set(f.album for f in db.query(Foto).all() if f.album))
    return templates.TemplateResponse("admin/fotos/form.html", {
        "request": request,
        "foto": None,
        "albuns": albuns,
    })


@router.post("/admin/fotos/novo")
async def criar_foto(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    form = await request.form()
    arquivo = form.get("arquivo")
    imagem_url = form.get("imagem_url", "")
    if arquivo and hasattr(arquivo, "filename") and arquivo.filename:
        upload_dir = os.path.join("static", "img", "galeria")
        os.makedirs(upload_dir, exist_ok=True)
        ext = os.path.splitext(arquivo.filename)[1] or ".jpg"
        if ext.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
            ext = ".jpg"
        import uuid
        nome_arquivo = f"foto_{uuid.uuid4().hex[:8]}{ext}"
        dest = os.path.join(upload_dir, nome_arquivo)
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
        imagem_url = f"/static/img/galeria/{nome_arquivo}"
    if not imagem_url:
        return RedirectResponse(url="/admin/fotos/novo?erro=1", status_code=302)
    foto = Foto(
        titulo=form.get("titulo", ""),
        descricao=form.get("descricao", "") or None,
        imagem_url=imagem_url,
        album=form.get("album", "") or None,
        destaque=form.get("destaque") == "on",
        ativo=form.get("ativo") != "off",
    )
    db.add(foto)
    db.commit()
    return RedirectResponse(url="/admin/fotos", status_code=302)


@router.get("/admin/fotos/{id}/editar", response_class=HTMLResponse)
def editar_foto_page(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    foto = db.query(Foto).filter(Foto.id == id).first()
    if not foto:
        raise HTTPException(status_code=404)
    albuns = sorted(set(f.album for f in db.query(Foto).all() if f.album))
    return templates.TemplateResponse("admin/fotos/form.html", {
        "request": request,
        "foto": foto,
        "albuns": albuns,
    })


@router.post("/admin/fotos/{id}/editar")
async def atualizar_foto(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    foto = db.query(Foto).filter(Foto.id == id).first()
    if not foto:
        raise HTTPException(status_code=404)
    form = await request.form()
    foto.titulo = form.get("titulo", "")
    foto.descricao = form.get("descricao", "") or None
    foto.album = form.get("album", "") or None
    foto.destaque = form.get("destaque") == "on"
    foto.ativo = form.get("ativo") != "off"
    db.commit()
    return RedirectResponse(url="/admin/fotos", status_code=302)


@router.post("/admin/fotos/{id}/excluir")
def excluir_foto(
    id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    foto = db.query(Foto).filter(Foto.id == id).first()
    if not foto:
        raise HTTPException(status_code=404)
    db.delete(foto)
    db.commit()
    return RedirectResponse(url="/admin/fotos", status_code=302)
