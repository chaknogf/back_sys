from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .models import PersonalSaludModel


def obtener_personal_salud(ps_id: int, db: Session) -> PersonalSaludModel:
    registro = db.query(PersonalSaludModel).filter(PersonalSaludModel.id == ps_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de personal_salud no encontrado")
    return registro


def listar_personal_salud(db: Session) -> list:
    return db.query(PersonalSaludModel).order_by(PersonalSaludModel.nombre).all()


def crear_personal_salud(nombre: str, especialidad_id: int | None, medico_id: int | None, db: Session) -> PersonalSaludModel:
    existente = db.query(PersonalSaludModel).filter(PersonalSaludModel.nombre == nombre).first()
    if existente:
        raise HTTPException(status_code=409, detail=f"'{nombre}' ya existe en personal_salud")
    registro = PersonalSaludModel(nombre=nombre, especialidad_id=especialidad_id, medico_id=medico_id)
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


def actualizar_personal_salud(ps_id: int, nombre: str | None, especialidad_id: int | None, medico_id: int | None, db: Session) -> PersonalSaludModel:
    registro = db.query(PersonalSaludModel).filter(PersonalSaludModel.id == ps_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de personal_salud no encontrado")
    if nombre is not None:
        registro.nombre = nombre
    if especialidad_id is not None:
        registro.especialidad_id = especialidad_id
    if medico_id is not None:
        registro.medico_id = medico_id
    db.commit()
    db.refresh(registro)
    return registro


def eliminar_personal_salud(ps_id: int, db: Session) -> dict:
    registro = db.query(PersonalSaludModel).filter(PersonalSaludModel.id == ps_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de personal_salud no encontrado")
    db.delete(registro)
    db.commit()
    return {"eliminado": True}
