from sqlalchemy import Column, BigInteger, Integer, String, Text, Date
from core.database import Base


class Sigsa3Model(Base):
    __tablename__ = "sigsa3"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    personal_salud = Column(String(100), nullable=True)
    fecha_consulta = Column(Date, nullable=True)
    no_historia_clinica = Column(String(30), nullable=True)
    nombre_paciente = Column(String(150), nullable=True)
    sexo = Column(String(1), nullable=True)
    pueblo = Column(String(80), nullable=True)
    comunidad_linguistica = Column(String(80), nullable=True)
    edad_dias = Column(Integer, nullable=True)
    edad_meses = Column(Integer, nullable=True)
    edad_anios = Column(Integer, nullable=True)
    departamento_residencia = Column(String(100), nullable=True)
    municipio_residencia = Column(String(100), nullable=True)
    comunidad = Column(String(150), nullable=True)
    direccion = Column(Text, nullable=True)
    tipo_consulta = Column(String(80), nullable=True)
    control = Column(String(80), nullable=True)
    semana_gestacional = Column(Integer, nullable=True)
    descripcion_diagnostico_control = Column(Text, nullable=True)
    codigo_cie_10 = Column(String(30), nullable=True)
    dx = Column(Text, nullable=True)
    tipologia = Column(String(100), nullable=True)
    especialidad = Column(String(100), nullable=True)
