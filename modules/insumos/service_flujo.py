"""Flujos operativos: requisiciones, despachos, atenciones y unidosis.

Cada operación que mueve stock descuenta/suma `lotes` y escribe su
`kardex_movimientos` con la referencia al documento que lo originó.
"""

from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from modules.insumos.models import (
    Almacen,
    Presentacion,
    Requisicion,
    RequisicionDetalle,
    Despacho,
    DespachoDetalle,
    Atencion,
    AtencionInsumo,
    Unidosis,
    UnidosisDetalle,
    Lote,
)
from modules.insumos.schemas import (
    RequisicionCreate,
    EstadoAccion,
    DespachoCreate,
    AtencionCreate,
    AtencionInsumoCreate,
    UnidosisCreate,
)
from modules.insumos.service_almacen import _obtener_lote
from modules.insumos.helpers import (
    cargar_lotes,
    descontar_lote,
    obtener_o_404,
    paginar,
    recargar_lote,
    resolver_numero,
    validar_existe,
    verificar_stock,
)

from modules.pacientes.models import PacienteModel
from modules.consultas.models import ConsultaModel
from modules.encamamiento.models import EncamamientoModel
from modules.medicos.models import MedicoModel  # tabla personal_atencion


# ---------------------------------------------------------------------------
# Requisiciones
# ---------------------------------------------------------------------------

def crear_requisicion(
    data: RequisicionCreate, usuario_id: int | None, db: Session
) -> Requisicion:
    validar_existe(db, EncamamientoModel, data.servicio_solicitante_id, "El servicio indicado no existe")
    if data.personal_solicita_id is not None:
        validar_existe(db, MedicoModel, data.personal_solicita_id, "El personal indicado no existe")

    req = Requisicion(
        numero=" ",
        servicio_solicitante_id=data.servicio_solicitante_id,
        personal_solicita_id=data.personal_solicita_id,
        usuario_solicita_id=usuario_id,
        estado="pendiente",
        observaciones=data.observaciones or "",
    )
    db.add(req)
    resolver_numero(db, req, data.numero, "REQ", Requisicion, "una requisición")

    for det in data.detalles:
        validar_existe(
            db, Presentacion, det.presentacion_id,
            f"La presentación {det.presentacion_id} indicada no existe",
        )
        db.add(RequisicionDetalle(
            requisicion_id=req.id,
            presentacion_id=det.presentacion_id,
            cantidad_solicitada=det.cantidad_solicitada,
        ))

    db.commit()
    db.refresh(req)
    return req


def listar_requisiciones(
    db: Session,
    estado: str | None = None,
    servicio_id: int | None = None,
    numero: str | None = None,
    activo: bool | None = True,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    query = db.query(Requisicion)
    if activo is not None:
        query = query.filter(Requisicion.activo == activo)
    if estado:
        query = query.filter(Requisicion.estado == estado)
    if servicio_id is not None:
        query = query.filter(Requisicion.servicio_solicitante_id == servicio_id)
    if numero:
        query = query.filter(Requisicion.numero.ilike(f"%{numero.strip()}%"))
    return paginar(query, skip, limit, Requisicion.id.desc())


def obtener_requisicion(requisicion_id: int, db: Session) -> Requisicion:
    return obtener_o_404(db, Requisicion, requisicion_id, "Requisición no encontrada")


def _cambiar_estado_requisicion(
    requisicion_id: int, nuevo_estado: str, usuario_id: int | None,
    data: EstadoAccion | None, db: Session,
) -> Requisicion:
    req = obtener_requisicion(requisicion_id, db)
    if req.estado != "pendiente":
        raise HTTPException(
            status_code=400,
            detail=f"La requisición está en estado '{req.estado}'; solo puede cambiarse desde 'pendiente'",
        )
    req.estado = nuevo_estado
    if data and data.observaciones:
        nota = f"[{nuevo_estado.upper()}] {data.observaciones.strip()}"
        req.observaciones = (req.observaciones + "\n" + nota).strip()
    if nuevo_estado == "aprobada":
        req.fecha_aprobacion = func.now()
        req.usuario_aprueba_id = usuario_id
    db.commit()
    db.refresh(req)
    return req


def aprobar_requisicion(
    requisicion_id: int, usuario_id: int | None, data: EstadoAccion | None, db: Session
) -> Requisicion:
    return _cambiar_estado_requisicion(requisicion_id, "aprobada", usuario_id, data, db)


def rechazar_requisicion(
    requisicion_id: int, usuario_id: int | None, data: EstadoAccion | None, db: Session
) -> Requisicion:
    return _cambiar_estado_requisicion(requisicion_id, "rechazada", usuario_id, data, db)


# ---------------------------------------------------------------------------
# Despachos
# ---------------------------------------------------------------------------

def _validar_destino(data: DespachoCreate) -> None:
    if data.tipo == "traslado" and data.almacen_destino_id is None:
        raise HTTPException(status_code=400, detail="El traslado requiere almacén destino")
    if data.tipo == "servicio" and data.servicio_destino_id is None:
        raise HTTPException(status_code=400, detail="El despacho a servicio requiere servicio destino")
    if data.tipo == "paciente" and data.paciente_id is None:
        raise HTTPException(status_code=400, detail="El despacho a paciente requiere paciente")


def crear_despacho(data: DespachoCreate, usuario_id: int | None, db: Session) -> Despacho:
    """Crea el despacho en estado 'borrador' (sin mover stock todavía)."""
    _validar_destino(data)
    validar_existe(db, Almacen, data.almacen_origen_id, "El almacén origen no existe")

    if data.tipo == "traslado":
        validar_existe(db, Almacen, data.almacen_destino_id, "El almacén destino no existe")
        if data.almacen_destino_id == data.almacen_origen_id:
            raise HTTPException(status_code=400, detail="Origen y destino deben ser distintos")
    if data.servicio_destino_id is not None:
        validar_existe(db, EncamamientoModel, data.servicio_destino_id, "El servicio indicado no existe")
    if data.paciente_id is not None:
        validar_existe(db, PacienteModel, data.paciente_id, "El paciente indicado no existe")
    if data.personal_receptor_id is not None:
        validar_existe(db, MedicoModel, data.personal_receptor_id, "El personal receptor no existe")

    req = None
    if data.requisicion_id is not None:
        req = obtener_o_404(db, Requisicion, data.requisicion_id, "La requisición indicada no existe")
        if req.estado not in ("aprobada", "despachada"):
            raise HTTPException(
                status_code=400,
                detail=f"La requisición está '{req.estado}'; debe estar aprobada para despachar",
            )

    despacho = Despacho(
        numero=" ",
        tipo=data.tipo,
        almacen_origen_id=data.almacen_origen_id,
        almacen_destino_id=data.almacen_destino_id,
        requisicion_id=data.requisicion_id,
        servicio_destino_id=data.servicio_destino_id,
        paciente_id=data.paciente_id,
        personal_receptor_id=data.personal_receptor_id,
        usuario_despacha_id=usuario_id,
        estado="borrador",
        observaciones=data.observaciones or "",
    )
    db.add(despacho)
    resolver_numero(db, despacho, data.numero, "DES", Despacho, "un despacho")

    vistos: set[int] = set()
    for det in data.detalles:
        if det.lote_id in vistos:
            db.rollback()
            raise HTTPException(status_code=400, detail="Lote repetido en los detalles")
        vistos.add(det.lote_id)
        lote = _obtener_lote(db, det.lote_id)
        if lote.almacen_id != despacho.almacen_origen_id:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=(
                    f"El lote {lote.id} pertenece al almacén {lote.almacen_id}, "
                    f"no al origen {despacho.almacen_origen_id}"
                ),
            )
        if (lote.cantidad_actual or Decimal("0")) < det.cantidad:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente en lote {lote.id}: "
                       f"disponible {lote.cantidad_actual}, solicitado {det.cantidad}",
            )
        db.add(DespachoDetalle(
            despacho_id=despacho.id,
            lote_id=det.lote_id,
            cantidad=det.cantidad,
            costo_unitario=det.costo_unitario or lote.costo_unitario,
        ))

    db.commit()
    db.refresh(despacho)
    return despacho


def _trasladar_a_destino(
    db: Session, despacho: Despacho, lote: Lote, cantidad: Decimal,
    costo: Decimal, usuario_id: int | None,
) -> None:
    """Entrada del stock trasladado en el almacén destino (crea lote si falta)."""
    lote_destino = (
        db.query(Lote)
        .filter(
            Lote.presentacion_id == lote.presentacion_id,
            Lote.almacen_id == despacho.almacen_destino_id,
            Lote.numero_lote == lote.numero_lote,
        )
        .first()
    )
    if lote_destino is None:
        lote_destino = Lote(
            presentacion_id=lote.presentacion_id,
            almacen_id=despacho.almacen_destino_id,
            numero_lote=lote.numero_lote,
            fecha_vencimiento=lote.fecha_vencimiento,
            cantidad_actual=Decimal("0"),
            costo_unitario=lote.costo_unitario,
        )
        db.add(lote_destino)
        db.flush()
    recargar_lote(
        db, lote_destino, cantidad, "entrada", "despacho", despacho.id, usuario_id,
        f"Traslado {despacho.numero} → almacén {despacho.almacen_destino_id}", costo,
    )


def despachar_despacho(despacho_id: int, usuario_id: int | None, db: Session) -> Despacho:
    """Ejecuta el despacho: descuenta lotes, escribe kardex y cierra requisición."""
    despacho = obtener_o_404(db, Despacho, despacho_id, "Despacho no encontrado")
    if despacho.estado != "borrador":
        raise HTTPException(
            status_code=400,
            detail=f"El despacho está en estado '{despacho.estado}'; solo se ejecuta desde 'borrador'",
        )

    req = None
    if despacho.requisicion_id is not None:
        req = obtener_o_404(db, Requisicion, despacho.requisicion_id, "La requisición no existe")
        if req.estado not in ("aprobada", "despachada"):
            raise HTTPException(
                status_code=400,
                detail=f"La requisición está '{req.estado}'; debe estar aprobada",
            )

    detalles = despacho.detalles
    if not detalles:
        raise HTTPException(status_code=400, detail="El despacho no tiene detalles")

    lotes = cargar_lotes(db, [d.lote_id for d in detalles])
    verificar_stock(lotes, detalles, despacho.almacen_origen_id)

    acumulado: dict[int, Decimal] = {}
    for det in detalles:
        lote = lotes[det.lote_id]
        descontar_lote(
            db, lote, det.cantidad, "salida", "despacho", despacho.id, usuario_id,
            f"Despacho {despacho.numero}", det.costo_unitario,
        )
        acumulado[lote.presentacion_id] = (
            acumulado.get(lote.presentacion_id, Decimal("0")) + det.cantidad
        )
        if despacho.tipo == "traslado":
            _trasladar_a_destino(db, despacho, lote, det.cantidad, det.costo_unitario, usuario_id)

    despacho.estado = "despachado"
    if usuario_id is not None:
        despacho.usuario_despacha_id = usuario_id

    if req is not None:
        for rd in req.detalles:
            if rd.presentacion_id in acumulado:
                rd.cantidad_despachada = (
                    (rd.cantidad_despachada or Decimal("0")) + acumulado[rd.presentacion_id]
                )
        if all(
            (rd.cantidad_despachada or Decimal("0")) >= rd.cantidad_solicitada
            for rd in req.detalles
        ):
            req.estado = "despachada"

    db.commit()
    db.refresh(despacho)
    return despacho


def anular_despacho(despacho_id: int, db: Session) -> Despacho:
    """Anula un despacho; solo si no se ejecutó (borrador) para no tocar stock."""
    despacho = obtener_o_404(db, Despacho, despacho_id, "Despacho no encontrado")
    if despacho.estado != "borrador":
        raise HTTPException(
            status_code=400,
            detail="Solo se anulan despachos en borrador; el despacho ejecutado ya movió stock",
        )
    despacho.estado = "anulado"
    despacho.activo = False
    db.commit()
    db.refresh(despacho)
    return despacho


def listar_despachos(
    db: Session,
    tipo: str | None = None,
    estado: str | None = None,
    almacen_origen_id: int | None = None,
    servicio_id: int | None = None,
    paciente_id: int | None = None,
    numero: str | None = None,
    activo: bool | None = True,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    query = db.query(Despacho)
    if activo is not None:
        query = query.filter(Despacho.activo == activo)
    if tipo:
        query = query.filter(Despacho.tipo == tipo)
    if estado:
        query = query.filter(Despacho.estado == estado)
    if almacen_origen_id is not None:
        query = query.filter(Despacho.almacen_origen_id == almacen_origen_id)
    if servicio_id is not None:
        query = query.filter(Despacho.servicio_destino_id == servicio_id)
    if paciente_id is not None:
        query = query.filter(Despacho.paciente_id == paciente_id)
    if numero:
        query = query.filter(Despacho.numero.ilike(f"%{numero.strip()}%"))
    return paginar(query, skip, limit, Despacho.id.desc())


def obtener_despacho(despacho_id: int, db: Session) -> Despacho:
    return obtener_o_404(db, Despacho, despacho_id, "Despacho no encontrado")


# ---------------------------------------------------------------------------
# Atenciones + consumo de insumos
# ---------------------------------------------------------------------------

def crear_atencion(data: AtencionCreate, db: Session) -> Atencion:
    validar_existe(db, PacienteModel, data.paciente_id, "El paciente indicado no existe")
    if data.consulta_id is not None:
        validar_existe(db, ConsultaModel, data.consulta_id, "La consulta indicada no existe")
    if data.servicio_id is not None:
        validar_existe(db, EncamamientoModel, data.servicio_id, "El servicio indicado no existe")
    if data.personal_atencion_id is not None:
        validar_existe(db, MedicoModel, data.personal_atencion_id, "El personal indicado no existe")

    atencion = Atencion(
        paciente_id=data.paciente_id,
        personal_atencion_id=data.personal_atencion_id,
        servicio_id=data.servicio_id,
        consulta_id=data.consulta_id,
        observaciones=data.observaciones or "",
    )
    db.add(atencion)
    db.commit()
    db.refresh(atencion)
    return atencion


def listar_atenciones(
    db: Session,
    paciente_id: int | None = None,
    estado: str | None = None,
    servicio_id: int | None = None,
    consulta_id: int | None = None,
    desde=None,
    hasta=None,
    activo: bool | None = True,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    query = db.query(Atencion)
    if activo is not None:
        query = query.filter(Atencion.activo == activo)
    if paciente_id is not None:
        query = query.filter(Atencion.paciente_id == paciente_id)
    if estado:
        query = query.filter(Atencion.estado == estado)
    if servicio_id is not None:
        query = query.filter(Atencion.servicio_id == servicio_id)
    if consulta_id is not None:
        query = query.filter(Atencion.consulta_id == consulta_id)
    if desde is not None:
        query = query.filter(Atencion.fecha >= desde)
    if hasta is not None:
        query = query.filter(Atencion.fecha < hasta)
    return paginar(query, skip, limit, [Atencion.fecha.desc(), Atencion.id.desc()])


def obtener_atencion(atencion_id: int, db: Session) -> Atencion:
    return obtener_o_404(db, Atencion, atencion_id, "Atención no encontrada")


def finalizar_atencion(atencion_id: int, db: Session) -> Atencion:
    atencion = obtener_atencion(atencion_id, db)
    if atencion.estado != "abierta":
        raise HTTPException(
            status_code=400,
            detail=f"La atención está en estado '{atencion.estado}'; solo se finaliza desde 'abierta'",
        )
    atencion.estado = "finalizada"
    db.commit()
    db.refresh(atencion)
    return atencion


def registrar_insumo_atencion(
    atencion_id: int, data: AtencionInsumoCreate, usuario_id: int | None, db: Session
) -> AtencionInsumo:
    """Descuenta stock del lote y registra el consumo en la atención (kardex)."""
    atencion = obtener_atencion(atencion_id, db)
    if atencion.estado != "abierta":
        raise HTTPException(
            status_code=400,
            detail=f"La atención está '{atencion.estado}'; solo se consume con atención abierta",
        )
    if data.origen == "despacho":
        if data.despacho_id is None:
            raise HTTPException(
                status_code=400, detail="origen='despacho' requiere despacho_id"
            )
        validar_existe(db, Despacho, data.despacho_id, "El despacho indicado no existe")

    lote = _obtener_lote(db, data.lote_id)
    verificar_stock({lote.id: lote}, [data])

    descontar_lote(
        db, lote, data.cantidad, "consumo", "atencion", atencion.id, usuario_id,
        f"Consumo en atención #{atencion.id}",
    )
    registro = AtencionInsumo(
        atencion_id=atencion.id,
        lote_id=lote.id,
        despacho_id=data.despacho_id,
        cantidad=data.cantidad,
        origen=data.origen,
        usuario_id=usuario_id,
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


# ---------------------------------------------------------------------------
# Unidosis (preparación de dosis unitarias desde farmacia)
# ---------------------------------------------------------------------------

def crear_unidosis(data: UnidosisCreate, usuario_id: int | None, db: Session) -> Unidosis:
    """Prepara la unidosis: descuenta farmacia (kardex consumo) al momento de crear."""
    validar_existe(db, PacienteModel, data.paciente_id, "El paciente indicado no existe")
    validar_existe(db, Almacen, data.almacen_origen_id, "El almacén indicado no existe")
    if data.atencion_id is not None:
        validar_existe(db, Atencion, data.atencion_id, "La atención indicada no existe")
    if data.personal_prepara_id is not None:
        validar_existe(db, MedicoModel, data.personal_prepara_id, "El personal indicado no existe")

    lotes = cargar_lotes(db, [d.lote_id for d in data.detalles])
    verificar_stock(lotes, data.detalles, data.almacen_origen_id)

    uni = Unidosis(
        paciente_id=data.paciente_id,
        atencion_id=data.atencion_id,
        almacen_origen_id=data.almacen_origen_id,
        personal_prepara_id=data.personal_prepara_id,
        usuario_prepara_id=usuario_id,
        estado="preparada",
        observaciones=data.observaciones or "",
    )
    db.add(uni)
    resolver_numero(db, uni, data.numero, "UNI", Unidosis, "una unidosis")

    for det in data.detalles:
        lote = lotes[det.lote_id]
        descontar_lote(
            db, lote, det.cantidad, "consumo", "unidosis", uni.id, usuario_id,
            f"Preparación de unidosis {uni.numero}",
        )
        db.add(UnidosisDetalle(
            unidosis_id=uni.id,
            lote_id=det.lote_id,
            cantidad=det.cantidad,
            dosis=det.dosis or "",
        ))

    db.commit()
    db.refresh(uni)
    return uni


def listar_unidosis(
    db: Session,
    paciente_id: int | None = None,
    estado: str | None = None,
    almacen_id: int | None = None,
    numero: str | None = None,
    activo: bool | None = True,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    query = db.query(Unidosis)
    if activo is not None:
        query = query.filter(Unidosis.activo == activo)
    if paciente_id is not None:
        query = query.filter(Unidosis.paciente_id == paciente_id)
    if estado:
        query = query.filter(Unidosis.estado == estado)
    if almacen_id is not None:
        query = query.filter(Unidosis.almacen_origen_id == almacen_id)
    if numero:
        query = query.filter(Unidosis.numero.ilike(f"%{numero.strip()}%"))
    return paginar(query, skip, limit, Unidosis.id.desc())


def obtener_unidosis(unidosis_id: int, db: Session) -> Unidosis:
    return obtener_o_404(db, Unidosis, unidosis_id, "Unidosis no encontrada")


def administrar_unidosis(unidosis_id: int, db: Session) -> Unidosis:
    uni = obtener_unidosis(unidosis_id, db)
    if uni.estado != "preparada":
        raise HTTPException(
            status_code=400,
            detail=f"La unidosis está '{uni.estado}'; solo se administra desde 'preparada'",
        )
    uni.estado = "administrada"
    for det in uni.detalles:
        det.fecha_administracion = func.now()
    db.commit()
    db.refresh(uni)
    return uni


def cancelar_unidosis(unidosis_id: int, usuario_id: int | None, db: Session) -> Unidosis:
    """Cancela la unidosis preparada y devuelve el stock a farmacia (kardex entrada)."""
    uni = obtener_unidosis(unidosis_id, db)
    if uni.estado != "preparada":
        raise HTTPException(
            status_code=400,
            detail=f"La unidosis está '{uni.estado}'; solo se cancela desde 'preparada'",
        )

    lotes = cargar_lotes(db, [d.lote_id for d in uni.detalles])
    for det in uni.detalles:
        lote = lotes.get(det.lote_id)
        if lote is None:
            raise HTTPException(status_code=404, detail=f"Lote {det.lote_id} no encontrado")
        recargar_lote(
            db, lote, det.cantidad, "entrada", "unidosis", uni.id, usuario_id,
            f"Devolución por cancelación de unidosis {uni.numero}",
        )

    uni.estado = "cancelada"
    db.commit()
    db.refresh(uni)
    return uni
