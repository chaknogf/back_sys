from typing import Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from fastapi import HTTPException

from modules.prestamos.models import Prestamo
from modules.pacientes.models import PacienteModel
from modules.consultas.models import ConsultaModel
from modules.prestamos.schemas import PrestamoCreate, PrestamoUpdate, PrestamoListResponse


def _normalizar_opcional(valor):
    if valor is None:
        return None
    if isinstance(valor, str):
        return valor.strip() or None
    return valor


def _validar_paciente(db: Session, id_paciente: int) -> None:
    existe = db.query(PacienteModel.id).filter(PacienteModel.id == id_paciente).first()
    if not existe:
        raise HTTPException(
            status_code=404,
            detail="El paciente no existe; verifique el ID de paciente",
        )


def crear_prestamo(data: PrestamoCreate, username: str, db: Session):
    _validar_paciente(db, data.id_paciente)

    if data.id_consulta is not None:
        existe_consulta = (
            db.query(ConsultaModel.id)
            .filter(ConsultaModel.id == data.id_consulta)
            .first()
        )
        if not existe_consulta:
            raise HTTPException(
                status_code=404,
                detail="La consulta asociada no fue encontrada",
            )

    payload = data.model_dump()
    payload["expediente"] = _normalizar_opcional(payload.get("expediente"))
    payload["motivo"] = _normalizar_opcional(payload.get("motivo"))
    payload["ubicacion"] = _normalizar_opcional(payload.get("ubicacion"))
    payload["nota"] = _normalizar_opcional(payload.get("nota"))
    payload["solicitante"] = (payload.get("solicitante") or "").strip()

    nuevo = Prestamo(**payload, usuario_entrega=username)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def listar_prestamos(
    db: Session,
    activo: Optional[bool] = True,
    id_paciente: Optional[int] = None,
    expediente: Optional[str] = None,
    tipo_documento: Optional[str] = None,
    nombre_paciente: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    skip: int = 0,
    limit: int = 20,
):
    query = db.query(Prestamo).join(
        PacienteModel, Prestamo.id_paciente == PacienteModel.id, isouter=True
    )

    if activo is not None:
        query = query.filter(Prestamo.activo == activo)
    if id_paciente:
        query = query.filter(Prestamo.id_paciente == id_paciente)
    if expediente:
        query = query.filter(Prestamo.expediente.ilike(f"%{expediente}%"))
    if tipo_documento:
        query = query.filter(Prestamo.tipo_documento.ilike(f"%{tipo_documento}%"))
    if nombre_paciente:
        nombre_normalizado = func.unaccent(func.lower(PacienteModel.nombre_completo))
        termino = "%" + nombre_paciente.strip().lower() + "%"
        query = query.filter(
            or_(
                nombre_normalizado.ilike(termino),
                PacienteModel.expediente.ilike(nombre_paciente.strip()),
            )
        )
    if fecha_desde:
        query = query.filter(Prestamo.fecha_prestamo >= fecha_desde)
    if fecha_hasta:
        # fecha_hasta es un date; sumamos 1 día → intervalo [.., hasta+1) para
        # incluir todo el día hasta las 23:59:59.
        query = query.filter(Prestamo.fecha_prestamo < fecha_hasta + timedelta(days=1))

    total = query.count()
    items = (
        query
        .order_by(desc(Prestamo.fecha_prestamo))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"total": total, "items": items}


def obtener_prestamo(prestamo_id: int, db: Session):
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return prestamo


def actualizar_prestamo(prestamo_id: int, data: PrestamoUpdate, username: str, db: Session):
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    if "id_consulta" in update_data and update_data["id_consulta"] is not None:
        existe_consulta = (
            db.query(ConsultaModel.id)
            .filter(ConsultaModel.id == update_data["id_consulta"])
            .first()
        )
        if not existe_consulta:
            raise HTTPException(
                status_code=404,
                detail="La consulta asociada no fue encontrada",
            )

    for key, value in update_data.items():
        setattr(prestamo, key, _normalizar_opcional(value))

    if "fecha_devolucion" in update_data:
        if update_data["fecha_devolucion"] is not None:
            prestamo.usuario_recibe = username
            prestamo.activo = False
        else:
            prestamo.usuario_recibe = None
            prestamo.activo = True

    db.commit()
    db.refresh(prestamo)
    return prestamo


def eliminar_prestamo(prestamo_id: int, db: Session):
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    prestamo.activo = False
    db.commit()
    return {"detail": "Préstamo desactivado correctamente"}