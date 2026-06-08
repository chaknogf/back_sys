# modules/eventos/service.py
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List

from modules.eventos.models import EventoConsultaModel
from modules.eventos.schemas import (
    EventoConsultaCreate,
    EventoConsultaOut,
    EventoConsultaUpdate,
    EventoConsultaList
)


def listar_eventos(
    db: Session,
    consulta_id: Optional[int] = None,
    tipo_evento: Optional[int] = None,
    responsable: Optional[str] = None,
    estado: Optional[str] = "A",
    skip: int = 0,
    limit: int = 50,
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


def obtener_evento(evento_id: int, db: Session):
    evento = db.get(EventoConsultaModel, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento clínico no encontrado")
    return evento


def crear_evento(evento_in: EventoConsultaCreate, db: Session, current_user):
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


def actualizar_evento(evento_id: int, update_data: EventoConsultaUpdate, db: Session, current_user=None):
    evento = db.get(EventoConsultaModel, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    datos = update_data.model_dump(exclude_unset=True)
    for key, value in datos.items():
        setattr(evento, key, value)

    db.commit()
    db.refresh(evento)
    return evento


def eliminar_evento(evento_id: int, db: Session, current_user=None):
    evento = db.get(EventoConsultaModel, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    evento.estado = "I"
    db.commit()

    return None
