from fastapi.templating import Jinja2Templates
from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo
from app.security import get_csrf_token
from app.auth import verificar_token
from app.database import SessionLocal
from app.models import Admin, PermissaoAdmin

TIMEZONE_SP = ZoneInfo("America/Sao_Paulo")


def localtime(value):
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(TIMEZONE_SP)
    return value


def sp_format(value, format_str="%d/%m/%Y %H:%M"):
    if value is None:
        return ""
    return localtime(value).strftime(format_str)


def get_cfg(request):
    return getattr(request.state, "cfg", {})


def tem_permissao(request, area):
    if not hasattr(request.state, "areas_admin_permitidas"):
        request.state.areas_admin_permitidas = set()
        token = request.cookies.get("session_token")
        payload = verificar_token(token) if token else None
        if not payload or not payload.get("sub"):
            return False
        db = SessionLocal()
        try:
            admin = db.query(Admin).filter(Admin.id == int(payload["sub"])).first()
            if admin:
                if admin.is_superadmin:
                    request.state.areas_admin_permitidas = None
                else:
                    request.state.areas_admin_permitidas = {
                        permissao.area
                        for permissao in db.query(PermissaoAdmin).filter_by(admin_id=admin.id).all()
                    }
        finally:
            db.close()
    return request.state.areas_admin_permitidas is None or area in request.state.areas_admin_permitidas


templates = Jinja2Templates(directory="templates")
templates.env.globals["get_cfg"] = get_cfg
templates.env.globals["tem_permissao"] = tem_permissao
templates.env.globals["get_csrf_token"] = get_csrf_token
templates.env.filters["localtime"] = localtime
templates.env.filters["sp_format"] = sp_format
