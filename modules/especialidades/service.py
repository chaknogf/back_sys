from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .models import EspecialidadModel
from .schemas import EspecialidadCreate, EspecialidadUpdate


def listar(db: Session) -> list:
    return db.query(EspecialidadModel).order_by(EspecialidadModel.nombre).all()


def obtener(esp_id: int, db: Session) -> EspecialidadModel:
    reg = db.query(EspecialidadModel).filter(EspecialidadModel.id == esp_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada")
    return reg


def crear(data: EspecialidadCreate, db: Session) -> EspecialidadModel:
    existente = db.query(EspecialidadModel).filter(
        EspecialidadModel.nombre == data.nombre
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail=f"'{data.nombre}' ya existe")
    reg = EspecialidadModel(nombre=data.nombre, abreviatura=data.abreviatura)
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar(esp_id: int, data: EspecialidadUpdate, db: Session) -> EspecialidadModel:
    reg = obtener(esp_id, db)
    if data.nombre is not None:
        reg.nombre = data.nombre
    if data.abreviatura is not None:
        reg.abreviatura = data.abreviatura
    db.commit()
    db.refresh(reg)
    return reg


def eliminar(esp_id: int, db: Session) -> dict:
    reg = obtener(esp_id, db)
    db.delete(reg)
    db.commit()
    return {"eliminado": True}
