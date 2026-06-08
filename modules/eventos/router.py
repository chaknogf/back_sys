# modules/eventos/router.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from .schemas import (
    EventoConsultaCreate,
    EventoConsultaOut,
    EventoConsultaUpdate,
    EventoConsultaList
)
from .service import (
    listar_eventos as service_listar_eventos,
    obtener_evento as service_obtener_evento,
    crear_evento as service_crear_evento,
    actualizar_evento as service_actualizar_evento,
    eliminar_evento as service_eliminar_evento,
)

router = APIRouter(prefix="/eventos", tags=["Eventos Clínicos"])


@router.get("/", response_model=EventoConsultaList)
def listar_eventos(
    consulta_id: Optional[int] = Query(None, description="Filtrar por ID de consulta"),
    tipo_evento: Optional[int] = Query(None, description="Ej: 1=Ingreso, 2=Evolución, 3=Egreso"),
    responsable: Optional[str] = Query(None, description="Nombre del responsable"),
    estado: Optional[str] = Query("A", description="A=Activo, I=Inactivo"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_listar_eventos(
        db=db,
        consulta_id=consulta_id,
        tipo_evento=tipo_evento,
        responsable=responsable,
        estado=estado,
        skip=skip,
        limit=limit,
    )


@router.get("/{evento_id}", response_model=EventoConsultaOut)
def obtener_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_obtener_evento(evento_id, db)


@router.post("/", response_model=EventoConsultaOut, status_code=201)
def crear_evento(
    evento_in: EventoConsultaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_crear_evento(evento_in, db, current_user)


@router.patch("/{evento_id}", response_model=EventoConsultaOut)
def actualizar_evento(
    evento_id: int,
    update_data: EventoConsultaUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_actualizar_evento(evento_id, update_data, db)


@router.delete("/{evento_id}", status_code=204)
def eliminar_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_eliminar_evento(evento_id, db)
