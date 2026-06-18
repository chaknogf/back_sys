from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from modules.encamamiento.models import EncamamientoModel
from modules.encamamiento.schemas import EncamamientoCreate, EncamamientoUpdate


def crear_servicio(data: EncamamientoCreate, db: Session) -> EncamamientoModel:
    existe = db.query(EncamamientoModel).filter(
        EncamamientoModel.nombre_servicio == data.nombre_servicio
    ).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un servicio con ese nombre"
        )
    payload = data.model_dump()
    if not payload.get("descripcion"):
        payload["descripcion"] = payload["nombre_servicio"]
    servicio = EncamamientoModel(**payload)
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio


def listar_servicios(
    db: Session,
    activo: bool | None = None,
    limit: int = 100
) -> List[EncamamientoModel]:
    query = db.query(EncamamientoModel)
    if activo is not None:
        query = query.filter(EncamamientoModel.activo == activo)
    limit = min(limit, 500)
    return query.order_by(EncamamientoModel.nombre_servicio).limit(limit).all()


def obtener_servicio(servicio_id: int, db: Session) -> EncamamientoModel:
    servicio = db.query(EncamamientoModel).filter(EncamamientoModel.id == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio de encamamiento no encontrado")
    return servicio


def actualizar_servicio(servicio_id: int, data: EncamamientoUpdate, db: Session) -> EncamamientoModel:
    servicio = db.query(EncamamientoModel).filter(EncamamientoModel.id == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio de encamamiento no encontrado")
    update_data = data.model_dump(exclude_unset=True)
    if "nombre_servicio" in update_data:
        existe = db.query(EncamamientoModel).filter(
            EncamamientoModel.nombre_servicio == update_data["nombre_servicio"],
            EncamamientoModel.id != servicio_id
        ).first()
        if existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe otro servicio con ese nombre"
            )
    for key, value in update_data.items():
        setattr(servicio, key, value)
    db.commit()
    db.refresh(servicio)
    return servicio


def eliminar_servicio(servicio_id: int, db: Session) -> None:
    servicio = db.query(EncamamientoModel).filter(EncamamientoModel.id == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio de encamamiento no encontrado")
    try:
        db.delete(servicio)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar, está relacionado con otros registros"
        )
    return None
