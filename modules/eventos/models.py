# modules/eventos/models.py
from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime


class EventoConsultaModel(Base):
    __tablename__ = "eventos_consulta"

    id = Column(Integer, primary_key=True, autoincrement=True)
    consulta_id = Column(Integer, ForeignKey("consultas.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_evento = Column(Integer, nullable=False)
    datos = Column(JSONB, nullable=True)
    responsable = Column(JSONB, nullable=True)
    estado = Column(String(2), server_default="A", nullable=False)
    creado_en = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP"))
    actualizado_en = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    consulta = relationship("ConsultaModel", back_populates="eventos")
