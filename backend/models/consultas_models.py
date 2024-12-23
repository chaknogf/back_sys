# coding: utf-8
from sqlalchemy import BigInteger, CHAR, Column, Date, DateTime, Enum, ForeignKey, Integer, String, TIMESTAMP, Text, Time, text
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


class Especialidad(Base):
    __tablename__ = 'especialidad'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    especialista = Column(String(100))


class EstadosCivile(Base):
    __tablename__ = 'estados_civiles'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)


class Estatu(Base):
    __tablename__ = 'estatus'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(50), nullable=False)


class GrupoEdad(Base):
    __tablename__ = 'grupo_edad'

    id = Column(Integer, primary_key=True)
    grupo = Column(String(50), nullable=False)
    edad_inicio = Column(Integer, nullable=False)
    edad_fin = Column(Integer)
    caracteristicas = Column(Text)


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


class Servicio(Base):
    __tablename__ = 'servicios'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)


class TipoConsulta(Base):
    __tablename__ = 'tipo_consulta'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)


class TipoLesion(Base):
    __tablename__ = 'tipo_lesion'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)


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
    direccion = Column(String(4))
    municipio = Column(String(100))
    telefono1 = Column(String(10))
    telefono2 = Column(String(10))
    telefono3 = Column(String(15))
    email = Column(String(150))
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
    


class Expediente(Base):
    __tablename__ = 'expedientes'

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(ForeignKey('pacientes.id'), index=True)
    expediente = Column(String(15), unique=True)
    hoja_emergencia = Column(String(15), unique=True)
    referencia_anterior = Column(String(11))
    expediente_madre = Column(String(11))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    paciente = relationship('Paciente')


class Consulta(Base):
    __tablename__ = 'consultas'

    id = Column(Integer, primary_key=True)
    exp_id = Column(ForeignKey('expedientes.id'), index=True)
    paciente_id = Column(ForeignKey('pacientes.id'), index=True)
    historia_clinica = Column(String(15))
    fecha_consulta = Column(Date, index=True)
    hora = Column(Time)
    fecha_recepcion = Column(DateTime)
    fecha_egreso = Column(DateTime)
    tipo_consulta = Column(ForeignKey('tipo_consulta.id'), index=True)
    tipo_lesion = Column(ForeignKey('tipo_lesion.id'), index=True)
    estancia = Column(Integer)
    especialidad = Column(ForeignKey('especialidad.id'), index=True)
    servicio = Column(ForeignKey('servicios.id'), index=True)
    fallecido = Column(String(1))
    referido = Column(String(1))
    contraindicado = Column(String(1))
    diagnostico = Column(String(100))
    folios = Column(Integer)
    medico = Column(ForeignKey('medicos.colegiado'), index=True)
    nota = Column(Text)
    estatus = Column(ForeignKey('estatus.id'), index=True)
    lactancia = Column(String(1))
    prenatal = Column(Integer)
    create_user = Column(String(50))
    update_user = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    grupo_edad = Column(ForeignKey('grupo_edad.id'), index=True)

    especialidad1 = relationship('Especialidad')
    estatu = relationship('Estatu')
    exp = relationship('Expediente')
    grupo_edad1 = relationship('GrupoEdad')
    medico1 = relationship('Medico')
    servicio1 = relationship('Servicio')
    tipo_consulta1 = relationship('TipoConsulta')
    tipo_lesion1 = relationship('TipoLesion')


class VistaConsultas(Base):
    __tablename__ = 'vr_consultas'

    id = Column(Integer, primary_key=True)
    exp_id = Column(Integer)
    paciente_id = Column(Integer)
    historia_clinica = Column(String(15))
    fecha_consulta = Column(Date)
    hora = Column(Time)
    fecha_recepcion = Column(DateTime)
    fecha_egreso = Column(DateTime)
    tipo_consulta = Column(Integer)
    estatus = Column(Integer)


