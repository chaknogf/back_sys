from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.nacimientos_legacy import NacimientoLegacy
from app.schemas.nacimientos_legacy import NacimientoLegacyBase, NacimientoLegacyResponse

router = APIRouter(prefix="/nacimientos-legacy", tags=["Nacimientos Legacy"])


@router.get("/", response_model=List[NacimientoLegacyResponse])
def listar_nacimientos(
    id: int | None = None,
    madre: str | None = None,
    doc: str | None = None,
    fecha: date | None = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(NacimientoLegacy)

    if id is not None:
        query = query.filter(NacimientoLegacy.id == id)

    if madre:
        query = query.filter(NacimientoLegacy.madre.ilike(f"%{madre}%"))

    if doc:
        query = query.filter(NacimientoLegacy.doc.ilike(f"%{doc}%"))

    if fecha:
        query = query.filter(NacimientoLegacy.fecha == fecha)

    limit = min(limit, 500)

    return (
        query
        .order_by(NacimientoLegacy.fecha.desc())
        .limit(limit)
        .all()
    )



@router.put("/{id}", response_model=NacimientoLegacyResponse)
def update_nacimiento(id: int, data: NacimientoLegacyBase, db: Session = Depends(get_db)):
    nacimiento = db.query(NacimientoLegacy).filter(NacimientoLegacy.id == id).first()
    if not nacimiento:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(nacimiento, key, value)

    db.commit()
    db.refresh(nacimiento)
    return nacimiento