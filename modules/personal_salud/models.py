from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from core.database import Base


class PersonalSaludModel(Base):
    __tablename__ = "personal_salud"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(200), nullable=False, unique=True, index=True)
    especialidad_id = Column(Integer, ForeignKey("especialidades.id", ondelete="SET NULL"), nullable=True, index=True)
    medico_id = Column(Integer, ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP"))
    especialidad_ref = relationship("EspecialidadModel", lazy="joined")

    @property
    def especialidad_nombre(self):
        return self.especialidad_ref.nombre if self.especialidad_ref else None
