from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from core.database import Base


class NacimientoModel(Base):
    __tablename__ = "nacimientos"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(
        Integer, ForeignKey("pacientes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    madre_id = Column(
        Integer, ForeignKey("pacientes.id", ondelete="SET NULL"), nullable=True, index=True
    )

    peso_gramos = Column(Numeric)
    clasificacion_nacimiento = Column(String(50))
    trabajo_parto = Column(String(50))
    id_legacy = Column(Integer, nullable=True)

    registrador_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    paciente = relationship("PacienteModel", foreign_keys=[paciente_id])
    madre = relationship("PacienteModel", foreign_keys=[madre_id])
    registrador = relationship("UserModel")
