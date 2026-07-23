from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, text
from core.database import Base


class PersonalSaludModel(Base):
    __tablename__ = "personal_salud"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(200), nullable=False, unique=True, index=True)
    especialidad = Column(String(100), nullable=True)
    medico_id = Column(Integer, ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP"))
