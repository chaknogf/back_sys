from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.prestamos.models import Prestamo
from modules.pacientes.models import PacienteModel
from modules.prestamos.schemas import (
    PrestamoCreate,
    PrestamoUpdate,
    Prestamo as PrestamoSchema,
    PrestamoListResponse
)


router = APIRouter(
    prefix="/prestamos",
    tags=["Prestamos"]
)


@router.post("/", response_model=PrestamoSchema)
def crear_prestamo(
    data: PrestamoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    nuevo_prestamo = Prestamo(
        **data.model_dump(),
        usuario_entrega=current_user.username
    )

    db.add(nuevo_prestamo)
    db.commit()
    db.refresh(nuevo_prestamo)

    return nuevo_prestamo


@router.get("/", response_model=PrestamoListResponse)
def listar_prestamos(
    activo: Optional[bool] = Query(True),
    id_paciente: Optional[int] = Query(None),
    expediente: Optional[str] = Query(None),
    tipo_documento: Optional[str] = Query(None),
    nombre_paciente: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
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


@router.get("/{prestamo_id}", response_model=PrestamoSchema)
def obtener_prestamo(
    prestamo_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()

    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    return prestamo


@router.put("/{prestamo_id}", response_model=PrestamoSchema)
def actualizar_prestamo(
    prestamo_id: int,
    data: PrestamoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()

    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(prestamo, key, value)

    if "fecha_devolucion" in update_data and update_data["fecha_devolucion"] is not None:
        prestamo.usuario_recibe = current_user.username
        prestamo.activo = False

    db.commit()
    db.refresh(prestamo)

    return prestamo


@router.delete("/{prestamo_id}")
def eliminar_prestamo(
    prestamo_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()

    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    prestamo.activo = False

    db.commit()

    return {"detail": "Préstamo desactivado correctamente"}
