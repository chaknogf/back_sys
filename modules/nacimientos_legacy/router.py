"""Acceso de compatibilidad al catálogo histórico de nacimientos importados."""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, get_current_admin_user
from modules.nacimientos_legacy.models import NacimientoLegacy
from modules.nacimientos_legacy.schemas import NacimientoLegacyBase, NacimientoLegacyResponse

router = APIRouter(
    prefix="/nacimientos-legacy",
    tags=["Nacimientos Legacy"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=List[NacimientoLegacyResponse])
def listar_nacimientos(
    id: int | None = None,
    madre: str | None = None,
    doc: str | None = None,
    fecha: date | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Filtra registros originales y limita la lectura a 500 filas por solicitud."""
    query = db.query(NacimientoLegacy)

    if id is not None:
        query = query.filter(NacimientoLegacy.id == id)

    if madre:
        query = query.filter(NacimientoLegacy.madre.ilike(f"%{madre}%"))

    if doc:
        query = query.filter(NacimientoLegacy.doc.ilike(f"%{doc}%"))

    if fecha:
        query = query.filter(NacimientoLegacy.fecha == fecha)

    return (
        query
        .order_by(NacimientoLegacy.fecha.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )



@router.put("/{id}", response_model=NacimientoLegacyResponse)
def update_nacimiento(
    id: int,
    data: NacimientoLegacyBase,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    """Actualiza campos explícitos sin convertir el registro al modelo vigente."""
    nacimiento = db.query(NacimientoLegacy).filter(NacimientoLegacy.id == id).first()
    if not nacimiento:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(nacimiento, key, value)

    db.commit()
    db.refresh(nacimiento)
    return nacimiento
