import re
from contextvars import ContextVar
from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy.orm import Session

from .models import AuditLogModel

client_ip_var: ContextVar[str | None] = ContextVar("audit_client_ip", default=None)


def get_client_ip() -> str | None:
    return client_ip_var.get()


def registrar_acceso(
    db: Session,
    username: str,
    tabla: str,
    endpoint: str,
    registro_id: int | None = None,
    metodo: str = "GET",
    ip_address: str | None = None,
    so: str | None = None,
    nombre_equipo: str | None = None,
    user_agent: str | None = None,
):
    if ip_address is None:
        ip_address = get_client_ip()
    log = AuditLogModel(
        fecha_hora=datetime.now(timezone.utc),
        username=username,
        tabla=tabla,
        registro_id=registro_id,
        endpoint=endpoint,
        metodo=metodo,
        ip_address=ip_address,
        so=so,
        nombre_equipo=nombre_equipo,
        user_agent=user_agent,
    )
    db.add(log)
    db.commit()


_UA_SO_PATTERNS = (
    ("Windows", re.compile(r"Windows NT|Win(dows|32|64)", re.I)),
    ("Android", re.compile(r"Android", re.I)),
    ("iOS", re.compile(r"iPhone|iPad|iPod", re.I)),
    ("macOS", re.compile(r"Mac OS X|Macintosh", re.I)),
    ("Linux", re.compile(r"Linux", re.I)),
    ("Chrome OS", re.compile(r"CrOS|Chromium OS", re.I)),
)


def detectar_so(user_agent: str | None) -> str | None:
    if not user_agent:
        return None
    for nombre, patron in _UA_SO_PATTERNS:
        if patron.search(user_agent):
            return nombre
    return "desconocido"


def obtener_ip(request: Request) -> str | None:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else None