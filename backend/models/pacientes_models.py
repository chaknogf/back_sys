# coding: utf-8
from sqlalchemy import BigInteger, CHAR, Column, Date, Enum, ForeignKey, Integer, String, TIMESTAMP, Time, text, Table, MetaData
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base
from tools.validador import trim_str 

Base = declarative_base()
metadata = Base.metadata


class DeptoMuni(Base):
    __tablename__ = 'depto_muni'

    codigo = Column(CHAR(4), primary_key=True)
    departamento = Column(String(100), nullable=False)
    municipio = Column(String(100), nullable=False)
    lugar = Column(String(255), nullable=False)


class Educacion(Base):
    __tablename__ = 'educacion'

    id = Column(Integer, primary_key=True)
    nivel = Column(String(50), nullable=False, unique=True)


class EstadosCivile(Base):
    __tablename__ = 'estados_civiles'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)


class Idioma(Base):
    __tablename__ = 'idiomas'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)


class Nacionalidade(Base):
    __tablename__ = 'nacionalidades'

    iso = Column(String(3), primary_key=True)
    nacionalidad = Column(String(50))
    pais = Column(String(50))
    cti = Column(Integer)
    idioma = Column(String(30))


class Parentesco(Base):
    __tablename__ = 'parentescos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)


class Pueblo(Base):
    __tablename__ = 'pueblos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)


class Paciente(Base):
    __tablename__ = 'pacientes'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    apellido = Column(String(100))
    dpi = Column(BigInteger)
    pasaporte = Column(String(50))
    sexo = Column(Enum('M', 'F'), server_default=text("'M'"))
    nacimiento = Column(Date)
    defuncion = Column(Date)
    tiempo_defuncion = Column(Time)
    nacionalidad_iso = Column(ForeignKey('nacionalidades.iso'), index=True)
    lugar_nacimiento = Column(ForeignKey('depto_muni.codigo'), index=True)
    estado_civil = Column(ForeignKey('estados_civiles.id'), index=True)
    educacion = Column(ForeignKey('educacion.id'), index=True)
    pueblo = Column(ForeignKey('pueblos.id'), index=True)
    idioma = Column(ForeignKey('idiomas.id'), index=True)
    ocupacion = Column(String(50))
    estado = Column(Enum('V', 'M'), server_default=text("'V'"))
    padre = Column(String(100))
    madre = Column(String(100))
    conyugue = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    educacion1 = relationship('Educacion')
    estados_civile = relationship('EstadosCivile')
    idioma1 = relationship('Idioma')
    depto_muni = relationship('DeptoMuni')
    nacionalidade = relationship('Nacionalidade')
    pueblo1 = relationship('Pueblo')
    
    # Validaciones de nombre y apellido
    @validates('nombre', 'apellido')
    def validar_nombres(self, key, value):
        return trim_str(value)
    


class ContactoPaciente(Base):
    __tablename__ = 'contacto_paciente'

    id = Column(Integer, primary_key=True)
    paciente_id = Column(ForeignKey('pacientes.id'), nullable=False, index=True)
    direccion = Column(String(150))
    telefono1 = Column(String(10))
    telefono2 = Column(String(10))
    telefono3 = Column(String(15))
    email = Column(String(150))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    paciente = relationship('Paciente')


class ReferenciaContacto(Base):
    __tablename__ = 'referencia_contacto'

    id = Column(Integer, primary_key=True)
    paciente_id = Column(ForeignKey('pacientes.id'), index=True)
    nombre_contacto = Column(String(100), nullable=False)
    telefono_contacto = Column(String(10))
    parentesco_id = Column(ForeignKey('parentescos.id'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    paciente = relationship('Paciente')
    parentesco = relationship('Parentesco')

    @validates('nombre_contacto')
    def validar_contacto(self, key, value):
        return trim_str(value)
    
class VistaPaciente(Base):
    __tablename__ = 'vi_paciente'  # Nombre de la vista

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    apellido = Column(String(100))
    dpi = Column(BigInteger)
    pasaporte = Column(String(50))
    sexo = Column(String(1))
    nacimiento = Column(Date)
    defuncion = Column(Date)
    tiempo_defuncion = Column(Time)
    nacionalidad_iso = Column(String(3))
    nacionalidad = Column(String(50))
    lugar_nacimiento = Column(CHAR(4))
    lugar = Column(String(255))
    estado_civil = Column(Integer)
    e_civil = Column(String(50))
    educacion = Column(Integer)
    nivel_educacion = Column(String(50))
    pueblo = Column(Integer)
    pueblo_ = Column(String(50))
    idioma = Column(Integer)
    idioma_ = Column(String(50))
    ocupacion = Column(String(50))
    estado = Column(Enum('V', 'M'), server_default=text("'V'"))
    padre = Column(String(100))
    madre = Column(String(100))
    conyugue = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    direccion = Column(String(150))
    telefono1 = Column(String(10))
    telefono2 = Column(String(10))
    telefono3 = Column(String(15))
    email = Column(String(150))
    nombre_contacto = Column(String(100))
    telefono_contacto = Column(String(10))
    parentesco_id = Column(Integer)
    parentesco_nombre = Column(String(50))
    
class CardPaciente(Base):
    __tablename__ = 'card_paciente'

    paciente_id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    apellido = Column(String(100))
    dpi = Column(BigInteger)
    sexo = Column(Enum('M', 'F'), server_default=text("'M'"))
    nacimiento = Column(Date)
    defuncion = Column(Date, nullable=True)
    estado = Column(Enum('V', 'M'), server_default=text("'V'"))
    direccion = Column(String(150), nullable=True)
    telefono1 = Column(String(10), nullable=True)
    telefono2 = Column(String(10), nullable=True)
    telefono3 = Column(String(15), nullable=True)
    email = Column(String(150), nullable=True)
    expediente_id = Column(Integer, nullable=True)
    expediente = Column(String(15), nullable=True)
    hoja_emergencia = Column(String(15), nullable=True)
    referencia_anterior = Column(String(11), nullable=True)
    expediente_madre = Column(String(11), nullable=True)
    paciente_created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    paciente_updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    contacto_created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    contacto_updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    expediente_created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    expediente_updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
