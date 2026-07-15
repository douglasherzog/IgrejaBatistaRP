from fastapi.templating import Jinja2Templates
from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo
from app.security import get_csrf_token

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


templates = Jinja2Templates(directory="templates")
templates.env.globals["get_cfg"] = get_cfg
templates.env.globals["get_csrf_token"] = get_csrf_token
templates.env.filters["localtime"] = localtime
templates.env.filters["sp_format"] = sp_format
