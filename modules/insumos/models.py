"""Modelos ORM del módulo de almacén de insumos.

Catálogo espejo del CSV de importación (insumos + presentaciones) y
operativas: almacenes, lotes (stock), kardex, requisiciones, despachos,
atenciones con consumo y unidosis. Espejo exacto de la migración 084.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from core.database import Base


class Insumo(Base):
    """Catálogo de insumos, 1 fila por CÓDIGO DE INSUMO (espejo CSV cols 1-4)."""

    __tablename__ = "insumos"

    id = Column(Integer, primary_key=True, index=True)
    renglon = Column(String(3), nullable=False, index=True)
    codigo_insumo = Column(String(20), nullable=False, unique=True, index=True)
    nombre = Column(Text, nullable=False)
    # Texto crudo del CSV ("Estado: X;  Grado: Y;  Uso: Z;"); parseo a JSONB pendiente.
    caracteristicas = Column(Text, nullable=False, server_default="")
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

    presentaciones = relationship(
        "Presentacion", back_populates="insumo", lazy="selectin",
    )


class Presentacion(Base):
    """Presentación de un insumo, 1 fila por CÓDIGO DE PRESENTACIÓN (cols 5-7)."""

    __tablename__ = "presentaciones"

    id = Column(Integer, primary_key=True, index=True)
    insumo_id = Column(
        Integer, ForeignKey("insumos.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    nombre = Column(String(50), nullable=False, default="Envase")
    # Texto crudo del CSV ("250 Mililitro"); NO es stock, el stock es de lotes.
    cantidad_unidad = Column(Text, nullable=False, server_default="")
    codigo_presentacion = Column(String(20), nullable=False, unique=True, index=True)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

    insumo = relationship("Insumo", back_populates="presentaciones")


class Almacen(Base):
    """Áreas de almacenamiento: bodega, farmacia, productos afines o servicio."""

    __tablename__ = "almacenes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), nullable=False, unique=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    tipo = Column(String(20), nullable=False, default="bodega")
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )


class Lote(Base):
    """Stock real por presentación, almacén y número de lote."""

    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True, index=True)
    presentacion_id = Column(
        Integer, ForeignKey("presentaciones.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    almacen_id = Column(
        Integer, ForeignKey("almacenes.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    numero_lote = Column(String(50), nullable=False, default="")
    fecha_vencimiento = Column(Date)
    cantidad_actual = Column(Numeric(14, 3), nullable=False, default=0)
    costo_unitario = Column(Numeric(12, 4), nullable=False, default=0)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

    presentacion = relationship("Presentacion", lazy="joined")
    almacen = relationship("Almacen", lazy="joined")


class KardexMovimiento(Base):
    """Libro mayor de movimientos de stock (entrada/salida/traslado/consumo/ajuste)."""

    __tablename__ = "kardex_movimientos"

    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(
        Integer, ForeignKey("lotes.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    almacen_id = Column(
        Integer, ForeignKey("almacenes.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    tipo_movimiento = Column(String(10), nullable=False, index=True)
    cantidad = Column(Numeric(14, 3), nullable=False)
    saldo_resultante = Column(Numeric(14, 3), nullable=False, default=0)
    costo_unitario = Column(Numeric(12, 4), nullable=False, default=0)
    referencia_tipo = Column(String(20))
    referencia_id = Column(Integer)
    observacion = Column(Text, nullable=False, server_default="")
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    fecha = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    lote = relationship("Lote", lazy="joined")
    almacen = relationship("Almacen", lazy="joined")


class Requisicion(Base):
    """Requisición de un servicio: pendiente → aprobada/rechazada → despachada."""

    __tablename__ = "requisiciones"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, unique=True, index=True)
    servicio_solicitante_id = Column(
        Integer, ForeignKey("encamamiento.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    personal_solicita_id = Column(
        Integer, ForeignKey("personal_atencion.id", ondelete="SET NULL"),
    )
    usuario_solicita_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    estado = Column(String(12), nullable=False, default="pendiente", index=True)
    observaciones = Column(Text, nullable=False, server_default="")
    usuario_aprueba_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    fecha_aprobacion = Column(DateTime(timezone=True))
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

    detalles = relationship(
        "RequisicionDetalle", back_populates="requisicion",
        lazy="selectin", cascade="all, delete-orphan",
    )


class RequisicionDetalle(Base):
    """Línea de requisición: cantidad solicitada vs despachada por presentación."""

    __tablename__ = "requisiciones_detalles"

    id = Column(Integer, primary_key=True, index=True)
    requisicion_id = Column(
        Integer, ForeignKey("requisiciones.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    presentacion_id = Column(
        Integer, ForeignKey("presentaciones.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    cantidad_solicitada = Column(Numeric(14, 3), nullable=False)
    cantidad_despachada = Column(Numeric(14, 3), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    requisicion = relationship("Requisicion", back_populates="detalles")
    presentacion = relationship("Presentacion", lazy="joined")


class Despacho(Base):
    """Salida de un almacén hacia un servicio, un paciente o traslado a otro almacén."""

    __tablename__ = "despachos"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, unique=True, index=True)
    tipo = Column(String(10), nullable=False, default="servicio")
    almacen_origen_id = Column(
        Integer, ForeignKey("almacenes.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    almacen_destino_id = Column(
        Integer, ForeignKey("almacenes.id", ondelete="RESTRICT"),
    )
    requisicion_id = Column(
        Integer, ForeignKey("requisiciones.id", ondelete="SET NULL"),
        index=True,
    )
    servicio_destino_id = Column(
        Integer, ForeignKey("encamamiento.id", ondelete="SET NULL"),
        index=True,
    )
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="SET NULL"), index=True)
    personal_receptor_id = Column(
        Integer, ForeignKey("personal_atencion.id", ondelete="SET NULL"),
    )
    usuario_despacha_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    estado = Column(String(12), nullable=False, default="borrador", index=True)
    fecha = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    observaciones = Column(Text, nullable=False, server_default="")
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

    detalles = relationship(
        "DespachoDetalle", back_populates="despacho",
        lazy="selectin", cascade="all, delete-orphan",
    )
    requisicion = relationship("Requisicion", lazy="joined")


class DespachoDetalle(Base):
    """Línea de despacho con el lote exacto que descuenta (o que se traslada)."""

    __tablename__ = "despachos_detalles"

    id = Column(Integer, primary_key=True, index=True)
    despacho_id = Column(
        Integer, ForeignKey("despachos.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    lote_id = Column(
        Integer, ForeignKey("lotes.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    cantidad = Column(Numeric(14, 3), nullable=False)
    costo_unitario = Column(Numeric(12, 4), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    despacho = relationship("Despacho", back_populates="detalles")
    lote = relationship("Lote", lazy="joined")


class Atencion(Base):
    """Atención de un paciente que puede consumir insumos de stock."""

    __tablename__ = "atenciones"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(
        Integer, ForeignKey("pacientes.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    personal_atencion_id = Column(
        Integer, ForeignKey("personal_atencion.id", ondelete="SET NULL"),
    )
    servicio_id = Column(
        Integer, ForeignKey("encamamiento.id", ondelete="SET NULL"),
        index=True,
    )
    consulta_id = Column(Integer, ForeignKey("consultas.id", ondelete="SET NULL"), index=True)
    estado = Column(String(12), nullable=False, default="abierta", index=True)
    fecha = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    observaciones = Column(Text, nullable=False, server_default="")
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

    insumos_consumidos = relationship(
        "AtencionInsumo", back_populates="atencion", lazy="selectin",
    )


class AtencionInsumo(Base):
    """Insumo consumido en una atención (origen: despacho o descuento directo)."""

    __tablename__ = "atenciones_insumos"

    id = Column(Integer, primary_key=True, index=True)
    atencion_id = Column(
        Integer, ForeignKey("atenciones.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    lote_id = Column(
        Integer, ForeignKey("lotes.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    despacho_id = Column(
        Integer, ForeignKey("despachos.id", ondelete="SET NULL"),
    )
    cantidad = Column(Numeric(14, 3), nullable=False)
    origen = Column(String(10), nullable=False, default="directo")
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    fecha = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    atencion = relationship("Atencion", back_populates="insumos_consumidos")
    lote = relationship("Lote", lazy="joined")


class Unidosis(Base):
    """Dosis unitaria preparada por paciente desde la farmacia."""

    __tablename__ = "unidosis"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True)
    paciente_id = Column(
        Integer, ForeignKey("pacientes.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    atencion_id = Column(
        Integer, ForeignKey("atenciones.id", ondelete="SET NULL"),
        index=True,
    )
    almacen_origen_id = Column(
        Integer, ForeignKey("almacenes.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    personal_prepara_id = Column(
        Integer, ForeignKey("personal_atencion.id", ondelete="SET NULL"),
    )
    usuario_prepara_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    estado = Column(String(12), nullable=False, default="preparada", index=True)
    fecha = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    observaciones = Column(Text, nullable=False, server_default="")
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

    detalles = relationship(
        "UnidosisDetalle", back_populates="unidosis",
        lazy="selectin", cascade="all, delete-orphan",
    )


class UnidosisDetalle(Base):
    """Línea de unidosis: lote descontado de farmacia y dosis pautada."""

    __tablename__ = "unidosis_detalles"

    id = Column(Integer, primary_key=True, index=True)
    unidosis_id = Column(
        Integer, ForeignKey("unidosis.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    lote_id = Column(
        Integer, ForeignKey("lotes.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    cantidad = Column(Numeric(14, 3), nullable=False)
    dosis = Column(String(100), nullable=False, server_default="")
    fecha_administracion = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    unidosis = relationship("Unidosis", back_populates="detalles")
    lote = relationship("Lote", lazy="joined")
