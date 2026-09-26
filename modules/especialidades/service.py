"""Gestión del catálogo de especialidades con unicidad y protección referencial."""

from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from .models import EspecialidadModel
from .schemas import EspecialidadCreate, EspecialidadUpdate


def listar(
    db: Session,
    estado: Optional[bool] = None,
    sop: Optional[bool] = None,
) -> list:
    query = db.query(EspecialidadModel)
    if estado is not None:
        query = query.filter(EspecialidadModel.estado == estado)
    if sop is not None:
        query = query.filter(EspecialidadModel.sop == sop)
    return query.order_by(EspecialidadModel.nombre).all()


def obtener(esp_id: int, db: Session) -> EspecialidadModel:
    reg = db.query(EspecialidadModel).filter(EspecialidadModel.id == esp_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada")
    return reg


def _verificar_unicos(
    db: Session,
    nombre: Optional[str] = None,
    abreviatura: Optional[str] = None,
    codigo: Optional[str] = None,
    exclude_id: Optional[int] = None,
):
    """Rechaza nombre, abreviatura o código ya asignados a otra especialidad."""
    checks = [
        (EspecialidadModel.nombre, nombre, "nombre"),
        (EspecialidadModel.abreviatura, abreviatura, "abreviatura"),
        (EspecialidadModel.codigo, codigo, "codigo"),
    ]
    for col, valor, etiqueta in checks:
        if not valor:
            continue
        query = db.query(EspecialidadModel).filter(col == valor)
        if exclude_id is not None:
            query = query.filter(EspecialidadModel.id != exclude_id)
        if query.first():
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe una especialidad con {etiqueta} '{valor}'",
            )


def crear(data: EspecialidadCreate, db: Session) -> EspecialidadModel:
    _verificar_unicos(
        db,
        nombre=data.nombre,
        abreviatura=data.abreviatura,
        codigo=data.codigo,
    )
    reg = EspecialidadModel(
        nombre=data.nombre,
        abreviatura=data.abreviatura,
        codigo=data.codigo,
        estado=data.estado,
        sop=data.sop,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar(esp_id: int, data: EspecialidadUpdate, db: Session) -> EspecialidadModel:
    reg = obtener(esp_id, db)
    _verificar_unicos(
        db,
        nombre=data.nombre,
        abreviatura=data.abreviatura,
        codigo=data.codigo,
        exclude_id=esp_id,
    )
    if data.nombre is not None:
        reg.nombre = data.nombre
    if data.abreviatura is not None:
        reg.abreviatura = data.abreviatura
    if data.codigo is not None:
        reg.codigo = data.codigo
    if data.estado is not None:
        reg.estado = data.estado
    if data.sop is not None:
        reg.sop = data.sop
    db.commit()
    db.refresh(reg)
    return reg


def eliminar(esp_id: int, db: Session) -> dict:
    """Devuelve conflicto si hay registros que todavía referencian la especialidad."""
    reg = obtener(esp_id, db)
    try:
        db.delete(reg)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: la especialidad está referenciada por otros registros",
        )
    return {"eliminado": True}
