# app/models/medicos.py

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, TIMESTAMP, text, Index
from app.database.db import Base

class MedicoModel(Base):
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    colegiado = Column(String(20), index=True)
    dpi = Column(BigInteger, index=True)
    sexo = Column(String(1))
    especialidad = Column(String(100), index=True)
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(
        TIMESTAMP(timezone=False),
        server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        Index("idx_medicos_activo", "activo"),
        Index("idx_medicos_colegiado", "colegiado"),
        Index("idx_medicos_dpi", "dpi"),
        Index("idx_medicos_especialidad", "especialidad"),
        Index("idx_medicos_nombre", "nombre"),
    )