"""Almacenamiento de aprendizaje del agente: sinónimos y feedback."""

from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    func,
)
from core.database import Base


class ReglaAgente(Base):
    """Sinónimo/regla aprendido por el usuario o por feedback."""

    __tablename__ = "agente_reglas"
    id = Column(BigInteger, primary_key=True, index=True)
    # tipo: sinonimo_entidad | sinonimo_agrupacion | sinonimo_medida | plantilla
    tipo = Column(String(40), nullable=False, index=True)
    clave = Column(String(200), nullable=False)      # texto que dispara la regla
    valor = Column(String(200), nullable=False)      # entidad/dimensión destino
    veces_usado = Column(BigInteger, nullable=False, default=0)
    veces_exito = Column(BigInteger, nullable=False, default=0)
    veces_fracaso = Column(BigInteger, nullable=False, default=0)
    origen = Column(String(20), nullable=False, default="manual")  # manual|feedback
    usuario = Column(String(60), nullable=True)
    creado_en = Column(DateTime(timezone=True), nullable=False,
                       server_default=func.now())


class FeedbackAgente(Base):
    """Registro de calificación de una respuesta del agente."""

    __tablename__ = "agente_feedback"
    id = Column(BigInteger, primary_key=True, index=True)
    pregunta = Column(Text, nullable=False)
    respuesta = Column(Text, nullable=False)
    sql_generado = Column(Text, nullable=True)
    correcto = Column(Boolean, nullable=True)          # None = pendiente
    correccion = Column(Text, nullable=True)           # texto de la corrección
    username = Column(String(60), nullable=False)
    creado_en = Column(DateTime(timezone=True), nullable=False,
                       server_default=func.now())