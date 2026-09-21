# modules/citas/service.py
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, time, timedelta

from modules.citas.models import CitaModel, CitaDiaInhabilModel
from modules.pacientes.models import PacienteModel
from modules.medicos.models import MedicoModel
from modules.citas.schemas import (
    CitaCreate, CitaListResponse, CitaUpdate, CitaResponse, CitaBase, CitasPorFechaRazon,
    DiaInhabilCreate, DiaInhabilUpdate,
)


DIAS_ES = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}


def _validar_fecha_cita(db: Session, fecha: date, es_creacion: bool = True) -> None:
    """Reglas para agendar: solo días hábiles (lun–vie) y fechas no
    deshabilitadas por el administrador (feriados / asuetos)."""
    if fecha is None:
        return
    if fecha.weekday() >= 5:
        raise HTTPException(
            status_code=400,
            detail=(
                "Las citas solo se pueden agendar en días hábiles "
                "(lunes a viernes)."
            ),
        )
    inhabilitado = (
        db.query(CitaDiaInhabilModel)
        .filter(
            CitaDiaInhabilModel.fecha == fecha,
            CitaDiaInhabilModel.activo.is_(True),
        )
        .first()
    )
    if inhabilitado:
        motivo = f" ({inhabilitado.motivo})" if inhabilitado.motivo else ""
        raise HTTPException(
            status_code=400,
            detail=f"La fecha {fecha.isoformat()} está deshabilitada para citas{motivo}.",
        )


def crear_cita(cita: CitaCreate, current_user, db: Session):
    _validar_fecha_cita(db, cita.fecha_cita)
    if cita.personal_atencion_id is not None:
        if db.get(MedicoModel, cita.personal_atencion_id) is None:
            raise HTTPException(
                status_code=404,
                detail="El personal de atención asignado no existe",
            )
    nueva_cita = CitaModel(
        created_by=current_user.username[:8] if current_user and current_user.username else None,
        fecha_registro=cita.fecha_registro,
        expediente=cita.expediente,
        paciente_id=cita.paciente_id,
        especialidad=cita.especialidad,
        especialidad_id=cita.especialidad_id,
        personal_atencion_id=cita.personal_atencion_id,
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
    especialidad_id: Optional[int] = None,
    personal_atencion_id: Optional[int] = None,
    fecha_cita: Optional[date] = None,
    limit: int = 200,
    skip: int = 0,
):
    query = db.query(CitaModel).outerjoin(
        PacienteModel, CitaModel.paciente_id == PacienteModel.id
    )
    if fecha_cita is None and id is None and paciente_id is None:
        fecha_cita = date.today()
    if id is not None:
        query = query.filter(CitaModel.id == id)
    if expediente is not None:
        query = query.filter(PacienteModel.expediente == expediente)
    if paciente_id is not None:
        query = query.filter(CitaModel.paciente_id == paciente_id)
    if especialidad is not None:
        query = query.filter(CitaModel.especialidad == especialidad)
    if especialidad_id is not None:
        query = query.filter(CitaModel.especialidad_id == especialidad_id)
    if personal_atencion_id is not None:
        query = query.filter(CitaModel.personal_atencion_id == personal_atencion_id)
    if fecha_cita is not None:
        query = query.filter(CitaModel.fecha_cita == fecha_cita)
    total = query.count()
    citas = query.order_by(PacienteModel.expediente.asc().nullslast()).offset(skip).limit(limit).all()
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

    dia_semana = func.trim(
        func.to_char(CitaModel.fecha_cita, 'Day')
    ).label("dia_semana")

    resultados = (
        db.query(
            CitaModel.fecha_cita,
            CitaModel.razon_consulta,
            dia_semana,
            func.count(CitaModel.id).label("total")
        )
        .filter(
            CitaModel.especialidad == especialidad,
            CitaModel.fecha_cita >= fecha_inicio
        )
        .group_by(
            CitaModel.fecha_cita,
            CitaModel.razon_consulta,
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
        datos_dict = datos.model_dump(exclude_unset=True)

        if "fecha_cita" in datos_dict:
            _validar_fecha_cita(db, datos_dict["fecha_cita"])
        if "personal_atencion_id" in datos_dict and datos_dict.get("personal_atencion_id") is not None:
            if db.get(MedicoModel, datos_dict["personal_atencion_id"]) is None:
                raise HTTPException(
                    status_code=404,
                    detail="El personal de atención asignado no existe",
                )

        for campo, valor in datos_dict.items():
            setattr(cita, campo, valor)

        db.commit()
        db.refresh(cita)

    except HTTPException:
        db.rollback()
        raise
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


# ════════════════════════════════════════════════════════════════
# DÍAS INHÁBILES — control de fechas sin agendar (feriados/asuetos)
# ════════════════════════════════════════════════════════════════
def listar_dias_inhabiles(
    db: Session,
    activo: Optional[bool] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
):
    query = db.query(CitaDiaInhabilModel)
    if activo is not None:
        query = query.filter(CitaDiaInhabilModel.activo.is_(activo))
    if desde is not None:
        query = query.filter(CitaDiaInhabilModel.fecha >= desde)
    if hasta is not None:
        query = query.filter(CitaDiaInhabilModel.fecha <= hasta)
    return query.order_by(CitaDiaInhabilModel.fecha.asc()).all()


def crear_dia_inhabil(data: DiaInhabilCreate, username: str, db: Session):
    existe = (
        db.query(CitaDiaInhabilModel)
        .filter(CitaDiaInhabilModel.fecha == data.fecha)
        .first()
    )
    if existe:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un registro para esa fecha",
        )
    registro = CitaDiaInhabilModel(
        fecha=data.fecha,
        motivo=(data.motivo or "").strip() or None,
        activo=True,
        created_by=(username or "")[:20],
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


def actualizar_dia_inhabil(registro_id: int, data: DiaInhabilUpdate, db: Session):
    registro = db.get(CitaDiaInhabilModel, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Fecha no encontrada")

    datos = data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(registro, campo, valor)
    db.commit()
    db.refresh(registro)
    return registro


def eliminar_dia_inhabil(registro_id: int, db: Session):
    registro = db.get(CitaDiaInhabilModel, registro_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Fecha no encontrada")
    db.delete(registro)
    db.commit()
    return {"message": "Fecha eliminada correctamente"}