from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates
from app.database.db import Base

class PacienteModel(Base):
    __tablename__ = 'pacientes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    unidad = Column(Integer)
    cui = Column(Integer, unique=True, nullable=True)
    expediente = Column(String, unique=True, nullable=True)
    pasaporte = Column(String, unique=True, nullable=True)
    otro_id = Column(String, unique=True, nullable=True)
    nombre = Column(JSONB, nullable=False)
    sexo = Column(String(2))
    fecha_nacimiento = Column(Date)
    contacto = Column(JSONB)
    referencias = Column(JSONB)
    datos_extra = Column(JSONB)
    estado = Column(String(2), default='A')
    metadatos = Column(JSONB)

    nombre_completo = Column(Text)

    # Relaciones
    consultas = relationship("ConsultaModel", back_populates="paciente", cascade="all, delete-orphan")

    def generar_nombre_completo(nombre: dict) -> str:
        partes = [
            nombre.get("primer_nombre"),
            nombre.get("segundo_nombre"),
            nombre.get("otro_nombre"),
            nombre.get("primer_apellido"),
            nombre.get("segundo_apellido"),
            nombre.get("apellido_casada")
        ]
        # Elimina elementos vacíos o nulos y une con un solo espacio
        return ' '.join(p for p in partes if p and p.strip())

@validates("nombre")
def actualizar_nombre_completo(self, key, value):
    self.nombre_completo = " ".join(
        [str(p).strip() for p in [
            value.get("primer_nombre"),
            value.get("segundo_nombre"),
            value.get("otro_nombre"),
            value.get("primer_apellido"),
            value.get("segundo_apellido"),
            value.get("apellido_casada")
        ] if p and str(p).strip()]
    )
    return value