from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base


class RayosX(Base):
    __tablename__ = "rayos_x"

    id = Column(Integer, primary_key=True, index=True)

    cod_rx = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    registro = Column(TIMESTAMP)

    usuario = Column(Text)
    activo = Column(Boolean, nullable=False, default=True)

    consulta_id = Column(
        Integer,
        ForeignKey("consultas.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False
    )

    ciclo_consulta_id = Column(
        Integer,
        ForeignKey("ciclos_consulta.id", ondelete="SET NULL", onupdate="CASCADE")
    )

    resultados = Column(JSONB)
    metadatos = Column(JSONB)

    consulta = relationship("ConsultaModel", back_populates="rayos_x")
    ciclo = relationship("CiclosConsulta", lazy="joined")

    __table_args__ = (
        Index("idx_rx_consulta", "consulta_id"),
        Index("idx_rx_ciclo", "ciclo_consulta_id"),
        Index("idx_rx_registro", "registro"),
        Index("idx_rx_activo", "activo"),
    )