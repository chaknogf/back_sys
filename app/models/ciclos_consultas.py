from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, ForeignKey, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base


class CiclosConsulta(Base):
    __tablename__ = "ciclos_consulta"

    id = Column(Integer, primary_key=True, index=True)
    consulta_id = Column( Integer, ForeignKey("consultas.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    numero = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    registro = Column(TIMESTAMP, nullable=False, server_default=func.now())
    usuario = Column(Text, nullable=False)
    especialidad = Column(Text)
    servicio = Column(Text)
    contenido = Column(Text)
    datos_medicos = Column(JSONB)

    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("consulta_id", "numero", name="unique_ciclo_por_consulta"),
        CheckConstraint("numero > 0", name="check_numero_positivo"),
        Index("idx_ciclos_consulta_id", "consulta_id"),
        Index("idx_ciclos_registro", "registro"),
        Index("idx_ciclos_activo", "activo"),
    )

    consulta = relationship("ConsultaModel", back_populates="ciclos")