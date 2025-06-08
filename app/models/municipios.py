from sqlalchemy import CHAR, Column, Integer, String, TIMESTAMP, func
from app.database.db import Base

class MunicipiosModel(Base):
   __tablename__ = "municipios"

   codigo = Column(String(5),primary_key=True, unique=True, nullable=False)
   vecindad = Column(String(150))
   municipio = Column(String(50), nullable=False)
   departamento = Column(String(50), nullable=False)
   

   def __init__(self, codigo, vecindad, municipio, departamento):
      self.codigo = codigo
      self.vecindad = vecindad
      self.municipio = municipio
      self.departamento = departamento