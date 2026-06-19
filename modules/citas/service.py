# modules/citas/service.py
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, time, timedelta

from modules.citas.models import CitaModel
from modules.citas.schemas import CitaCreate, CitaListResponse, CitaUpdate, CitaResponse, CitaBase, CitasPorFechaRazon


DIAS_ES = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}


def crear_cita(cita: CitaCreate, current_user, db: Session):
    nueva_cita = CitaModel(
        created_by=current_user.id,
        fecha_registro=cita.fecha_registro,
        expediente=cita.expediente,
        paciente_id=cita.paciente_id,
        especialidad=cita.especialidad,
        fecha_cita=cita.fecha_cita,
        datos_extra=cita.datos_extra
    )

    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita


def listar_citas(
    db: Session,
    id: Optional[int] = None,
    expediente: Optional[str] = None,
    paciente_id: Optional[int] = None,
    especialidad: Optional[str] = None,
    fecha_cita: Optional[date] = None,
    limit: int = 200,
    skip: int = 0,
):
    query = db.query(CitaModel)
    if fecha_cita is None:
        fecha_cita = date.today()
    if id is not None:
        query = query.filter(CitaModel.id == id)
    if expediente is not None:
        query = query.filter(CitaModel.expediente == expediente)
    if paciente_id is not None:
        query = query.filter(CitaModel.paciente_id == paciente_id)
    if especialidad is not None:
        query = query.filter(CitaModel.especialidad == especialidad)
    if fecha_cita is not None:
        query = query.filter(CitaModel.fecha_cita == fecha_cita)
    total = query.count()
    citas = query.order_by(CitaModel.expediente.asc()).offset(skip).limit(limit).all()
    return CitaListResponse(total=total, citas=citas)


def obtener_citas_por_paciente(
    db: Session,
    paciente_id: int,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    especialidad: Optional[str] = None,
    limit: int = 200,
    skip: int = 0,
):
    query = db.query(CitaModel).filter(CitaModel.paciente_id == paciente_id)

    if fecha_desde is not None:
        query = query.filter(CitaModel.fecha_cita == fecha_desde)
    if fecha_hasta is not None:
        query = query.filter(CitaModel.fecha_cita == fecha_hasta)
    if especialidad is not None:
        query = query.filter(CitaModel.especialidad == especialidad)

    citas = query.order_by(CitaModel.fecha_cita.asc()).offset(skip).limit(limit).all()

    if not citas:
        raise HTTPException(status_code=404, detail="No se encontraron citas para este paciente")

    return citas


def citas_por_especialidad(especialidad: str, db: Session):
    fecha_inicio = date.today() + timedelta(days=1)

    razon = CitaModel.datos_extra['razon_consulta'].astext

    dia_semana = func.trim(
        func.to_char(CitaModel.fecha_cita, 'Day')
    ).label("dia_semana")

    resultados = (
        db.query(
            CitaModel.fecha_cita,
            razon.label("razon_consulta"),
            dia_semana,
            func.count(CitaModel.id).label("total")
        )
        .filter(
            CitaModel.especialidad == especialidad,
            CitaModel.fecha_cita >= fecha_inicio
        )
        .group_by(
            CitaModel.fecha_cita,
            razon,
            dia_semana
        )
        .order_by(
            CitaModel.fecha_cita.asc()
        )
        .all()
    )

    resultados_formateados = []

    for r in resultados:
        resultados_formateados.append({
            "fecha_cita": r.fecha_cita,
            "razon_consulta": r.razon_consulta,
            "dia_semana": DIAS_ES.get(r.dia_semana, r.dia_semana),
            "total": r.total
        })

    return resultados_formateados


def obtener_cita(cita_id: int, db: Session):
    cita = db.query(CitaModel).filter(CitaModel.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return cita


def actualizar_cita(cita_id: int, datos: CitaUpdate, db: Session):
    cita = db.query(CitaModel).filter(CitaModel.id == cita_id).first()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    try:
        datos_dict = datos.dict(exclude_unset=True)

        for campo, valor in datos_dict.items():
            setattr(cita, campo, valor)

        db.commit()
        db.refresh(cita)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar: {str(e)}"
        )

    return cita


def eliminar_cita(cita_id: int, db: Session):
    cita = db.query(CitaModel).filter(CitaModel.id == cita_id).first()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    db.delete(cita)
    db.commit()

    return {"message": "Cita eliminada correctamente"}