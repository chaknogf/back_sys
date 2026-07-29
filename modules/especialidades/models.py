from sqlalchemy import Column, Integer, String
from core.database import Base


class EspecialidadModel(Base):
    __tablename__ = "especialidades"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    abreviatura = Column(String(10), unique=True, nullable=True)
    codigo = Column(String(10), unique=True, nullable=True)
