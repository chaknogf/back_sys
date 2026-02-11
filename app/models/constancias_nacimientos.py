# app/models/constancias_nacimientos.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Text,
    ForeignKey,
    Index
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from app.database.db import Base


class ConstanciaNacimientoModel(Base):
    __tablename__ = "constancia_nacimiento"

    id = Column(Integer, primary_key=True, autoincrement=True)

    documento = Column(String(20), unique=True, nullable=False)

    paciente_id = Column(
        Integer,
        ForeignKey("pacientes.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )

    medico_id = Column(
        Integer,
        ForeignKey("medicos.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )

    registrador_id = Column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
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
    metadata = Column(JSONB)

    created_at = Column(
        TIMESTAMP(timezone=False),
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_at = Column(
        TIMESTAMP(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    # ========================
    # Relaciones ORM
    # ========================

    paciente = relationship(
        "PacienteModel",
        back_populates="constancias_nacimientos"
    )

    medico = relationship(
        "MedicoModel",
        back_populates="constancias_nacimientos"
    )

    registrador = relationship(
        "UserModel",
        back_populates="constancias_nacimientos"
    )

    __table_args__ = (
        Index(
            "idx_constancia_paciente_fecha",
            "paciente_id",
            "fecha_registro"
        ),
        Index(
            "idx_constancia_fecha_desc",
            text("fecha_registro DESC")
        ),
    )