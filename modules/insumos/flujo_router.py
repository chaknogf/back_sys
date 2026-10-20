"""Requisiciones (servicio pide → aprueba → despacha) y despachos/traslados."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, get_current_admin_user
from modules.users.models import UserModel
from modules.insumos.schemas import (
    RequisicionCreate,
    RequisicionOut,
    RequisicionListResponse,
    EstadoAccion,
    DespachoCreate,
    DespachoOut,
    DespachoListResponse,
)
from modules.insumos import service_flujo

router = APIRouter(tags=["Insumos — Flujos"])


# ---------------------------------------------------------------------------
# Requisiciones
# ---------------------------------------------------------------------------

@router.post("/requisiciones", response_model=RequisicionOut, status_code=201)
def crear_requisicion(
    data: RequisicionCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_flujo.crear_requisicion(data, current_user.id, db)


@router.get("/requisiciones", response_model=RequisicionListResponse)
def listar_requisiciones(
    estado: Optional[str] = Query(None, description="pendiente|aprobada|rechazada|despachada"),
    servicio_id: Optional[int] = Query(None, description="ID del servicio (encamamiento)"),
    numero: Optional[str] = Query(None, description="Correlativo parcial (ej. 'REQ-2026')"),
    activo: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_flujo.listar_requisiciones(
        db=db, estado=estado, servicio_id=servicio_id, numero=numero,
        activo=activo, skip=skip, limit=limit,
    )


@router.get("/requisiciones/{requisicion_id}", response_model=RequisicionOut)
def obtener_requisicion(
    requisicion_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_flujo.obtener_requisicion(requisicion_id, db)


@router.post("/requisiciones/{requisicion_id}/aprobar", response_model=RequisicionOut)
def aprobar_requisicion(
    requisicion_id: int,
    data: EstadoAccion | None = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_flujo.aprobar_requisicion(requisicion_id, current_user.id, data, db)


@router.post("/requisiciones/{requisicion_id}/rechazar", response_model=RequisicionOut)
def rechazar_requisicion(
    requisicion_id: int,
    data: EstadoAccion | None = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_flujo.rechazar_requisicion(requisicion_id, current_user.id, data, db)


# ---------------------------------------------------------------------------
# Despachos
# ---------------------------------------------------------------------------

@router.post("/despachos", response_model=DespachoOut, status_code=201)
def crear_despacho(
    data: DespachoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Crea el despacho en borrador; use POST /despachos/{id}/despachar para ejecutarlo."""
    return service_flujo.crear_despacho(data, current_user.id, db)


@router.get("/despachos", response_model=DespachoListResponse)
def listar_despachos(
    tipo: Optional[str] = Query(None, description="servicio|paciente|traslado"),
    estado: Optional[str] = Query(None, description="borrador|despachado|anulado"),
    almacen_origen_id: Optional[int] = Query(None),
    servicio_id: Optional[int] = Query(None),
    paciente_id: Optional[int] = Query(None),
    numero: Optional[str] = Query(None, description="Correlativo parcial (ej. 'DES-2026')"),
    activo: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_flujo.listar_despachos(
        db=db, tipo=tipo, estado=estado, almacen_origen_id=almacen_origen_id,
        servicio_id=servicio_id, paciente_id=paciente_id, numero=numero,
        activo=activo, skip=skip, limit=limit,
    )


@router.get("/despachos/{despacho_id}", response_model=DespachoOut)
def obtener_despacho(
    despacho_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_flujo.obtener_despacho(despacho_id, db)


@router.post("/despachos/{despacho_id}/despachar", response_model=DespachoOut)
def despachar_despacho(
    despacho_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Ejecuta el despacho: descuenta lotes, escribe kardex y cierra la requisición."""
    return service_flujo.despachar_despacho(despacho_id, current_user.id, db)


@router.post("/despachos/{despacho_id}/anular", response_model=DespachoOut)
def anular_despacho(
    despacho_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_admin_user),
):
    """Solo despachos en borrador; los ejecutados ya movieron stock."""
    return service_flujo.anular_despacho(despacho_id, db)
