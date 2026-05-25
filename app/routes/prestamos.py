# app/routes/prestamos.py

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.db import get_db
from app.database.security import get_current_user
from app.models.user import UserModel
from app.models.prestamos import Prestamo
from app.schemas.prestamos import (
    PrestamoCreate,
    PrestamoUpdate,
    Prestamo as PrestamoSchema
)


router = APIRouter(
    prefix="/prestamos",
    tags=["Prestamos"]
)


# =========================================================
# CREAR PRESTAMO
# =========================================================

@router.post("/", response_model=PrestamoSchema)
def crear_prestamo(
    data: PrestamoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    nuevo_prestamo = Prestamo(
        **data.model_dump(),
        usuario_entrega=current_user.username   # ← automático desde el token
    )

    db.add(nuevo_prestamo)
    db.commit()
    db.refresh(nuevo_prestamo)

    return nuevo_prestamo


# =========================================================
# LISTAR PRESTAMOS
# =========================================================

@router.get("/", response_model=List[PrestamoSchema])
def listar_prestamos(
    activo: Optional[bool] = Query(None),
    id_paciente: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    query = db.query(Prestamo)

    if activo is not None:
        query = query.filter(Prestamo.activo == activo)

    if id_paciente:
        query = query.filter(Prestamo.id_paciente == id_paciente)

    return query.order_by(desc(Prestamo.fecha_prestamo)).all()


# =========================================================
# OBTENER PRESTAMO
# =========================================================

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


# =========================================================
# ACTUALIZAR PRESTAMO
# =========================================================

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

    # Si se está registrando la devolución (fecha_devolucion llega en el PUT),
    # asignar automáticamente quién recibe
    if "fecha_devolucion" in update_data and update_data["fecha_devolucion"] is not None:
        prestamo.usuario_recibe = current_user.username  # ← automático desde el token

    db.commit()
    db.refresh(prestamo)

    return prestamo


# =========================================================
# ELIMINAR (DESACTIVAR)
# =========================================================

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