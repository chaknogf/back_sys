from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.prestamos.schemas import (
    PrestamoCreate,
    PrestamoUpdate,
    Prestamo as PrestamoSchema,
    PrestamoListResponse
)
from modules.prestamos.service import (
    crear_prestamo as service_crear,
    listar_prestamos as service_listar,
    obtener_prestamo as service_obtener,
    actualizar_prestamo as service_actualizar,
    eliminar_prestamo as service_eliminar,
)

router = APIRouter(prefix="/prestamos", tags=["Prestamos"])


@router.post("/", response_model=PrestamoSchema)
def crear_prestamo(
    data: PrestamoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_crear(data, current_user.username, db)


@router.get("/", response_model=PrestamoListResponse)
def listar_prestamos(
    activo: Optional[bool] = Query(True),
    id_paciente: Optional[int] = Query(None),
    expediente: Optional[str] = Query(None),
    tipo_documento: Optional[str] = Query(None),
    nombre_paciente: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None, description="Rango desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Rango hasta (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_listar(
        db=db, activo=activo, id_paciente=id_paciente,
        expediente=expediente, tipo_documento=tipo_documento,
        nombre_paciente=nombre_paciente,
        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        skip=skip, limit=limit,
    )


@router.get("/{prestamo_id}", response_model=PrestamoSchema)
def obtener_prestamo(
    prestamo_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_obtener(prestamo_id, db)


@router.put("/{prestamo_id}", response_model=PrestamoSchema)
def actualizar_prestamo(
    prestamo_id: int,
    data: PrestamoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_actualizar(prestamo_id, data, current_user.username, db)


@router.delete("/{prestamo_id}")
def eliminar_prestamo(
    prestamo_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_eliminar(prestamo_id, db)
