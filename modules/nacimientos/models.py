from sqlalchemy import Column, Integer, String, Date, Time, Boolean, ForeignKey, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB
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

    expediente = Column(String(20))
    nombre_completo = Column(String(300))
    sexo = Column(String(1))
    fecha_nacimiento = Column(Date)

    peso_nacimiento = Column(String(20))
    edad_gestacional = Column(String(20))
    tipo_parto = Column(String(50))
    clase_parto = Column(String(50))
    gemelo = Column(String(20))
    hora_nacimiento = Column(Time)
    extrahospitalario = Column(Boolean, default=False)
    datos_extra = Column(JSONB, default=dict)

    registrador_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    paciente = relationship("PacienteModel", foreign_keys=[paciente_id])
    madre = relationship("PacienteModel", foreign_keys=[madre_id])
    registrador = relationship("UserModel")
