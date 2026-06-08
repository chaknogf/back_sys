# modules/ciclos/router.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from .models import CiclosConsulta
from .schemas import CicloConsulta, CicloConsultaBase, CicloOut
from .service import (
    obtener_ciclos_por_consulta as service_obtener_ciclos_por_consulta,
    obtener_ciclo as service_obtener_ciclo,
    crear_ciclo as service_crear_ciclo,
)

router = APIRouter(prefix="/ciclos", tags=["Ciclos Clínicos"])


@router.get("/consulta/{consulta_id}", response_model=List[CicloConsulta])
def obtener_ciclos_por_consulta(
    consulta_id: int,
    activo: Optional[bool] = Query(True),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_obtener_ciclos_por_consulta(consulta_id, activo, db)


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
    return service_crear_ciclo(data, db, current_user)
