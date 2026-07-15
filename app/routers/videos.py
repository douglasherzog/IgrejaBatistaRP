import re
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Video, Admin
from app.auth import get_admin_atual

router = APIRouter()


def extrair_youtube_id(url: str) -> str:
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([A-Za-z0-9_-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return ""


@router.get("/admin/videos", response_class=HTMLResponse)
def listar_videos(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    videos = db.query(Video).order_by(Video.criado_em.desc()).all()
    return templates.TemplateResponse("admin/videos/lista.html", {
        "request": request,
        "videos": videos,
    })


@router.get("/admin/videos/novo", response_class=HTMLResponse)
def novo_video_page(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    return templates.TemplateResponse("admin/videos/form.html", {
        "request": request,
        "video": None,
    })


@router.post("/admin/videos/novo")
async def criar_video(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    form = await request.form()
    url = form.get("youtube_url", "")
    video = Video(
        titulo=form.get("titulo", ""),
        descricao=form.get("descricao", "") or None,
        youtube_url=url,
        youtube_id=extrair_youtube_id(url),
        destaque=form.get("destaque") == "on",
        ativo=form.get("ativo") != "off",
    )
    db.add(video)
    db.commit()
    return RedirectResponse(url="/admin/videos", status_code=302)


@router.get("/admin/videos/{id}/editar", response_class=HTMLResponse)
def editar_video_page(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    video = db.query(Video).filter(Video.id == id).first()
    if not video:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("admin/videos/form.html", {
        "request": request,
        "video": video,
    })


@router.post("/admin/videos/{id}/editar")
async def atualizar_video(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    video = db.query(Video).filter(Video.id == id).first()
    if not video:
        raise HTTPException(status_code=404)
    form = await request.form()
    url = form.get("youtube_url", "")
    video.titulo = form.get("titulo", "")
    video.descricao = form.get("descricao", "") or None
    video.youtube_url = url
    video.youtube_id = extrair_youtube_id(url)
    video.destaque = form.get("destaque") == "on"
    video.ativo = form.get("ativo") != "off"
    db.commit()
    return RedirectResponse(url="/admin/videos", status_code=302)


@router.post("/admin/videos/{id}/excluir")
def excluir_video(
    id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    video = db.query(Video).filter(Video.id == id).first()
    if not video:
        raise HTTPException(status_code=404)
    db.delete(video)
    db.commit()
    return RedirectResponse(url="/admin/videos", status_code=302)
