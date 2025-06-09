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
    # identificadores = Column(JSONB, nullable=True)
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
            nombre.get("primer"),
            nombre.get("segundo"),
            nombre.get("otro"),
            nombre.get("apellido_primero"),
            nombre.get("apellido_segundo"),
            nombre.get("casada")
        ]
        # Elimina elementos vacíos o nulos y une con un solo espacio
        return ' '.join(p for p in partes if p and p.strip())

@validates("nombre")
def actualizar_nombre_completo(self, key, value):
    self.nombre_completo = " ".join(
        [str(p).strip() for p in [
            value.get("primer"),
            value.get("segundo"),
            value.get("otro"),
            value.get("apellido_primero"),
            value.get("apellido_segundo"),
            value.get("casada")
        ] if p and str(p).strip()]
    )
    return value