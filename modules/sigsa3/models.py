from sqlalchemy import Column, BigInteger, Integer, String, Text, Date, SmallInteger, ForeignKey, TIMESTAMP, Index, text
from sqlalchemy.orm import relationship
from core.database import Base


class Sigsa3Model(Base):
    """Staging: registros sin normalizar. Se migra a Sigsa3Registro cuando tiene paciente_id y medico_id."""
    __tablename__ = "sigsa3"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="SET NULL"), nullable=True, index=True)
    medico_id = Column(Integer, ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True, index=True)
    consulta_id = Column(Integer, ForeignKey("consultas.id", ondelete="SET NULL"), nullable=True, index=True)
    personal_salud_id = Column(Integer, ForeignKey("personal_salud.id", ondelete="SET NULL"), nullable=True, index=True)
    personal_salud = Column(String(100), nullable=True)
    fecha_consulta = Column(Date, nullable=True)
    no_historia_clinica = Column(String(30), nullable=True)
    nombre_paciente = Column(String(150), nullable=True)
    sexo = Column(String(1), nullable=True)
    edad_dias = Column(Integer, nullable=True)
    edad_meses = Column(Integer, nullable=True)
    edad_anios = Column(Integer, nullable=True)
    tipo_consulta = Column(String(80), nullable=True)
    tipo_consulta_id = Column(SmallInteger, ForeignKey("tipos_consulta_sigsa3.id", ondelete="SET NULL"), nullable=True, index=True)
    control = Column(String(80), nullable=True)
    semana_gestacional = Column(Integer, nullable=True)
    codigo_cie_10_id = Column(Integer, ForeignKey("cie10_catalogo.id", ondelete="SET NULL"), nullable=True, index=True)
    codigo_cie_10 = Column(String(30), nullable=True)
    dx = Column(Text, nullable=True)
    especialidad_id = Column(Integer, ForeignKey("especialidades.id", ondelete="SET NULL"), nullable=True, index=True)

    __table_args__ = (
        Index("ix_sigsa3_nombre_paciente", "nombre_paciente"),
        Index("ix_sigsa3_no_historia_clinica", "no_historia_clinica"),
        Index("ix_sigsa3_fecha_consulta", "fecha_consulta"),
        Index("ix_sigsa3_paciente_fecha", "paciente_id", "fecha_consulta"),
        Index("ix_sigsa3_nhc_fecha", "no_historia_clinica", "fecha_consulta"),
        Index("ix_sigsa3_personal_salud_id", "personal_salud_id"),
        Index("ix_sigsa3_codigo_cie10_id", "codigo_cie_10_id"),
        Index("ix_sigsa3_especialidad_id", "especialidad_id"),
    )

    especialidad_ref = relationship("EspecialidadModel", lazy="joined")

    @property
    def especialidad_nombre(self):
        return self.especialidad_ref.nombre if self.especialidad_ref else None


class Sigsa3RegistroModel(Base):
    """Normalizado: solo FKs, sin datos redundantes."""
    __tablename__ = "sigsa3_registros"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="SET NULL"), nullable=False, index=True)
    medico_id = Column(Integer, ForeignKey("medicos.id", ondelete="SET NULL"), nullable=False, index=True)
    personal_salud_id = Column(Integer, ForeignKey("personal_salud.id", ondelete="SET NULL"), nullable=True, index=True)
    consulta_id = Column(Integer, ForeignKey("consultas.id", ondelete="SET NULL"), nullable=True, index=True)
    fecha_consulta = Column(Date, nullable=False, index=True)
    tipo_consulta_id = Column(SmallInteger, ForeignKey("tipos_consulta_sigsa3.id", ondelete="SET NULL"), nullable=True, index=True)
    control = Column(String(80), nullable=True)
    semana_gestacional = Column(Integer, nullable=True)
    codigo_cie_10_id = Column(Integer, ForeignKey("cie10_catalogo.id", ondelete="SET NULL"), nullable=True, index=True)
    especialidad_id = Column(Integer, ForeignKey("especialidades.id", ondelete="SET NULL"), nullable=True, index=True)
    # ID del registro staging (sigsa3) de origen. Sin FK (default NULL) para
    # evitar restricciones al purgar staging tras normalizar.
    sigsa3_id = Column(BigInteger, nullable=True, default=None, index=True)
    normalized_at = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        Index("ix_sigsa3_reg_paciente_fecha", "paciente_id", "fecha_consulta"),
        Index("ix_sigsa3_reg_fecha", "fecha_consulta"),
        Index("ix_sigsa3_reg_sigsa3_id", "sigsa3_id"),
    )
