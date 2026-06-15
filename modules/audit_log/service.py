from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .models import AuditLogModel


def registrar_acceso(
    db: Session,
    username: str,
    tabla: str,
    endpoint: str,
    registro_id: int | None = None,
    metodo: str = "GET",
):
    log = AuditLogModel(
        fecha_hora=datetime.now(timezone.utc),
        username=username,
        tabla=tabla,
        registro_id=registro_id,
        endpoint=endpoint,
        metodo=metodo,
    )
    db.add(log)
    db.commit()
