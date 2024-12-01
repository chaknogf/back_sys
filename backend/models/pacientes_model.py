from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  Column, Integer, String, BigInteger, Enum, Date, Time, ForeignKey, TIMESTAMP, text


class PacienteModel(Base):
    __tablename__ = "pacientes"

    id = Column("id_paciente", Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    dpi = Column(BigInteger, unique=True)
    pasaporte = Column(String(50))
    sexo = Column(Enum("M", "F"))
    nacimiento = Column(Date)
    defuncion = Column(Date, nullable=True)
    tiempo_defuncion = Column(Time, nullable=True)
    nacionalidad_iso = Column(String(3), ForeignKey("nacionalidades.iso"), default="GTM")
    lugar_nacimiento_id = Column(String(4), ForeignKey("depto_muni.codigo"))
    estado_civil_id = Column(Integer, ForeignKey("estados_civiles.id"))
    educacion_id = Column(Integer, ForeignKey("educacion.id"))
    pueblo_id = Column(Integer, ForeignKey("pueblos.id"))
    idioma_id = Column(Integer, ForeignKey("idiomas.id"))
    ocupacion = Column(String(50))
    estado = Column(Enum("V", "M"), default="V")
    padre = Column(String(100))
    madre = Column(String(100))
    conyugue = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    # Relationships (if needed)
    nacionalidad = relationship("NacionalidadModel", back_populates="pacientes", lazy="select")
    lugar_nacimiento = relationship("DeptoMuniModel", back_populates="pacientes", lazy="select")
    estado_civil = relationship("EstadoCivilModel", back_populates="pacientes", lazy="select")
    educacion = relationship("EducacionModel", back_populates="pacientes", lazy="select")
    pueblo = relationship("PuebloModel", back_populates="pacientes", lazy="select")
    idioma = relationship("IdiomaModel", back_populates="pacientes", lazy="select")

# Relaciones inversas en modelos relacionados serían necesarias, por ejemplo:
# class NacionalidadModel(Base):
#     __tablename__ = "nacionalidades"
#     iso = Column(String(3), primary_key=True)
#     pacientes = relationship("PacienteModel", back_populates="nacionalidad")

class ReferenciaContactoModel(Base):
    __tablename__ = "referencia_contacto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"))
    nombre_contacto = Column(String(100), nullable=False)
    telefono_contacto = Column(String(10))
    parentesco_id = Column(Integer, ForeignKey("parentescos.id"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    # Relación con Paciente
    paciente = relationship("PacienteModel", back_populates="referencias_contacto", lazy="select")
    # Relación con Parentesco (opcional)
    parentesco = relationship("ParentescoModel", back_populates="referencias_contacto", lazy="select")


class ContactoPacienteModel(Base):
    __tablename__ = "contacto_paciente"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id_paciente"), nullable=False)
    direccion = Column(String(150), nullable=True, default=None)
    telefono1 = Column(String(10), nullable=True, default=None)
    telefono2 = Column(String(10), nullable=True, default=None)
    telefono3 = Column(String(15), nullable=True, default=None)
    email = Column(String(150), nullable=True, default=None)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    # Relación con Paciente
    paciente = relationship("PacienteModel", back_populates="contactos_paciente", lazy="select")