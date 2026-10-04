"""Servicios para el catálogo maestro de procedimientos y áreas."""

from typing import List, Optional
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from modules.catalogo_procedimientos.models import (
    CatalogoProcedimiento,
    AreaCuerpoIntervenida,
)


# ────────────────────────── CATÁLOGO ──────────────────────────

def listar_catalogo(
    db: Session,
    q: Optional[str] = None,
    especialidad_ref: Optional[int] = None,
    activo: Optional[bool] = True,
    skip: int = 0,
    limit: int = 5000,
) -> List[CatalogoProcedimiento]:
    query = db.query(CatalogoProcedimiento)
    if activo is not None:
        query = query.filter(CatalogoProcedimiento.activo == activo)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            CatalogoProcedimiento.nombre.ilike(like),
            CatalogoProcedimiento.abreviatura.ilike(like),
        ))
    if especialidad_ref is not None:
        query = query.filter(CatalogoProcedimiento.especialidad_ref == especialidad_ref)
    return query.order_by(CatalogoProcedimiento.nombre).offset(skip).limit(limit).all()


def obtener_catalogo(cat_id: int, db: Session) -> CatalogoProcedimiento:
    from fastapi import HTTPException
    reg = db.query(CatalogoProcedimiento).filter(CatalogoProcedimiento.id == cat_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Procedimiento de catálogo no encontrado")
    return reg


def crear_catalogo(data, db: Session) -> CatalogoProcedimiento:
    from fastapi import HTTPException
    existente = db.query(CatalogoProcedimiento).filter(
        CatalogoProcedimiento.nombre == data.nombre
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un procedimiento con ese nombre")
    reg = CatalogoProcedimiento(**data.model_dump())
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar_catalogo(cat_id: int, data, db: Session) -> CatalogoProcedimiento:
    reg = obtener_catalogo(cat_id, db)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(reg, k, v)
    db.commit()
    db.refresh(reg)
    return reg


def eliminar_catalogo(cat_id: int, db: Session) -> dict:
    from fastapi import HTTPException
    reg = obtener_catalogo(cat_id, db)
    # Soft delete: desactivar
    reg.activo = False
    db.commit()
    return {"message": "Procedimiento desactivado", "id": reg.id}


# ────────────────────────── ÁREAS ──────────────────────────

def listar_areas(db: Session, activo: Optional[bool] = True) -> List[AreaCuerpoIntervenida]:
    query = db.query(AreaCuerpoIntervenida)
    if activo is not None:
        query = query.filter(AreaCuerpoIntervenida.activo == activo)
    return query.order_by(AreaCuerpoIntervenida.nombre).all()


def obtener_area(area_id: int, db: Session) -> AreaCuerpoIntervenida:
    from fastapi import HTTPException
    reg = db.query(AreaCuerpoIntervenida).filter(AreaCuerpoIntervenida.id == area_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Área del cuerpo no encontrada")
    return reg


def crear_area(data, db: Session) -> AreaCuerpoIntervenida:
    from fastapi import HTTPException
    existente = db.query(AreaCuerpoIntervenida).filter(
        AreaCuerpoIntervenida.codigo == data.codigo
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un área con ese código")
    reg = AreaCuerpoIntervenida(**data.model_dump())
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar_area(area_id: int, data, db: Session) -> AreaCuerpoIntervenida:
    reg = obtener_area(area_id, db)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(reg, k, v)
    db.commit()
    db.refresh(reg)
    return reg


def eliminar_area(area_id: int, db: Session) -> dict:
    reg = obtener_area(area_id, db)
    reg.activo = False
    db.commit()
    return {"message": "Área desactivada", "id": reg.id}