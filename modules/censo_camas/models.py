from sqlalchemy import Column, Integer, SmallInteger, Date, ForeignKey, UniqueConstraint, TIMESTAMP, text
from sqlalchemy.orm import relationship
from core.database import Base


class CensoCamasModel(Base):
    __tablename__ = "censo_camas"
    __table_args__ = (
        UniqueConstraint("fecha", "servicio_id", name="uq_censo_camas_fecha_servicio"),
    )

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, index=True)
    servicio_id = Column(
        Integer, ForeignKey("encamamiento.id", ondelete="CASCADE"), nullable=False, index=True
    )

    ocupados = Column(SmallInteger, nullable=False, default=0)
    camas_ocupadas = Column(SmallInteger, nullable=False, default=0)
    egresos_totales = Column(SmallInteger, nullable=False, default=0)
    egresos = Column(SmallInteger, nullable=False, default=0)
    fallecidos = Column(SmallInteger, nullable=False, default=0)
    referido = Column(SmallInteger, nullable=False, default=0)
    traslado = Column(SmallInteger, nullable=False, default=0)
    contraindicados = Column(SmallInteger, nullable=False, default=0)
    otro_ingresos = Column(SmallInteger, nullable=False, default=0)
    ingresos = Column(SmallInteger, nullable=False, default=0)
    huespedes = Column(SmallInteger, nullable=False, default=0)
    emergencia = Column(SmallInteger, nullable=False, default=0)

    ocupados_masculino = Column(SmallInteger, nullable=False, default=0)
    egresos_masculino = Column(SmallInteger, nullable=False, default=0)
    fallecidos_masculino = Column(SmallInteger, nullable=False, default=0)
    referido_masculino = Column(SmallInteger, nullable=False, default=0)
    traslado_masculino = Column(SmallInteger, nullable=False, default=0)
    contraindicados_masculino = Column(SmallInteger, nullable=False, default=0)
    otro_ingresos_masculino = Column(SmallInteger, nullable=False, default=0)
    ingresos_masculino = Column(SmallInteger, nullable=False, default=0)
    huespedes_masculino = Column(SmallInteger, nullable=False, default=0)
    emergencia_masculino = Column(SmallInteger, nullable=False, default=0)

    ocupados_femenino = Column(SmallInteger, nullable=False, default=0)
    egresos_femenino = Column(SmallInteger, nullable=False, default=0)
    fallecidos_femenino = Column(SmallInteger, nullable=False, default=0)
    referido_femenino = Column(SmallInteger, nullable=False, default=0)
    traslado_femenino = Column(SmallInteger, nullable=False, default=0)
    contraindicados_femenino = Column(SmallInteger, nullable=False, default=0)
    otro_ingresos_femenino = Column(SmallInteger, nullable=False, default=0)
    ingresos_femenino = Column(SmallInteger, nullable=False, default=0)
    huespedes_femenino = Column(SmallInteger, nullable=False, default=0)
    emergencia_femenino = Column(SmallInteger, nullable=False, default=0)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    servicio = relationship("EncamamientoModel")
