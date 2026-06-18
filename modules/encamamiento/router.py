from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from .schemas import EncamamientoCreate, EncamamientoUpdate, EncamamientoOut
from .service import (
    crear_servicio as service_crear_servicio,
    listar_servicios as service_listar_servicios,
    obtener_servicio as service_obtener_servicio,
    actualizar_servicio as service_actualizar_servicio,
    eliminar_servicio as service_eliminar_servicio,
)

router = APIRouter(
    prefix="/encamamiento",
    tags=["Encamamiento"]
)


@router.post("/", response_model=EncamamientoOut, status_code=status.HTTP_201_CREATED)
def crear_servicio(data: EncamamientoCreate, db: Session = Depends(get_db)):
    return service_crear_servicio(data, db)


@router.get("/", response_model=List[EncamamientoOut])
def listar_servicios(
    activo: bool | None = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return service_listar_servicios(db=db, activo=activo, limit=limit)


@router.get("/{servicio_id}", response_model=EncamamientoOut)
def obtener_servicio(servicio_id: int, db: Session = Depends(get_db)):
    return service_obtener_servicio(servicio_id, db)


@router.patch("/{servicio_id}", response_model=EncamamientoOut)
def actualizar_servicio(servicio_id: int, data: EncamamientoUpdate, db: Session = Depends(get_db)):
    return service_actualizar_servicio(servicio_id, data, db)


@router.delete("/{servicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_servicio(servicio_id: int, db: Session = Depends(get_db)):
    return service_eliminar_servicio(servicio_id, db)
