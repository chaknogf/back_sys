from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base


class Laboratorios(Base):
    __tablename__ = "laboratorios"

    id = Column(Integer, primary_key=True, index=True)

    cod_lab = Column(Text)
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

    consulta = relationship("ConsultaModel", back_populates="laboratorios")
    ciclo = relationship("CiclosConsulta")

    __table_args__ = (
        Index("idx_lab_consulta", "consulta_id"),
        Index("idx_lab_ciclo", "ciclo_consulta_id"),
        Index("idx_lab_registro", "registro"),
        Index("idx_lab_activo", "activo"),
    )