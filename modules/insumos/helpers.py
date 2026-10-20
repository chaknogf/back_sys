"""Patrones compartidos por los servicios del módulo de insumos.

Aquí vive todo lo que estaba copiado en los tres servicios: obtener-o-404,
validar existencia de FKs, paginado de listas, numeración de documentos,
verificación de stock y movimientos de cantidad con kardex.
"""

from decimal import Decimal
from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Query, Session

from modules.insumos.models import KardexMovimiento, Lote


# ---------------------------------------------------------------------------
# Obtención / validación de entidades
# ---------------------------------------------------------------------------

def obtener_o_404(db: Session, model, pk: int, mensaje: str):
    """Devuelve la fila con `pk` o lanza 404 con `mensaje`."""
    obj = db.query(model).filter(model.id == pk).first()
    if not obj:
        raise HTTPException(status_code=404, detail=mensaje)
    return obj


def validar_existe(db: Session, model, pk: int, mensaje: str) -> None:
    """Verifica que exista la FK `pk`; no carga el objeto."""
    if not db.query(model.id).filter(model.id == pk).first():
        raise HTTPException(status_code=404, detail=mensaje)


# ---------------------------------------------------------------------------
# Paginado de listas
# ---------------------------------------------------------------------------

def paginar(query: Query, skip: int, limit: int, order_by=None) -> dict:
    """Devuelve `{total, items}` con el total antes de paginar."""
    total = query.count()
    if order_by is not None:
        query = query.order_by(*order_by) if isinstance(order_by, (list, tuple)) else query.order_by(order_by)
    items = query.offset(skip).limit(limit).all()
    return {"total": total, "items": items}


# ---------------------------------------------------------------------------
# Numeración de documentos (REQ/DES/UNI-YYYY-NNNNNN)
# ---------------------------------------------------------------------------

def _formato_numero(prefijo: str, obj_id: int) -> str:
    return f"{prefijo}-{date.today().year}-{obj_id:06d}"


def asignar_numero(db: Session, obj, prefijo: str) -> str:
    """Asigna `obj.numero` con el correlativo derivado de su ID (ya hace flush)."""
    db.flush()
    obj.numero = _formato_numero(prefijo, obj.id)
    return obj.numero


def resolver_numero(
    db: Session, obj, numero: str | None, prefijo: str, model, etiqueta: str
) -> None:
    """Número manual (validando duplicado 409) o correlativo automático.

    Hace el flush necesario para conocer el ID de `obj` y, en el caso manual,
    conoce el ID para excluirse a sí mismo del chequeo de duplicado.
    """
    numero = (numero or "").strip()
    if numero:
        db.flush()
        otro = (
            db.query(model.id)
            .filter(model.numero == numero, model.id != obj.id)
            .first()
        )
        if otro:
            db.rollback()
            raise HTTPException(
                status_code=409, detail=f"Ya existe {etiqueta} número '{numero}'"
            )
        obj.numero = numero
    else:
        asignar_numero(db, obj, prefijo)


# ---------------------------------------------------------------------------
# Stock y movimientos de cantidad
# ---------------------------------------------------------------------------

def cargar_lotes(db: Session, lotes_ids) -> dict[int, Lote]:
    """Carga en un solo query los lotes por ID -> {id: Lote}."""
    return {
        l.id: l
        for l in db.query(Lote).filter(Lote.id.in_(lotes_ids)).all()
    }


def verificar_stock(
    lotes: dict[int, Lote], detalles, almacen_id: int | None = None
) -> None:
    """Valida lote existe, pertenece al almacén y hay stock; lanza 404/400.

    Recolecta todos los faltantes antes de fallar para dar un mensaje completo.
    """
    faltantes = []
    for det in detalles:
        lote = lotes.get(det.lote_id)
        if lote is None:
            raise HTTPException(status_code=404, detail=f"Lote {det.lote_id} no encontrado")
        if almacen_id is not None and lote.almacen_id != almacen_id:
            raise HTTPException(
                status_code=400,
                detail=f"El lote {lote.id} no pertenece al almacén {almacen_id}",
            )
        if (lote.cantidad_actual or Decimal("0")) < det.cantidad:
            faltantes.append(
                f"lote {lote.id}: disponible {lote.cantidad_actual}, solicitado {det.cantidad}"
            )
    if faltantes:
        raise HTTPException(
            status_code=400, detail="Stock insuficiente — " + "; ".join(faltantes)
        )


def registrar_kardex(
    db: Session,
    lote: Lote,
    tipo: str,
    cantidad: Decimal,
    saldo: Decimal,
    costo: Decimal,
    ref_tipo: str | None,
    ref_id: int | None,
    usuario_id: int | None,
    observacion: str = "",
) -> KardexMovimiento:
    movimiento = KardexMovimiento(
        lote_id=lote.id,
        almacen_id=lote.almacen_id,
        tipo_movimiento=tipo,
        cantidad=cantidad,
        saldo_resultante=saldo,
        costo_unitario=costo,
        referencia_tipo=ref_tipo,
        referencia_id=ref_id,
        observacion=observacion or "",
        usuario_id=usuario_id,
    )
    db.add(movimiento)
    return movimiento


def descontar_lote(
    db: Session,
    lote: Lote,
    cantidad: Decimal,
    tipo: str,
    ref_tipo: str,
    ref_id: int | None,
    usuario_id: int | None,
    observacion: str = "",
    costo: Decimal | None = None,
) -> None:
    """Descuenta stock del lote y escribe el kardex correspondiente."""
    lote.cantidad_actual = (lote.cantidad_actual or Decimal("0")) - cantidad
    registrar_kardex(
        db, lote, tipo, cantidad, lote.cantidad_actual,
        costo if costo is not None else lote.costo_unitario,
        ref_tipo, ref_id, usuario_id, observacion,
    )


def recargar_lote(
    db: Session,
    lote: Lote,
    cantidad: Decimal,
    tipo: str,
    ref_tipo: str,
    ref_id: int | None,
    usuario_id: int | None,
    observacion: str = "",
    costo: Decimal | None = None,
) -> None:
    """Suma stock al lote y escribe el kardex correspondiente."""
    lote.cantidad_actual = (lote.cantidad_actual or Decimal("0")) + cantidad
    registrar_kardex(
        db, lote, tipo, cantidad, lote.cantidad_actual,
        costo if costo is not None else lote.costo_unitario,
        ref_tipo, ref_id, usuario_id, observacion,
    )
