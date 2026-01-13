# app/models/pacientes.py
from sqlalchemy import Column, Integer, String, Date, Text, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates
from app.database.db import Base


class PacienteModel(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # unidad = Column(Integer, nullable=True)
    cui = Column(Integer, unique=True, nullable=True, index=True)
    expediente = Column(String(20), unique=True, nullable=True, index=True)
    pasaporte = Column(String(20), unique=True, nullable=True)
    # otro_id = Column(String(50), unique=True, nullable=True)
    nombre = Column(JSONB, nullable=False)
    sexo = Column(String(1), nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    contacto = Column(JSONB, nullable=True)
    referencias = Column(JSONB, nullable=True)
    datos_extra = Column(JSONB, nullable=True)
    estado = Column(String(2), server_default="A", nullable=False)
    metadatos = Column(JSONB, nullable=True)
    nombre_completo = Column(Text, nullable=True)

    # Índices condicionales (solo únicos si no son nulos)
    __table_args__ = (
        Index("uq_cui_not_null", "cui", unique=True,
              postgresql_where=text("cui IS NOT NULL")),
        Index("uq_expediente_not_null", "expediente", unique=True,
              postgresql_where=text("expediente IS NOT NULL AND expediente <> ''")),
        Index("idx_paciente_estado", "estado"),
    )

    consultas = relationship("ConsultaModel", back_populates="paciente", cascade="all, delete-orphan")

    @validates("nombre")
    def actualizar_nombre_completo(self, key: str, nombre_dict: dict) -> dict:
        partes = [
            nombre_dict.get("primer_nombre"),
            nombre_dict.get("segundo_nombre"),
            nombre_dict.get("otro_nombre"),
            nombre_dict.get("primer_apellido"),
            nombre_dict.get("segundo_apellido"),
            nombre_dict.get("apellido_casada")
        ]
        nombre_limpio = " ".join(p.strip() for p in partes if p and p.strip())
        self.nombre_completo = nombre_limpio.upper() if nombre_limpio else None
        return nombre_dict