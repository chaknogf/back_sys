# app/routes/eventos.py
"""
Router de eventos clínicos - Historia clínica electrónica
Soporta búsquedas avanzadas en campos JSONB y CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List

from app.database.db import get_db
from app.models.eventos import EventoConsultaModel
from app.schemas.eventos import (
    EventoConsultaCreate,
    EventoConsultaOut,
    EventoConsultaUpdate,
    EventoConsultaList
)
from app.database.security import get_current_user
from app.models.user import UserModel


router = APIRouter(prefix="/eventos", tags=["Eventos Clínicos"])


# =============================================================================
# LISTAR EVENTOS CON FILTROS AVANZADOS (JSONB)
# =============================================================================
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
    query = db.query(EventoConsultaModel).order_by(desc(EventoConsultaModel.creado_en))

    if consulta_id:
        query = query.filter(EventoConsultaModel.consulta_id == consulta_id)
    if tipo_evento:
        query = query.filter(EventoConsultaModel.tipo_evento == tipo_evento)
    if responsable:
        query = query.filter(
            EventoConsultaModel.responsable["nombre"].astext.ilike(f"%{responsable}%")
        )
    if estado:
        query = query.filter(EventoConsultaModel.estado == estado.upper())

    total = query.count()
    eventos = query.offset(skip).limit(limit).all()

    return EventoConsultaList(total=total, eventos=eventos)


# =============================================================================
# OBTENER UN EVENTO
# =============================================================================
@router.get("/{evento_id}", response_model=EventoConsultaOut)
def obtener_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    evento = db.get(EventoConsultaModel, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento clínico no encontrado")
    return evento


# =============================================================================
# CREAR NUEVO EVENTO
# =============================================================================
@router.post("/", response_model=EventoConsultaOut, status_code=201)
def crear_evento(
    evento_in: EventoConsultaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Opcional: registrar quién creó el evento
    if evento_in.responsable is None:
        evento_in.responsable = {
            "nombre": current_user.nombre,
            "registro": getattr(current_user, "registro", None),
            "cargo": current_user.role
        }

    nuevo_evento = EventoConsultaModel(**evento_in.model_dump())
    db.add(nuevo_evento)
    db.commit()
    db.refresh(nuevo_evento)
    return nuevo_evento


# =============================================================================
# ACTUALIZAR EVENTO (parcial)
# =============================================================================
@router.patch("/{evento_id}", response_model=EventoConsultaOut)
def actualizar_evento(
    evento_id: int,
    update_data: EventoConsultaUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    evento = db.get(EventoConsultaModel, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    datos = update_data.model_dump(exclude_unset=True)
    for key, value in datos.items():
        setattr(evento, key, value)

    db.commit()
    db.refresh(evento)
    return evento


# =============================================================================
# ELIMINAR EVENTO (lógico o físico)
# =============================================================================
@router.delete("/{evento_id}", status_code=204)
def eliminar_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    evento = db.get(EventoConsultaModel, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Opción suave: marcar como inactivo
    evento.estado = "I"
    db.commit()
    
    # Opción fuerte: eliminar físicamente
    # db.delete(evento)
    # db.commit()

    return None