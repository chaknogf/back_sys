"""Atenciones con consumo de insumos y unidosis por paciente."""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.insumos.schemas import (
    AtencionCreate,
    AtencionInsumoCreate,
    AtencionInsumo,
    AtencionOut,
    AtencionDetalle,
    AtencionListResponse,
    UnidosisCreate,
    UnidosisOut,
    UnidosisListResponse,
)
from modules.insumos import service_flujo

router = APIRouter(tags=["Insumos — Atenciones y Unidosis"])


# ---------------------------------------------------------------------------
# Atenciones
# ---------------------------------------------------------------------------

@router.post("/atenciones", response_model=AtencionOut, status_code=201)
def crear_atencion(
    data: AtencionCreate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_flujo.crear_atencion(data, db)


@router.get("/atenciones", response_model=AtencionListResponse)
def listar_atenciones(
    paciente_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None, description="abierta|finalizada|cancelada"),
    servicio_id: Optional[int] = Query(None),
    consulta_id: Optional[int] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    activo: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_flujo.listar_atenciones(
        db=db, paciente_id=paciente_id, estado=estado, servicio_id=servicio_id,
        consulta_id=consulta_id, desde=desde, hasta=hasta,
        activo=activo, skip=skip, limit=limit,
    )


@router.get("/atenciones/{atencion_id}", response_model=AtencionDetalle)
def obtener_atencion(
    atencion_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_flujo.obtener_atencion(atencion_id, db)


@router.post("/atenciones/{atencion_id}/finalizar", response_model=AtencionOut)
def finalizar_atencion(
    atencion_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_flujo.finalizar_atencion(atencion_id, db)


@router.post("/atenciones/{atencion_id}/insumos", response_model=AtencionInsumo, status_code=201)
def registrar_insumo_atencion(
    atencion_id: int,
    data: AtencionInsumoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Descuenta stock del lote y registra el consumo (kardex) en la atención."""
    return service_flujo.registrar_insumo_atencion(atencion_id, data, current_user.id, db)


# ---------------------------------------------------------------------------
# Unidosis
# ---------------------------------------------------------------------------

@router.post("/unidosis", response_model=UnidosisOut, status_code=201)
def crear_unidosis(
    data: UnidosisCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Prepara la unidosis: descuenta farmacia (kardex consumo) al momento de crear."""
    return service_flujo.crear_unidosis(data, current_user.id, db)


@router.get("/unidosis", response_model=UnidosisListResponse)
def listar_unidosis(
    paciente_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None, description="preparada|administrada|cancelada"),
    almacen_id: Optional[int] = Query(None),
    numero: Optional[str] = Query(None, description="Correlativo parcial (ej. 'UNI-2026')"),
    activo: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_flujo.listar_unidosis(
        db=db, paciente_id=paciente_id, estado=estado, almacen_id=almacen_id,
        numero=numero, activo=activo, skip=skip, limit=limit,
    )


@router.get("/unidosis/{unidosis_id}", response_model=UnidosisOut)
def obtener_unidosis(
    unidosis_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_flujo.obtener_unidosis(unidosis_id, db)


@router.post("/unidosis/{unidosis_id}/administrar", response_model=UnidosisOut)
def administrar_unidosis(
    unidosis_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_flujo.administrar_unidosis(unidosis_id, db)


@router.post("/unidosis/{unidosis_id}/cancelar", response_model=UnidosisOut)
def cancelar_unidosis(
    unidosis_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Cancela la unidosis preparada y devuelve el stock a farmacia."""
    return service_flujo.cancelar_unidosis(unidosis_id, current_user.id, db)
