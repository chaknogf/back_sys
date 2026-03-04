from sqlalchemy import Column, Integer, String, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database.db import Base


class ConstanciaNacimientoHistorialModel(Base):
    __tablename__ = "constancia_nacimiento_historial"

    id = Column(Integer, primary_key=True)

    constancia_id = Column(
        Integer,
        ForeignKey("constancia_nacimiento.id", ondelete="CASCADE"),
        nullable=False
    )

    datos_anteriores = Column(JSONB, nullable=False)

    usuario_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    motivo = Column(String(255), nullable=False)

    fecha = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP"))

    constancia = relationship("ConstanciaNacimientoModel", back_populates="historial")