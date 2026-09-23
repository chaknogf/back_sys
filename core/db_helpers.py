"""Funciones utilitarias compartidas para ejecución de queries SQLAlchemy."""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


def fetchone(db: Session, sql: str, params: Optional[dict] = None) -> Optional[dict]:
    """Ejecuta una query SQL y devuelve un dict o None."""
    r = db.execute(text(sql), params or {}).mappings().first()
    return dict(r) if r else None


def fetchall(db: Session, sql: str, params: Optional[dict] = None) -> List[dict]:
    """Ejecuta una query SQL y devuelve una lista de dicts."""
    return [dict(r) for r in db.execute(text(sql), params or {}).mappings().all()]
