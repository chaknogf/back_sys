# app/models/citas.py

from sqlalchemy import Column, Integer, Date, String, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from app.database.db import Base


class CitaModel(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=True)
    paciente_id = Column(
        Integer,
        ForeignKey("pacientes.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=True
    )
    especialidad = Column(Integer, nullable=True)
    fecha_cita = Column(Date, nullable=True)
    nota = Column(String(255), nullable=True)
    tipo = Column(Integer, nullable=True)
    lab = Column(Integer, nullable=True)
    fecha_lab = Column(Date, nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=False),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_at = Column(
        TIMESTAMP(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    created_by = Column(String(8), nullable=True)

    # Relación
    paciente = relationship("PacienteModel", back_populates="citas")