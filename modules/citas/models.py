# modules/citas/models.py

from sqlalchemy import Column, Integer, Date, String, ForeignKey, Text, Boolean, text, func
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

    # Quién atiende la cita (médico u otro personal de atención)
    personal_atencion_id = Column(
        Integer,
        ForeignKey("personal_atencion.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

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
    personal_atencion = relationship(
        "MedicoModel",
        foreign_keys=[personal_atencion_id],
        lazy="joined",
    )

    @property
    def personal_atencion_nombre(self) -> Optional[str]:
        return self.personal_atencion.nombre if self.personal_atencion else None


class CitaDiaInhabilModel(Base):
    """Fechas en las que no se pueden agendar citas (feriados / asuetos
    oficiales). Las activa/desactiva el administrador desde adminsys."""
    __tablename__ = "citas_dias_inhabiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date, nullable=False, unique=True, index=True)
    motivo = Column(String(200), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_by = Column(String(20), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=False),
        server_default=text("CURRENT_TIMESTAMP")
    )
