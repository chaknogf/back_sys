# modules/ciclos/router.py
"""Endpoints autenticados para consultar y registrar ciclos de historia clínica."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from .models import CiclosConsulta
from .schemas import CicloConsulta, CicloConsultaBase, CicloOut, HistoriaClinicaResponse, UltimoOdontogramaOut
from .service import (
    obtener_ciclos_por_consulta as service_obtener_ciclos_por_consulta,
    obtener_ciclo as service_obtener_ciclo,
    obtener_ultimo_ciclo_por_consulta as service_obtener_ultimo_ciclo_por_consulta,
    crear_ciclo as service_crear_ciclo,
    obtener_historia_clinica as service_obtener_historia_clinica,
    obtener_ultimo_odontograma as service_obtener_ultimo_odontograma,
)

router = APIRouter(prefix="/ciclos", tags=["Ciclos Clínicos"])


@router.get("/paciente/{paciente_id}", response_model=HistoriaClinicaResponse)
def obtener_historia_clinica(
    paciente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Historia clínica completa de un paciente, agrupada por consulta.
    Optimizado: una sola query por patient en vez de N+1."""
    return service_obtener_historia_clinica(paciente_id, db, skip, limit)


@router.get("/paciente/{paciente_id}/ultimo-odontograma", response_model=UltimoOdontogramaOut)
def obtener_ultimo_odontograma(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Odontograma más reciente del paciente, para dar continuidad a una nueva nota."""
    return {"odontograma": service_obtener_ultimo_odontograma(paciente_id, db)}


@router.get("/consulta/{consulta_id}", response_model=List[CicloOut])
def obtener_ciclos_por_consulta(
    consulta_id: int,
    activo: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Lista los ciclos de una consulta, activos por defecto.

    Incluye la consulta y su paciente para permitir cargar la historia clínica
    directamente desde el id de consulta."""
    return service_obtener_ciclos_por_consulta(consulta_id, activo, db, skip, limit)


@router.get("/consulta/{consulta_id}/ultimo", response_model=Optional[CicloOut])
def obtener_ultimo_ciclo_por_consulta(
    consulta_id: int,
    activo: Optional[bool] = Query(True),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Nota (ciclo) más reciente de una consulta; null si no tiene notas activas."""
    return service_obtener_ultimo_ciclo_por_consulta(consulta_id, activo, db)


@router.get("/{ciclo_id}", response_model=CicloOut)
def obtener_ciclo(
    ciclo_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_obtener_ciclo(ciclo_id, db)


@router.post("/", response_model=CicloConsulta, status_code=201)
def crear_ciclo(
    data: CicloConsultaBase,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Registra un ciclo atribuyéndolo al usuario autenticado."""
    return service_crear_ciclo(data, db, current_user)
