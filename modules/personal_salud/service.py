"""Gestión del catálogo de nombres de personal usados en SIGSA-3."""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .models import PersonalSaludModel


def obtener_personal_salud(ps_id: int, db: Session) -> PersonalSaludModel:
    registro = db.query(PersonalSaludModel).filter(PersonalSaludModel.id == ps_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de personal_salud no encontrado")
    return registro


def listar_personal_salud(
    db: Session,
    nombre: str | None = None,
    especialidad_id: int | None = None,
    personal_atencion_id: int | None = None,
) -> list:
    """Filtra el catálogo por nombre, especialidad o vínculo al personal de atención."""
    query = db.query(PersonalSaludModel)
    if nombre:
        query = query.filter(PersonalSaludModel.nombre.ilike(f"%{nombre}%"))
    if especialidad_id is not None:
        query = query.filter(PersonalSaludModel.especialidad_id == especialidad_id)
    if personal_atencion_id is not None:
        query = query.filter(PersonalSaludModel.personal_atencion_id == personal_atencion_id)
    return query.order_by(PersonalSaludModel.nombre).all()


def crear_personal_salud(nombre: str, especialidad_id: int | None, personal_atencion_id: int | None, db: Session) -> PersonalSaludModel:
    """Rechaza nombres ya existentes para evitar duplicados en el catálogo."""
    existente = db.query(PersonalSaludModel).filter(PersonalSaludModel.nombre == nombre).first()
    if existente:
        raise HTTPException(status_code=409, detail=f"'{nombre}' ya existe en personal_salud")
    registro = PersonalSaludModel(nombre=nombre, especialidad_id=especialidad_id, personal_atencion_id=personal_atencion_id)
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


def actualizar_personal_salud(ps_id: int, nombre: str | None, especialidad_id: int | None, personal_atencion_id: int | None, db: Session) -> PersonalSaludModel:
    registro = db.query(PersonalSaludModel).filter(PersonalSaludModel.id == ps_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de personal_salud no encontrado")
    if nombre is not None:
        registro.nombre = nombre
    if especialidad_id is not None:
        registro.especialidad_id = especialidad_id
    if personal_atencion_id is not None:
        registro.personal_atencion_id = personal_atencion_id
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
