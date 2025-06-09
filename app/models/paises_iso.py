from sqlalchemy import Column, Integer, String
from app.database.db import Base

class PaisIsoModel(Base):
    __tablename__ = "paises_iso"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    codigo_iso3 = Column(String(3))