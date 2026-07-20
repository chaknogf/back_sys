from sqlalchemy import Column, BigInteger, Integer, String, Text, Date, ForeignKey, TIMESTAMP, Index, text
from core.database import Base


class PersonalSaludModel(Base):
    __tablename__ = "personal_salud"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(200), nullable=False, unique=True, index=True)
    especialidad = Column(String(100), nullable=True)
    medico_id = Column(Integer, ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP"))


class Sigsa3Model(Base):
    __tablename__ = "sigsa3"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="SET NULL"), nullable=True, index=True)
    medico_id = Column(Integer, ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True, index=True)
    consulta_id = Column(Integer, ForeignKey("consultas.id", ondelete="SET NULL"), nullable=True, index=True)
    personal_salud = Column(String(100), nullable=True)
    fecha_consulta = Column(Date, nullable=True)
    no_historia_clinica = Column(String(30), nullable=True)
    nombre_paciente = Column(String(150), nullable=True)
    sexo = Column(String(1), nullable=True)
    edad_dias = Column(Integer, nullable=True)
    edad_meses = Column(Integer, nullable=True)
    edad_anios = Column(Integer, nullable=True)
    tipo_consulta = Column(String(80), nullable=True)
    control = Column(String(80), nullable=True)
    semana_gestacional = Column(Integer, nullable=True)
    codigo_cie_10 = Column(String(30), nullable=True)
    dx = Column(Text, nullable=True)
    especialidad = Column(String(100), nullable=True)

    __table_args__ = (
        Index("ix_sigsa3_nombre_paciente", "nombre_paciente"),
        Index("ix_sigsa3_no_historia_clinica", "no_historia_clinica"),
        Index("ix_sigsa3_fecha_consulta", "fecha_consulta"),
        Index("ix_sigsa3_paciente_fecha", "paciente_id", "fecha_consulta"),
        Index("ix_sigsa3_nhc_fecha", "no_historia_clinica", "fecha_consulta"),
    )
