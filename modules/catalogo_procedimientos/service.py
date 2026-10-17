"""Servicios para el catálogo maestro de procedimientos y áreas."""

from typing import List, Optional
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from modules.catalogo_procedimientos.models import (
    CatalogoProcedimiento,
    AreaCuerpoIntervenida,
)
from modules.procedimientos.models import CatalogoProcedimientoEspecialidad


# ────────────────────────── CATÁLOGO ──────────────────────────

def _adjuntar_especialidades(db: Session, regs: List[CatalogoProcedimiento]) -> List[CatalogoProcedimiento]:
    """Carga `especialidades_ids` en cada procedimiento con una sola consulta."""
    mapa: dict = {}
    ids = [r.id for r in regs if r is not None]
    if ids:
        filas = db.query(CatalogoProcedimientoEspecialidad).filter(
            CatalogoProcedimientoEspecialidad.id_catalogo_procedimiento.in_(ids)
        ).all()
        for fila in filas:
            mapa.setdefault(fila.id_catalogo_procedimiento, []).append(fila.id_especialidad)
    for r in regs:
        if r is not None:
            r.especialidades_ids = sorted(mapa.get(r.id, []))
    return regs


def _sincronizar_especialidades(db: Session, cat_id: int, especialidades: Optional[List[int]]) -> None:
    """Reemplaza las especialidades habilitadas de un procedimiento."""
    db.query(CatalogoProcedimientoEspecialidad).filter(
        CatalogoProcedimientoEspecialidad.id_catalogo_procedimiento == cat_id
    ).delete(synchronize_session=False)
    vistos = set()
    for esp_id in especialidades or []:
        if esp_id is None or esp_id in vistos:
            continue
        vistos.add(esp_id)
        db.add(CatalogoProcedimientoEspecialidad(
            id_catalogo_procedimiento=cat_id,
            id_especialidad=esp_id,
        ))


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
        sub = db.query(CatalogoProcedimientoEspecialidad.id_catalogo_procedimiento).filter(
            CatalogoProcedimientoEspecialidad.id_especialidad == especialidad_ref
        )
        query = query.filter(CatalogoProcedimiento.id.in_(sub))
    regs = query.order_by(CatalogoProcedimiento.nombre).offset(skip).limit(limit).all()
    return _adjuntar_especialidades(db, regs)


def obtener_catalogo(cat_id: int, db: Session) -> CatalogoProcedimiento:
    from fastapi import HTTPException
    reg = db.query(CatalogoProcedimiento).filter(CatalogoProcedimiento.id == cat_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Procedimiento de catálogo no encontrado")
    _adjuntar_especialidades(db, [reg])
    return reg


def crear_catalogo(data, db: Session) -> CatalogoProcedimiento:
    from fastapi import HTTPException
    existente = db.query(CatalogoProcedimiento).filter(
        CatalogoProcedimiento.nombre == data.nombre
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un procedimiento con ese nombre")
    payload = data.model_dump()
    especialidades = payload.pop("especialidades_ids", None)
    if especialidades is not None:
        payload["especialidad_ref"] = especialidades[0] if especialidades else None
    reg = CatalogoProcedimiento(**payload)
    db.add(reg)
    db.flush()
    if especialidades is None:
        especialidades = [reg.especialidad_ref] if reg.especialidad_ref is not None else []
    _sincronizar_especialidades(db, reg.id, especialidades)
    db.commit()
    db.refresh(reg)
    return _adjuntar_especialidades(db, [reg])[0]


def actualizar_catalogo(cat_id: int, data, db: Session) -> CatalogoProcedimiento:
    reg = obtener_catalogo(cat_id, db)
    cambios = data.model_dump(exclude_unset=True)
    especialidades = cambios.pop("especialidades_ids", None)
    for k, v in cambios.items():
        setattr(reg, k, v)
    if especialidades is not None:
        reg.especialidad_ref = especialidades[0] if especialidades else None
        _sincronizar_especialidades(db, reg.id, especialidades)
    elif "especialidad_ref" in cambios:
        lista = [cambios["especialidad_ref"]] if cambios["especialidad_ref"] is not None else []
        _sincronizar_especialidades(db, reg.id, lista)
    db.commit()
    db.refresh(reg)
    return _adjuntar_especialidades(db, [reg])[0]


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