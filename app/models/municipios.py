# app/models/municipios.py
from sqlalchemy import Column, String
from app.database.db import Base


class MunicipiosModel(Base):
    __tablename__ = "municipios"

    codigo = Column(String(5), primary_key=True)
    vecindad = Column(String(150), nullable=True)
    municipio = Column(String(50), nullable=False)
    departamento = Column(String(50), nullable=False)

    def __repr__(self) -> str:
        return f"<Municipio {self.municipio}, {self.departamento}>"