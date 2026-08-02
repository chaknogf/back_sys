from sqlalchemy import Column, SmallInteger, String

from core.database import Base
from modules.sigsa3.models import Sigsa3RegistroModel

__all__ = ["Sigsa3RegistroModel", "TipoConsultaSigsa3Model"]


class TipoConsultaSigsa3Model(Base):
    """Catálogo de tipos de consulta SIGSA-3 (1 Primeras, 2 Reconsultas,
    3 Emergencia, 4 Interconsultas). NO es el catálogo de consultas."""
    __tablename__ = "tipos_consulta_sigsa3"

    id = Column(SmallInteger, primary_key=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(String(200), nullable=True)
