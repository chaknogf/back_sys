from sqlalchemy import Boolean, Column, Integer, String, Text, TIMESTAMP, text, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class DefuncionModel(Base):
    __tablename__ = "defunciones"

    id = Column(Integer, primary_key=True, index=True)

    medico_id = Column(Integer, ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True)
    fecha_defuncion = Column(TIMESTAMP(timezone=True))

    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="SET NULL"), nullable=True, index=True)
    fallecido_edad_horas = Column(Integer)
    fallecido_edad_dias = Column(Integer)
    fallecido_edad_meses = Column(Integer)
    fallecido_edad_anios = Column(Integer)
    mujer_edad_fertil = Column(Boolean, default=False)

    muerte_gestacion = Column(String(30))

    causa_a = Column(Text)
    causa_b = Column(Text)
    causa_c = Column(Text)
    causa_d = Column(Text)
    causa_intervalo = Column(Text)
    causa_otros = Column(Text)

    fue_presunto = Column(String(20))
    lugar_lesion = Column(String(50))
    ocurrio_trabajo = Column(Boolean)
    accidente_transito = Column(Boolean)
    arma = Column(String(200))

    madre_id = Column(Integer, ForeignKey("pacientes.id", ondelete="SET NULL"), nullable=True)
    madre_edad = Column(Integer)
    madre_sabe_leer_escribir = Column(String(10))

    es_fetal = Column(Boolean, default=False)
    embarazos_previvos_vivos = Column(Integer)
    embarazos_previvos_muertos = Column(Integer)
    fetal_sexo = Column(String(1))
    fetal_murio_antes_parto = Column(Boolean)
    fetal_parto_tipo = Column(String(20))
    fetal_clase_parto = Column(String(20))
    fetal_via_parto = Column(String(20))
    fetal_semanas_gestacion = Column(Integer)
    fetal_causas_fetales = Column(Text)
    fetal_causas_maternas = Column(Text)

    registrador_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    observaciones = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    paciente = relationship("PacienteModel", foreign_keys=[paciente_id])
    madre = relationship("PacienteModel", foreign_keys=[madre_id])
    medico = relationship("MedicoModel", foreign_keys=[medico_id])
    registrador = relationship("UserModel")
