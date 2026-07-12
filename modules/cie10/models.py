from sqlalchemy import Column, Integer, String, Text, Index
from core.database import Base


class Cie10Model(Base):
    __tablename__ = "cie10_catalogo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(10), nullable=False, index=True, unique=True)
    descripcion = Column(Text, nullable=False)
    nivel = Column(Integer, nullable=False, default=0)
    codigo_padre = Column(String(10), nullable=True, index=True)
    fuente = Column(String(20), nullable=True)

    __table_args__ = (
        Index("ix_cie10_descripcion_trgm", "descripcion", postgresql_using="gin",
              postgresql_ops={"descripcion": "gin_trgm_ops"}),
    )

    def __repr__(self):
        return f"<Cie10 {self.codigo}: {self.descripcion[:50]}>"
