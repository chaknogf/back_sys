# coding: utf-8
from sqlalchemy import BigInteger, CHAR, Column, Date, Enum, ForeignKey, Integer, String, TIMESTAMP, Text, Time, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class ClasesParto(Base):
    __tablename__ = 'clases_parto'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(50))


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


class Especialidad(Base):
    __tablename__ = 'especialidad'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    especialista = Column(String(100))


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


class Pueblo(Base):
    __tablename__ = 'pueblos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)
    permisos = Column(String(250))


class TiposParto(Base):
    __tablename__ = 'tipos_parto'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(50))


class Medico(Base):
    __tablename__ = 'medicos'

    id = Column(Integer, primary_key=True)
    colegiado = Column(Integer, nullable=False, unique=True)
    nombre = Column(String(200))
    dpi = Column(BigInteger)
    especialidad = Column(ForeignKey('especialidad.id'), index=True)
    pasaporte = Column(String(30))
    sexo = Column(Enum('M', 'F'))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    especialidad1 = relationship('Especialidad')


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


class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    username = Column(String(10), nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100))
    dpi = Column(BigInteger, unique=True)
    contraseña = Column(String(255))
    rol = Column(ForeignKey('roles.id'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    role = relationship('Role')


class Madre(Base):
    __tablename__ = 'madres'

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(ForeignKey('pacientes.id'), nullable=False, index=True)
    vecindad = Column(String(4))
    hijos = Column(Integer, server_default=text("'0'"))
    vivos = Column(Integer, server_default=text("'0'"))
    muertos = Column(Integer, server_default=text("'0'"))
    edad = Column(Integer)

    paciente = relationship('Paciente')


class RecienNacido(Base):
    __tablename__ = 'recien_nacidos'

    id = Column(Integer, primary_key=True)
    paciente_id = Column(ForeignKey('pacientes.id'), nullable=False, unique=True)
    hora = Column(Time)
    peso_libras = Column(Integer)
    peso_onzas = Column(Integer)
    tipo_parto = Column(ForeignKey('tipos_parto.id'), index=True)
    clase_parto = Column(ForeignKey('clases_parto.id'), index=True)

    clases_parto = relationship('ClasesParto')
    paciente = relationship('Paciente')
    tipos_parto = relationship('TiposParto')


class ConstanciasNacimiento(Base):
    __tablename__ = 'constancias_nacimiento'

    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    doc = Column(String(15), unique=True)
    madre_id = Column(ForeignKey('madres.id'), nullable=False, index=True)
    recien_nacido_id = Column(ForeignKey('recien_nacidos.id'), nullable=False, index=True)
    usuario_id = Column(ForeignKey('usuarios.id'), nullable=False, index=True)
    medico = Column(ForeignKey('medicos.colegiado'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    madre = relationship('Madre')
    medico1 = relationship('Medico')
    recien_nacido = relationship('RecienNacido')
    usuario = relationship('Usuario')
