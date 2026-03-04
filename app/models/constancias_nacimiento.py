from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Text,
    ForeignKey,
    UniqueConstraint,
    text
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database.db import Base


class ConstanciaNacimientoModel(Base):
    __tablename__ = "constancia_nacimiento"

    __table_args__ = (
        UniqueConstraint("documento", name="constancia_nacimiento_documento_key"),
    )

    id = Column(Integer, primary_key=True, index=True)

    documento = Column(String(20), nullable=False)

    paciente_id = Column(
        Integer,
        ForeignKey("pacientes.id", name="fk_constancia_paciente", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )

    medico_id = Column(
        Integer,
        ForeignKey("medicos.id", name="fk_constancia_medico", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )

    registrador_id = Column(
        Integer,
        ForeignKey("users.id", name="fk_constancia_registrador", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )

    nombre_madre = Column(String(200), nullable=False)
    vecindad_madre = Column(String(200))

    fecha_registro = Column(Date, nullable=False, server_default=text("CURRENT_DATE"))

    menor_edad = Column(JSONB)
    hijos = Column(Integer)
    vivos = Column(Integer)
    muertos = Column(Integer)

    observaciones = Column(Text)
    metadatos = Column(JSONB)

    created_at = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP"))

    # Relaciones
    paciente = relationship("PacienteModel", back_populates="constancias_nacimiento")
    medico = relationship("MedicoModel", back_populates="constancias")
    registrador = relationship("UserModel")
    historial = relationship("ConstanciaNacimientoHistorialModel", back_populates="constancia")