from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from .models import AuditLogModel

router = APIRouter(prefix="/audit-log", tags=["Auditoría"])


@router.get("/")
def listar_logs(
    tabla: Optional[str] = Query(None, description="Filtrar por tabla (ej: pacientes, consultas)"),
    username: Optional[str] = Query(None, description="Filtrar por usuario"),
    desde: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    query = db.query(AuditLogModel).order_by(desc(AuditLogModel.fecha_hora))

    if tabla:
        query = query.filter(AuditLogModel.tabla == tabla)
    if username:
        query = query.filter(AuditLogModel.username.ilike(f"%{username}%"))
    if desde:
        try:
            f_desde = datetime.strptime(desde, "%Y-%m-%d")
            query = query.filter(AuditLogModel.fecha_hora >= f_desde)
        except ValueError:
            pass
    if hasta:
        try:
            f_hasta = datetime.strptime(hasta, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(AuditLogModel.fecha_hora <= f_hasta)
        except ValueError:
            pass

    total = query.count()
    logs = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "logs": [
            {
                "id": l.id,
                "fecha_hora": l.fecha_hora.isoformat(),
                "username": l.username,
                "tabla": l.tabla,
                "registro_id": l.registro_id,
                "endpoint": l.endpoint,
                "metodo": l.metodo,
            }
            for l in logs
        ],
    }
