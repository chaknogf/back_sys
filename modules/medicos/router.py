# modules/medicos/router.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from .models import MedicoModel
from .schemas import MedicoCreate, MedicoUpdate, MedicoOut, MedicoListResponse
from .service import (
    crear_medico as service_crear_medico,
    listar_medicos as service_listar_medicos,
    obtener_medico as service_obtener_medico,
    actualizar_medico as service_actualizar_medico,
    eliminar_medico as service_eliminar_medico,
)

router = APIRouter(
    prefix="/medicos",
    tags=["Medicos"]
)


@router.post("/", response_model=MedicoOut, status_code=status.HTTP_201_CREATED)
def crear_medico(data: MedicoCreate, db: Session = Depends(get_db)):
    return service_crear_medico(data, db)


@router.get("/", response_model=MedicoListResponse)
def listar_medicos(
    id: Optional[int] = None,
    activo: Optional[bool] = None,
    nombre: Optional[str] = None,
    colegiado: Optional[str] = None,
    pasaporte: Optional[str] = None,
    especialidad: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    return service_listar_medicos(
        db=db,
        id=id,
        activo=activo,
        nombre=nombre,
        colegiado=colegiado,
        pasaporte=pasaporte,
        especialidad=especialidad,
        skip=skip,
        limit=limit,
    )


@router.get("/{medico_id}", response_model=MedicoOut)
def obtener_medico(medico_id: int, db: Session = Depends(get_db)):
    return service_obtener_medico(medico_id, db)


@router.put("/{medico_id}", response_model=MedicoOut)
def actualizar_medico(
    medico_id: int,
    data: MedicoUpdate,
    db: Session = Depends(get_db)
):
    return service_actualizar_medico(medico_id, data, db)


@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medico(medico_id: int, db: Session = Depends(get_db)):
    return service_eliminar_medico(medico_id, db)
