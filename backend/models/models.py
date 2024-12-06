# coding: utf-8
from sqlalchemy import BigInteger, CHAR, Column, Date, DateTime, Enum, ForeignKey, Integer, SmallInteger, String, TIMESTAMP, Text, Time, text
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
import re

Base = declarative_base()
metadata = Base.metadata


class ClasesParto(Base):
    __tablename__ = 'clases_parto'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(50))


class CodigoProcedimiento(Base):
    __tablename__ = 'codigo_procedimientos'

    id = Column(Integer, primary_key=True)
    abreviatura = Column(String(10), nullable=False)
    procedimiento = Column(String(200), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


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


class EstadiaE(Base):
    __tablename__ = 'estadia_es'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(50), nullable=False)


class EstadosCivile(Base):
    __tablename__ = 'estados_civiles'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)


class EstadosSalud(Base):
    __tablename__ = 'estados_salud'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)


class Estatu(Base):
    __tablename__ = 'estatus'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(50), nullable=False)


class Estudio(Base):
    __tablename__ = 'estudios'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)


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


class LugaresReferencia(Base):
    __tablename__ = 'lugares_referencia'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)


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


class Permiso(Base):
    __tablename__ = 'permisos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)


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


class Servicio(Base):
    __tablename__ = 'servicios'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)


class Servio(Base):
    __tablename__ = 'servio_es'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)


class SituacionesSalud(Base):
    __tablename__ = 'situaciones_salud'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)


class TipoCita(Base):
    __tablename__ = 'tipo_citas'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)


class TipoConsulta(Base):
    __tablename__ = 'tipo_consulta'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)


class TipoLesion(Base):
    __tablename__ = 'tipo_lesion'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)


class TiposParto(Base):
    __tablename__ = 'tipos_parto'

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(50))


class Cie10(Base):
    __tablename__ = 'cie10'

    cod = Column(String(7), primary_key=True)
    grupo = Column(CHAR(1), index=True)
    dx = Column(String(250), nullable=False)
    abreviatura = Column(String(10))
    especialidad_id = Column(ForeignKey('especialidad.id'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    especialidad = relationship('Especialidad')


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

  # Validaciones de nombre y apellido
    @validates('nombre')
    def validate_nombre(self, key, value):
        if value:
            # Convertir a mayúsculas y corregir espacios adicionales
            value = re.sub(r'\s+', ' ', value.strip())  # Elimina espacios extra
            return value.upper()  # Convertir a mayúsculas
        return value

    @validates('apellido')
    def validate_apellido(self, key, value):
        if value:
            # Convertir a mayúsculas y corregir espacios adicionales
            value = re.sub(r'\s+', ' ', value.strip())  # Elimina espacios extra
            return value.upper()  # Convertir a mayúsculas
        return value

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


class Cita(Base):
    __tablename__ = 'citas'

    id = Column(Integer, primary_key=True)
    paciente_id = Column(ForeignKey('pacientes.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    especialidad = Column(ForeignKey('especialidad.id'), index=True)
    fecha_cita = Column(Date)
    tipo_cita = Column(ForeignKey('tipo_citas.id'), index=True)
    doble_fecha = Column(Enum('S', 'N'), server_default=text("'N'"))
    laboratorio = Column(String(50))
    fecha_laboratorio = Column(Date)
    nota = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    created_by = Column(String(8))

    especialidad1 = relationship('Especialidad')
    paciente = relationship('Paciente')
    tipo_cita1 = relationship('TipoCita')


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


class ProceMedico(Base):
    __tablename__ = 'proce_medicos'

    id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    servicio_id = Column(ForeignKey('servicios.id'), index=True)
    sexo = Column(Enum('M', 'F'))
    codigo_procedimiento_id = Column(ForeignKey('codigo_procedimientos.id'), nullable=False, index=True)
    especialidad_id = Column(ForeignKey('especialidad.id'), index=True)
    cantidad = Column(Integer)
    medico_id = Column(ForeignKey('medicos.colegiado'), index=True)
    grupo_edad = Column(Enum('N', 'A'))
    created_by = Column(String(10))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    codigo_procedimiento = relationship('CodigoProcedimiento')
    especialidad = relationship('Especialidad')
    medico = relationship('Medico')
    servicio = relationship('Servicio')


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


class Consulta(Base):
    __tablename__ = 'consultas'

    id = Column(Integer, primary_key=True)
    exp_id = Column(ForeignKey('expedientes.id'), index=True)
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


class Uisau(Base):
    __tablename__ = 'uisau'

    id = Column(Integer, primary_key=True)
    consulta_id = Column(ForeignKey('consultas.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    estado_salud_id = Column(ForeignKey('estados_salud.id'), nullable=False, index=True)
    situacion_salud_id = Column(ForeignKey('situaciones_salud.id'), nullable=False, index=True)
    lugar_referencia_id = Column(ForeignKey('lugares_referencia.id'), nullable=False, index=True)
    fecha_referencia = Column(Date)
    fecha_contacto = Column(Date)
    hora_contacto = Column(Time)
    estadia = Column(SmallInteger)
    cama_numero = Column(SmallInteger)
    informacion = Column(Enum('S', 'N'))
    nombre_contacto = Column(String(150))
    parentesco_id = Column(ForeignKey('parentescos.id'), index=True)
    telefono = Column(String(15))
    nota = Column(Text)
    estudios = Column(String(230))
    evolucion = Column(Text)
    recetado_por = Column(Enum('S', 'N'))
    shampoo = Column(TINYINT(1), server_default=text("'0'"))
    toalla = Column(TINYINT(1), server_default=text("'0'"))
    peine = Column(TINYINT(1), server_default=text("'0'"))
    jabon = Column(TINYINT(1), server_default=text("'0'"))
    cepillo_dientes = Column(TINYINT(1), server_default=text("'0'"))
    pasta_dental = Column(TINYINT(1), server_default=text("'0'"))
    sandalias = Column(TINYINT(1), server_default=text("'0'"))
    agua = Column(TINYINT(1), server_default=text("'0'"))
    papel = Column(TINYINT(1), server_default=text("'0'"))
    panales = Column(TINYINT(1), server_default=text("'0'"))
    created_by = Column(String(50))
    update_by = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    consulta = relationship('Consulta')
    estado_salud = relationship('EstadosSalud')
    lugar_referencia = relationship('LugaresReferencia')
    parentesco = relationship('Parentesco')
    situacion_salud = relationship('SituacionesSalud')
