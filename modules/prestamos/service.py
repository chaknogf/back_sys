from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from fastapi import HTTPException

from modules.prestamos.models import Prestamo
from modules.pacientes.models import PacienteModel
from modules.prestamos.schemas import PrestamoCreate, PrestamoUpdate, PrestamoListResponse


def crear_prestamo(data: PrestamoCreate, username: str, db: Session):
    nuevo = Prestamo(**data.model_dump(), usuario_entrega=username)
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
        termino = f"%{nombre_paciente}%"
        query = query.filter(
            or_(
                PacienteModel.primer_nombre.ilike(termino),
                PacienteModel.segundo_nombre.ilike(termino),
                PacienteModel.primer_apellido.ilike(termino),
                PacienteModel.segundo_apellido.ilike(termino),
            )
        )

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
    for key, value in update_data.items():
        setattr(prestamo, key, value)

    if "fecha_devolucion" in update_data and update_data["fecha_devolucion"] is not None:
        prestamo.usuario_recibe = username
        prestamo.activo = False

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
