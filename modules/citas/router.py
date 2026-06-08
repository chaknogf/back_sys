# modules/citas/router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, time, timedelta

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from .models import CitaModel
from .schemas import CitaCreate, CitaListResponse, CitaUpdate, CitaResponse, CitaBase, CitasPorFechaRazon
from .service import (
    crear_cita as service_crear_cita,
    listar_citas as service_listar_citas,
    obtener_citas_por_paciente as service_obtener_citas_por_paciente,
    citas_por_especialidad as service_citas_por_especialidad,
    obtener_cita as service_obtener_cita,
    actualizar_cita as service_actualizar_cita,
    eliminar_cita as service_eliminar_cita,
)

router = APIRouter(
    prefix="/citas",
    tags=["Citas"]
)


@router.post("/", response_model=CitaResponse, status_code=201)
def crear_cita(
    cita: CitaCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service_crear_cita(cita, current_user, db)


@router.get("/", response_model=CitaListResponse)
def listar_citas(
    id: Optional[int] = None,
    expediente: Optional[str] = None,
    paciente_id: Optional[int] = None,
    especialidad: Optional[str] = None,
    fecha_cita: Optional[date] = None,
    limit: int = 200,
    skip: int = 0,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service_listar_citas(
        db=db,
        id=id,
        expediente=expediente,
        paciente_id=paciente_id,
        especialidad=especialidad,
        fecha_cita=fecha_cita,
        limit=limit,
        skip=skip,
    )


@router.get("/paciente/{paciente_id}", response_model=List[CitaResponse])
def obtener_citas_por_paciente(
    paciente_id: int,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    especialidad: Optional[str] = None,
    limit: int = 200,
    skip: int = 0,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service_obtener_citas_por_paciente(
        db=db,
        paciente_id=paciente_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        especialidad=especialidad,
        limit=limit,
        skip=skip,
    )


@router.get("/disponibles", response_model=List[CitasPorFechaRazon])
def citas_por_especialidad(
    especialidad: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service_citas_por_especialidad(especialidad, db)


@router.get("/{cita_id}", response_model=CitaResponse)
def obtener_cita(
    cita_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service_obtener_cita(cita_id, db)


@router.put("/{cita_id}", response_model=CitaResponse)
def actualizar_cita(
    cita_id: int,
    datos: CitaUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service_actualizar_cita(cita_id, datos, db)


@router.delete("/{cita_id}")
def eliminar_cita(
    cita_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service_eliminar_cita(cita_id, db)
