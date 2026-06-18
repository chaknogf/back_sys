from sqlalchemy import Column, Integer, SmallInteger, String, Text, Boolean, TIMESTAMP, text
from core.database import Base


class EncamamientoModel(Base):
    __tablename__ = "encamamiento"

    id = Column(Integer, primary_key=True, index=True)
    nombre_servicio = Column(String(100), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=False, server_default=text("''"))
    camas_censables = Column(SmallInteger, nullable=False, default=0)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
