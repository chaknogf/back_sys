"""Esquemas Pydantic del módulo de almacén de insumos."""

from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Catálogo: insumos y presentaciones (espejo CSV)
# ---------------------------------------------------------------------------

class InsumoBase(BaseModel):
    renglon: str = Field(min_length=1, max_length=3, description="Renglón presupuestal, ej. 261/011")
    codigo_insumo: str = Field(min_length=1, max_length=20)
    nombre: str = Field(min_length=1)
    caracteristicas: Optional[str] = Field(
        default="", description="Texto crudo del CSV: 'Estado: X;  Grado: Y;  Uso: Z;'"
    )
    activo: Optional[bool] = True


class InsumoCreate(InsumoBase):
    pass


class InsumoUpdate(BaseModel):
    renglon: Optional[str] = Field(default=None, min_length=1, max_length=3)
    codigo_insumo: Optional[str] = Field(default=None, min_length=1, max_length=20)
    nombre: Optional[str] = Field(default=None, min_length=1)
    caracteristicas: Optional[str] = None
    activo: Optional[bool] = None


class Insumo(InsumoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InsumoDetalle(Insumo):
    presentaciones: List["Presentacion"] = []


class InsumoListResponse(BaseModel):
    total: int
    items: List[Insumo]

    model_config = ConfigDict(from_attributes=True)


class PresentacionBase(BaseModel):
    insumo_id: int
    nombre: str = Field(default="Envase", max_length=50)
    cantidad_unidad: Optional[str] = Field(
        default="", description="Texto crudo del CSV, ej. '250 Mililitro'"
    )
    codigo_presentacion: str = Field(min_length=1, max_length=20)
    activo: Optional[bool] = True


class PresentacionCreate(PresentacionBase):
    pass


class PresentacionUpdate(BaseModel):
    insumo_id: Optional[int] = None
    nombre: Optional[str] = Field(default=None, max_length=50)
    cantidad_unidad: Optional[str] = None
    codigo_presentacion: Optional[str] = Field(default=None, min_length=1, max_length=20)
    activo: Optional[bool] = None


class Presentacion(PresentacionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PresentacionListResponse(BaseModel):
    total: int
    items: List[Presentacion]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Importación CSV
# ---------------------------------------------------------------------------

class ImportarCsvFilaError(BaseModel):
    fila: int
    error: str


class ImportarCsvResultado(BaseModel):
    filas: int
    insumos_creados: int
    insumos_actualizados: int
    presentaciones_creadas: int
    presentaciones_actualizadas: int
    errores: List[ImportarCsvFilaError] = []


# ---------------------------------------------------------------------------
# Almacenes, lotes y kardex
# ---------------------------------------------------------------------------

class AlmacenBase(BaseModel):
    codigo: str = Field(min_length=1, max_length=20)
    nombre: str = Field(min_length=1, max_length=100)
    tipo: str = Field(
        default="bodega",
        pattern="^(bodega|farmacia|productos_afines|servicio)$",
    )
    activo: Optional[bool] = True


class AlmacenCreate(AlmacenBase):
    pass


class AlmacenUpdate(BaseModel):
    codigo: Optional[str] = Field(default=None, min_length=1, max_length=20)
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    tipo: Optional[str] = Field(
        default=None, pattern="^(bodega|farmacia|productos_afines|servicio)$"
    )
    activo: Optional[bool] = None


class Almacen(AlmacenBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlmacenListResponse(BaseModel):
    total: int
    items: List[Almacen]

    model_config = ConfigDict(from_attributes=True)


class LoteOut(BaseModel):
    id: int
    presentacion_id: int
    almacen_id: int
    numero_lote: str
    fecha_vencimiento: Optional[date] = None
    cantidad_actual: Decimal
    costo_unitario: Decimal
    activo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoteListResponse(BaseModel):
    total: int
    items: List[LoteOut]

    model_config = ConfigDict(from_attributes=True)


class LoteIngresoCreate(BaseModel):
    """Ingreso de stock a un almacén: crea o recarga el lote y escribe kardex."""

    presentacion_id: int
    almacen_id: int
    numero_lote: str = Field(default="", max_length=50)
    fecha_vencimiento: Optional[date] = None
    cantidad: Decimal = Field(gt=0)
    costo_unitario: Decimal = Field(default=Decimal("0"), ge=0)
    observacion: Optional[str] = ""


class LoteAjusteCreate(BaseModel):
    """Ajuste de inventario: fija la cantidad real del lote (alta o baja)."""

    lote_id: int
    cantidad_nueva: Decimal = Field(ge=0)
    observacion: Optional[str] = ""


class KardexOut(BaseModel):
    id: int
    lote_id: int
    almacen_id: int
    tipo_movimiento: str
    cantidad: Decimal
    saldo_resultante: Decimal
    costo_unitario: Decimal
    referencia_tipo: Optional[str] = None
    referencia_id: Optional[int] = None
    observacion: str
    usuario_id: Optional[int] = None
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)


class KardexListResponse(BaseModel):
    total: int
    items: List[KardexOut]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Requisiciones
# ---------------------------------------------------------------------------

class RequisicionDetalleBase(BaseModel):
    presentacion_id: int
    cantidad_solicitada: Decimal = Field(gt=0)


class RequisicionDetalleCreate(RequisicionDetalleBase):
    pass


class RequisicionDetalle(RequisicionDetalleBase):
    id: int
    cantidad_despachada: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RequisicionCreate(BaseModel):
    servicio_solicitante_id: int
    numero: Optional[str] = Field(default=None, max_length=20)
    personal_solicita_id: Optional[int] = None
    observaciones: Optional[str] = ""
    detalles: List[RequisicionDetalleCreate] = Field(min_length=1)


class RequisicionOut(BaseModel):
    id: int
    numero: str
    servicio_solicitante_id: int
    personal_solicita_id: Optional[int] = None
    usuario_solicita_id: Optional[int] = None
    estado: str
    observaciones: str
    usuario_aprueba_id: Optional[int] = None
    fecha_aprobacion: Optional[datetime] = None
    activo: bool
    created_at: datetime
    updated_at: datetime
    detalles: List[RequisicionDetalle] = []

    model_config = ConfigDict(from_attributes=True)


class RequisicionListResponse(BaseModel):
    total: int
    items: List[RequisicionOut]

    model_config = ConfigDict(from_attributes=True)


class EstadoAccion(BaseModel):
    """Cuerpo opcional para aprobar/rechazar (observaciones que se anexan)."""

    observaciones: Optional[str] = ""


# ---------------------------------------------------------------------------
# Despachos
# ---------------------------------------------------------------------------

class DespachoDetalleBase(BaseModel):
    lote_id: int
    cantidad: Decimal = Field(gt=0)
    costo_unitario: Decimal = Field(default=Decimal("0"), ge=0)


class DespachoDetalleCreate(DespachoDetalleBase):
    pass


class DespachoDetalle(DespachoDetalleBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DespachoCreate(BaseModel):
    tipo: str = Field(default="servicio", pattern="^(servicio|paciente|traslado)$")
    almacen_origen_id: int
    almacen_destino_id: Optional[int] = None
    requisicion_id: Optional[int] = None
    servicio_destino_id: Optional[int] = None
    paciente_id: Optional[int] = None
    personal_receptor_id: Optional[int] = None
    numero: Optional[str] = Field(default=None, max_length=20)
    observaciones: Optional[str] = ""
    detalles: List[DespachoDetalleCreate] = Field(min_length=1)


class DespachoOut(BaseModel):
    id: int
    numero: str
    tipo: str
    almacen_origen_id: int
    almacen_destino_id: Optional[int] = None
    requisicion_id: Optional[int] = None
    servicio_destino_id: Optional[int] = None
    paciente_id: Optional[int] = None
    personal_receptor_id: Optional[int] = None
    usuario_despacha_id: Optional[int] = None
    estado: str
    fecha: datetime
    observaciones: str
    activo: bool
    created_at: datetime
    updated_at: datetime
    detalles: List[DespachoDetalle] = []

    model_config = ConfigDict(from_attributes=True)


class DespachoListResponse(BaseModel):
    total: int
    items: List[DespachoOut]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Atenciones y consumo de insumos
# ---------------------------------------------------------------------------

class AtencionCreate(BaseModel):
    paciente_id: int
    personal_atencion_id: Optional[int] = None
    servicio_id: Optional[int] = None
    consulta_id: Optional[int] = None
    observaciones: Optional[str] = ""


class AtencionInsumoCreate(BaseModel):
    lote_id: int
    cantidad: Decimal = Field(gt=0)
    origen: str = Field(default="directo", pattern="^(despacho|directo)$")
    despacho_id: Optional[int] = None


class AtencionInsumo(AtencionInsumoCreate):
    id: int
    usuario_id: Optional[int] = None
    fecha: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AtencionOut(BaseModel):
    id: int
    paciente_id: int
    personal_atencion_id: Optional[int] = None
    servicio_id: Optional[int] = None
    consulta_id: Optional[int] = None
    estado: str
    fecha: datetime
    observaciones: str
    activo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AtencionDetalle(AtencionOut):
    insumos_consumidos: List[AtencionInsumo] = []


class AtencionListResponse(BaseModel):
    total: int
    items: List[AtencionOut]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Unidosis
# ---------------------------------------------------------------------------

class UnidosisDetalleBase(BaseModel):
    lote_id: int
    cantidad: Decimal = Field(gt=0)
    dosis: str = Field(default="", max_length=100)


class UnidosisDetalleCreate(UnidosisDetalleBase):
    pass


class UnidosisDetalle(UnidosisDetalleBase):
    id: int
    fecha_administracion: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UnidosisCreate(BaseModel):
    paciente_id: int
    almacen_origen_id: int
    numero: Optional[str] = Field(default=None, max_length=20)
    atencion_id: Optional[int] = None
    personal_prepara_id: Optional[int] = None
    observaciones: Optional[str] = ""
    detalles: List[UnidosisDetalleCreate] = Field(min_length=1)


class UnidosisOut(BaseModel):
    id: int
    numero: Optional[str] = None
    paciente_id: int
    atencion_id: Optional[int] = None
    almacen_origen_id: int
    personal_prepara_id: Optional[int] = None
    usuario_prepara_id: Optional[int] = None
    estado: str
    fecha: datetime
    observaciones: str
    activo: bool
    created_at: datetime
    updated_at: datetime
    detalles: List[UnidosisDetalle] = []

    model_config = ConfigDict(from_attributes=True)


class UnidosisListResponse(BaseModel):
    total: int
    items: List[UnidosisOut]

    model_config = ConfigDict(from_attributes=True)
