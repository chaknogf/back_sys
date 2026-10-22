"""Operaciones del catálogo de personal de atención médica."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from modules.personal_atencion.models import PersonalAtencionModel
from modules.personal_atencion.schemas import (
    PersonalAtencionCreate,
    PersonalAtencionUpdate,
    PersonalAtencionOut,
    PersonalAtencionListResponse,
)


def crear_personal_atencion(data: PersonalAtencionCreate, db: Session):
    personal = PersonalAtencionModel(**data.model_dump())
    db.add(personal)
    db.commit()
    db.refresh(personal)
    return personal


def listar_personal_atencion(
    db: Session,
    id: int | None = None,
    activo: bool | None = None,
    nombre: str | None = None,
    colegiado: str | None = None,
    pasaporte: str | None = None,
    especialidad: str | None = None,
    especialidad_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
):
    """Busca personal de atención con filtros opcionales y devuelve conteo junto con la página."""
    query = db.query(PersonalAtencionModel)

    if id is not None:
        query = query.filter(PersonalAtencionModel.id == id)
        personal = query.first()
        total = 1 if personal else 0
        return PersonalAtencionListResponse(
            total=total,
            personal_atencion=[personal] if personal else []
        )

    if activo is not None:
        query = query.filter(PersonalAtencionModel.activo == activo)

    if nombre:
        query = query.filter(PersonalAtencionModel.nombre.ilike(f"%{nombre}%"))

    if colegiado:
        query = query.filter(PersonalAtencionModel.colegiado.ilike(f"%{colegiado}%"))

    if pasaporte:
        query = query.filter(PersonalAtencionModel.pasaporte.ilike(f"%{pasaporte}%"))

    if especialidad_id is not None:
        query = query.filter(PersonalAtencionModel.especialidad_id == especialidad_id)

    total = query.count()

    personal_atencion = (
        query
        .order_by(PersonalAtencionModel.nombre)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return PersonalAtencionListResponse(total=total, personal_atencion=personal_atencion)


def obtener_personal_atencion(personal_atencion_id: int, db: Session):
    personal = db.query(PersonalAtencionModel).filter(PersonalAtencionModel.id == personal_atencion_id).first()

    if not personal:
        raise HTTPException(status_code=404, detail="Personal de atención no encontrado")

    return personal


def actualizar_personal_atencion(personal_atencion_id: int, data: PersonalAtencionUpdate, db: Session):
    personal = db.query(PersonalAtencionModel).filter(PersonalAtencionModel.id == personal_atencion_id).first()

    if not personal:
        raise HTTPException(status_code=404, detail="Personal de atención no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(personal, key, value)

    db.commit()
    db.refresh(personal)

    return personal


def eliminar_personal_atencion(personal_atencion_id: int, db: Session):
    """Elimina el registro si no tiene referencias; revierte la sesión si falla la FK."""
    personal = db.query(PersonalAtencionModel).filter(PersonalAtencionModel.id == personal_atencion_id).first()

    if not personal:
        raise HTTPException(status_code=404, detail="Personal de atención no encontrado")

    try:
        db.delete(personal)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el personal de atención porque está relacionado con otros registros"
        )

    return None
