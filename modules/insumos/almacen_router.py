"""Almacenes, lotes (stock) y kardex."""

from typing import Optional
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, get_current_admin_user
from modules.users.models import UserModel
from modules.insumos.schemas import (
    AlmacenCreate,
    AlmacenUpdate,
    Almacen,
    AlmacenListResponse,
    LoteIngresoCreate,
    LoteAjusteCreate,
    LoteOut,
    LoteListResponse,
    KardexOut,
    KardexListResponse,
)
from modules.insumos import service_almacen

router = APIRouter(tags=["Insumos — Almacén"])


# ---------------------------------------------------------------------------
# Almacenes
# ---------------------------------------------------------------------------

@router.get("/almacenes", response_model=AlmacenListResponse)
def listar_almacenes(
    tipo: Optional[str] = Query(None, description="bodega|farmacia|productos_afines|servicio"),
    activo: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_almacen.listar_almacenes(
        db=db, tipo=tipo, activo=activo, skip=skip, limit=limit,
    )


@router.get("/almacenes/{almacen_id}", response_model=Almacen)
def obtener_almacen(
    almacen_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_almacen.obtener_almacen(almacen_id, db)


@router.post("/almacenes", response_model=Almacen, status_code=201)
def crear_almacen(
    data: AlmacenCreate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_almacen.crear_almacen(data, db)


@router.put("/almacenes/{almacen_id}", response_model=Almacen)
def actualizar_almacen(
    almacen_id: int,
    data: AlmacenUpdate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_almacen.actualizar_almacen(almacen_id, data, db)


@router.delete("/almacenes/{almacen_id}")
def eliminar_almacen(
    almacen_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_admin_user),
):
    return service_almacen.eliminar_almacen(almacen_id, db)


# ---------------------------------------------------------------------------
# Lotes (stock)
# ---------------------------------------------------------------------------

@router.get("/lotes", response_model=LoteListResponse)
def listar_lotes(
    almacen_id: Optional[int] = Query(None),
    presentacion_id: Optional[int] = Query(None),
    insumo_id: Optional[int] = Query(None),
    con_stock: Optional[bool] = Query(None, description="Solo lotes con/sin cantidad > 0"),
    vencimiento_hasta: Optional[date] = Query(None, description="Vencen en o antes de (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_almacen.listar_lotes(
        db=db, almacen_id=almacen_id, presentacion_id=presentacion_id,
        insumo_id=insumo_id, con_stock=con_stock,
        vencimiento_hasta=vencimiento_hasta, skip=skip, limit=limit,
    )


@router.post("/lotes/ingreso", response_model=LoteOut, status_code=201)
def ingresar_lote(
    data: LoteIngresoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Entrada de stock: recarga o crea el lote y registra kardex de entrada."""
    return service_almacen.ingresar_lote(data, current_user.id, db)


@router.post("/lotes/ajuste", response_model=LoteOut)
def ajustar_lote(
    data: LoteAjusteCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Ajuste de inventario (conteo físico): fija la cantidad real del lote."""
    return service_almacen.ajustar_lote(data, current_user.id, db)


# ---------------------------------------------------------------------------
# Kardex (solo lectura)
# ---------------------------------------------------------------------------

@router.get("/kardex", response_model=KardexListResponse)
def listar_kardex(
    lote_id: Optional[int] = Query(None),
    almacen_id: Optional[int] = Query(None),
    tipo_movimiento: Optional[str] = Query(None, description="entrada|salida|traslado|consumo|ajuste"),
    referencia_tipo: Optional[str] = Query(None, description="ingreso|despacho|unidosis|atencion|ajuste"),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_almacen.listar_kardex(
        db=db, lote_id=lote_id, almacen_id=almacen_id,
        tipo_movimiento=tipo_movimiento, referencia_tipo=referencia_tipo,
        desde=desde, hasta=hasta, skip=skip, limit=limit,
    )


@router.get("/kardex/lote/{lote_id}", response_model=KardexListResponse)
def obtener_kardex_lote(
    lote_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service_almacen.obtener_kardex_lote(lote_id, db)
