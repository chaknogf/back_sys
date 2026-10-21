"""Almacenes, lotes (stock) y kardex.

El stock vive solo en `lotes`; cada movimiento genera su fila en
`kardex_movimientos` con el saldo resultante del lote.
"""

from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from modules.insumos.models import (
    Almacen,
    Lote,
    KardexMovimiento,
    Presentacion,
)
from modules.insumos.schemas import (
    AlmacenCreate,
    AlmacenUpdate,
    LoteIngresoCreate,
    LoteAjusteCreate,
)
from modules.insumos.helpers import (
    obtener_o_404,
    paginar,
    registrar_kardex,
)


# ---------------------------------------------------------------------------
# Almacenes
# ---------------------------------------------------------------------------

def listar_almacenes(
    db: Session,
    tipo: str | None = None,
    activo: bool | None = True,
    skip: int = 0,
    limit: int = 50,
) -> dict:
    query = db.query(Almacen)
    if activo is not None:
        query = query.filter(Almacen.activo == activo)
    if tipo:
        query = query.filter(Almacen.tipo == tipo)
    return paginar(query, skip, limit, Almacen.nombre)


def obtener_almacen(almacen_id: int, db: Session) -> Almacen:
    return obtener_o_404(db, Almacen, almacen_id, "Almacén no encontrado")


def crear_almacen(data: AlmacenCreate, db: Session) -> Almacen:
    existe = (
        db.query(Almacen.id)
        .filter(or_(Almacen.codigo == data.codigo.strip(), Almacen.nombre == data.nombre.strip()))
        .first()
    )
    if existe:
        raise HTTPException(
            status_code=409, detail="Ya existe un almacén con ese código o nombre"
        )
    almacen = Almacen(
        codigo=data.codigo.strip(),
        nombre=data.nombre.strip(),
        tipo=data.tipo,
        activo=data.activo if data.activo is not None else True,
    )
    db.add(almacen)
    db.commit()
    db.refresh(almacen)
    return almacen


def actualizar_almacen(almacen_id: int, data: AlmacenUpdate, db: Session) -> Almacen:
    almacen = obtener_almacen(almacen_id, db)
    campos = data.model_dump(exclude_unset=True)
    for key in ("codigo", "nombre"):
        if key in campos:
            campos[key] = campos[key].strip()
    for key, value in campos.items():
        setattr(almacen, key, value)
    db.commit()
    db.refresh(almacen)
    return almacen


def eliminar_almacen(almacen_id: int, db: Session) -> dict:
    almacen = obtener_almacen(almacen_id, db)
    almacen.activo = False
    db.commit()
    return {"id": almacen_id, "activo": False}


# ---------------------------------------------------------------------------
# Lotes (stock)
# ---------------------------------------------------------------------------

def listar_lotes(
    db: Session,
    almacen_id: int | None = None,
    presentacion_id: int | None = None,
    insumo_id: int | None = None,
    con_stock: bool | None = None,
    vencimiento_hasta=None,
    skip: int = 0,
    limit: int = 50,
) -> dict:
    query = db.query(Lote).filter(Lote.activo == True)  # noqa: E712
    if almacen_id is not None:
        query = query.filter(Lote.almacen_id == almacen_id)
    if presentacion_id is not None:
        query = query.filter(Lote.presentacion_id == presentacion_id)
    if insumo_id is not None:
        query = query.join(Presentacion, Presentacion.id == Lote.presentacion_id).filter(
            Presentacion.insumo_id == insumo_id
        )
    if con_stock is True:
        query = query.filter(Lote.cantidad_actual > 0)
    elif con_stock is False:
        query = query.filter(Lote.cantidad_actual == 0)
    if vencimiento_hasta is not None:
        query = query.filter(
            Lote.fecha_vencimiento.isnot(None), Lote.fecha_vencimiento <= vencimiento_hasta
        )
    return paginar(
        query, skip, limit,
        [Lote.fecha_vencimiento.asc().nulls_last(), Lote.id],
    )


def _obtener_lote(db: Session, lote_id: int) -> Lote:
    return obtener_o_404(db, Lote, lote_id, "Lote no encontrado")


def _validar_presentacion_almacen(db: Session, presentacion_id: int, almacen_id: int) -> None:
    if not db.query(Presentacion.id).filter(Presentacion.id == presentacion_id).first():
        raise HTTPException(status_code=404, detail="La presentación indicada no existe")
    if not db.query(Almacen.id).filter(Almacen.id == almacen_id).first():
        raise HTTPException(status_code=404, detail="El almacén indicado no existe")


def ingresar_lote(data: LoteIngresoCreate, usuario_id: int | None, db: Session) -> Lote:
    """Entrada de stock: recarga (o crea) el lote y registra kardex de entrada."""
    _validar_presentacion_almacen(db, data.presentacion_id, data.almacen_id)

    lote = (
        db.query(Lote)
        .filter(
            Lote.presentacion_id == data.presentacion_id,
            Lote.almacen_id == data.almacen_id,
            Lote.numero_lote == (data.numero_lote or "").strip(),
        )
        .first()
    )
    if lote is None:
        lote = Lote(
            presentacion_id=data.presentacion_id,
            almacen_id=data.almacen_id,
            numero_lote=(data.numero_lote or "").strip(),
            fecha_vencimiento=data.fecha_vencimiento,
            cantidad_actual=Decimal("0"),
            costo_unitario=data.costo_unitario,
        )
        db.add(lote)
        db.flush()

    lote.cantidad_actual = (lote.cantidad_actual or Decimal("0")) + data.cantidad
    if data.fecha_vencimiento is not None:
        lote.fecha_vencimiento = data.fecha_vencimiento
    if data.costo_unitario and data.costo_unitario > 0:
        lote.costo_unitario = data.costo_unitario

    registrar_kardex(
        db, lote, "entrada", data.cantidad, lote.cantidad_actual,
        data.costo_unitario, "ingreso", lote.id, usuario_id,
        data.observacion or "Ingreso de stock",
    )
    db.commit()
    db.refresh(lote)
    return lote


def ajustar_lote(data: LoteAjusteCreate, usuario_id: int | None, db: Session) -> Lote:
    """Ajuste de inventario (conteo físico): fija la cantidad real del lote."""
    lote = _obtener_lote(db, data.lote_id)
    anterior = lote.cantidad_actual or Decimal("0")
    nueva = data.cantidad_nueva
    diferencia = nueva - anterior
    if diferencia == 0:
        raise HTTPException(
            status_code=400,
            detail=f"El lote ya tiene cantidad {nueva}; no hay diferencia que ajustar",
        )

    lote.cantidad_actual = nueva
    registrar_kardex(
        db, lote, "ajuste", abs(diferencia), nueva, lote.costo_unitario,
        "ajuste", lote.id, usuario_id,
        (data.observacion or "Ajuste de inventario")
        + f" ({'+' if diferencia > 0 else '-'}{abs(diferencia)})",
    )
    db.commit()
    db.refresh(lote)
    return lote


# ---------------------------------------------------------------------------
# Kardex (solo lectura)
# ---------------------------------------------------------------------------

def listar_kardex(
    db: Session,
    lote_id: int | None = None,
    almacen_id: int | None = None,
    tipo_movimiento: str | None = None,
    referencia_tipo: str | None = None,
    desde=None,
    hasta=None,
    skip: int = 0,
    limit: int = 50,
) -> dict:
    query = db.query(KardexMovimiento)
    if lote_id is not None:
        query = query.filter(KardexMovimiento.lote_id == lote_id)
    if almacen_id is not None:
        query = query.filter(KardexMovimiento.almacen_id == almacen_id)
    if tipo_movimiento:
        query = query.filter(KardexMovimiento.tipo_movimiento == tipo_movimiento)
    if referencia_tipo:
        query = query.filter(KardexMovimiento.referencia_tipo == referencia_tipo)
    if desde is not None:
        query = query.filter(KardexMovimiento.fecha >= desde)
    if hasta is not None:
        query = query.filter(KardexMovimiento.fecha < hasta)
    return paginar(
        query, skip, limit,
        [KardexMovimiento.fecha.desc(), KardexMovimiento.id.desc()],
    )


def obtener_kardex_lote(lote_id: int, db: Session, skip: int = 0, limit: int = 50) -> dict:
    """Página de movimientos del lote ordenados del más reciente al más antiguo."""
    _obtener_lote(db, lote_id)
    query = db.query(KardexMovimiento).filter(KardexMovimiento.lote_id == lote_id)
    total = query.count()
    items = (
        query.order_by(KardexMovimiento.fecha.desc(), KardexMovimiento.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"total": total, "items": items}
