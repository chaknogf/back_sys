# modules/medicos/service.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from modules.medicos.models import MedicoModel
from modules.medicos.schemas import (
    MedicoCreate,
    MedicoUpdate,
    MedicoOut,
    MedicoListResponse,
)


def crear_medico(data: MedicoCreate, db: Session):
    medico = MedicoModel(**data.model_dump())
    db.add(medico)
    db.commit()
    db.refresh(medico)
    return medico


def listar_medicos(
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
    query = db.query(MedicoModel)

    if id is not None:
        query = query.filter(MedicoModel.id == id)
        medico = query.first()
        total = 1 if medico else 0
        return MedicoListResponse(
            total=total,
            medicos=[medico] if medico else []
        )

    if activo is not None:
        query = query.filter(MedicoModel.activo == activo)

    if nombre:
        query = query.filter(MedicoModel.nombre.ilike(f"%{nombre}%"))

    if colegiado:
        query = query.filter(MedicoModel.colegiado.ilike(f"%{colegiado}%"))

    if pasaporte:
        query = query.filter(MedicoModel.pasaporte.ilike(f"%{pasaporte}%"))

    if especialidad:
        query = query.filter(MedicoModel.especialidad.ilike(f"%{especialidad}%"))
    if especialidad_id is not None:
        query = query.filter(MedicoModel.especialidad_id == especialidad_id)

    total = query.count()

    medicos = (
        query
        .order_by(MedicoModel.nombre)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return MedicoListResponse(total=total, medicos=medicos)


def obtener_medico(medico_id: int, db: Session):
    medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()

    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    return medico


def actualizar_medico(medico_id: int, data: MedicoUpdate, db: Session):
    medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()

    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(medico, key, value)

    db.commit()
    db.refresh(medico)

    return medico


def eliminar_medico(medico_id: int, db: Session):
    medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()

    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    try:
        db.delete(medico)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el médico porque está relacionado con otros registros"
        )

    return None
