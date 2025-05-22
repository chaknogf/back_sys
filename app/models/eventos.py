from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base

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

    consulta = relationship("ConsultaModel", back_populates="eventos")