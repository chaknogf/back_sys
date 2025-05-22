
from sqlalchemy import Column, Integer, String, Date, Time, TIMESTAMP, ForeignKey, JSON, text
from sqlalchemy import Column, Integer, String, Text, JSON, CHAR
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base


# 🧾 Modelo: EventoConsulta
class EventoConsultaModel(Base):
    __tablename__ = 'eventos_consulta'

    id = Column(Integer, primary_key=True)
    consulta_id = Column(Integer, ForeignKey('consultas.id', ondelete="CASCADE"), nullable=False)
    tipo_evento = Column(Integer, nullable=False)
    datos = Column(JSONB)
    responsable = Column(JSONB)
    creado_en = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    actualizado_en = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    estado = Column(String(2), default='A')

    consulta = relationship("Consulta", back_populates="eventos")