# app/models/consultas.py → solo cambia __table_args__
from sqlalchemy import BigInteger, Boolean, Column, Integer, String, Date, Text, Time, ForeignKey, Index, text, desc
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database.db import Base


class ConsultaModel(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    expediente = Column(String(20), nullable=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_consulta = Column(Integer, nullable=False, index=True)
    especialidad = Column(String(50), nullable=False)
    servicio = Column(String(50), nullable=False)
    documento = Column(String(20), nullable=False)
    fecha_consulta = Column(Date, nullable=False, index=True)
    hora_consulta = Column(Time, nullable=False)
    indicadores = Column(JSONB, nullable=True)
    ciclo = Column(JSONB, nullable=True)
    orden = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True)
    
    paciente = relationship("PacienteModel", back_populates="consultas")
    # eventos = relationship("EventoConsultaModel", back_populates="consulta", cascade="all, delete-orphan", passive_deletes=True)

    __table_args__ = (
        # Índice compuesto para filtros frecuentes y ordenamiento
        Index("idx_consulta_paciente_tipo_fecha", "paciente_id", "tipo_consulta", "fecha_consulta"),
        Index("idx_consulta_fecha_desc", text("fecha_consulta DESC")),  # Para orden descendente
        Index("idx_consulta_tipo_especialidad", "tipo_consulta", "especialidad"),
        Index("idx_consulta_servicio_documento", "servicio", "documento"),
    )


