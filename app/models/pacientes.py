from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base
from sqlalchemy.orm import validates

class PacienteModel(Base):
    __tablename__ = 'pacientes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    identificadores = Column(JSONB, nullable=False)
    nombre = Column(JSONB)
    sexo = Column(String(2))
    fecha_nacimiento = Column(Date)
    contacto = Column(JSONB)
    referencias = Column(JSONB)
    datos_extra = Column(JSONB)
    estado = Column(String(2), default='A')
    metadatos = Column(JSONB)
    nombre_completo = Column(Text)
    
    def generar_nombre_completo(self):
        n = self.nombre
        return " ".join(
            filter(None, [
                n.get("primer"),
                n.get("segundo"),
                n.get("otro"),
                n.get("apellido_primero"),
                n.get("apellido_segundo"),
                n.get("casada")
            ])
        )

    # relación con ConsultaModel
    consultas = relationship("ConsultaModel", back_populates="paciente", cascade="all, delete-orphan")
    
    
@validates("nombre")
def actualizar_nombre_completo(self, key, value):
    self.nombre_completo = " ".join(
        filter(None, [
            value.get("primer"),
            value.get("segundo"),
            value.get("otro"),
            value.get("apellido_primero"),
            value.get("apellido_segundo"),
            value.get("casada")
        ])
    )
    return value