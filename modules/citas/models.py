# modules/citas/models.py

from sqlalchemy import Column, Integer, Date, String, ForeignKey, Text, text, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy.orm import relationship, validates
from datetime import date
from core.database import Base


class CitaModel(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)

    fecha_registro = Column(Date, default=date.today)
    
    expediente = Column(String(20), nullable=True)

    paciente_id = Column(
        Integer,
        ForeignKey("pacientes.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=True
    )

    especialidad = Column(String(6), nullable=True)
    especialidad_id = Column(Integer, ForeignKey("especialidades.id", ondelete="SET NULL"), nullable=True)

    fecha_cita = Column(Date, nullable=True)

    razon_consulta = Column(String(50), nullable=True)
    notas = Column(Text, nullable=True)

    datos_extra = Column(JSONB, nullable=True)

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

    @validates("datos_extra")
    def sync_from_jsonb(self, key, value):
        if value and isinstance(value, dict):
            razon = value.get("razon_consulta")
            if razon and isinstance(razon, str) and razon.strip():
                self.razon_consulta = razon.strip()
            nota = value.get("notas") or value.get("nota")
            if nota and isinstance(nota, str) and nota.strip():
                self.notas = nota.strip()
        return value

    # Relaciones
    paciente = relationship("PacienteModel", back_populates="citas")
    especialidad_ref = relationship("EspecialidadModel", lazy="joined")
