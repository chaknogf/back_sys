# modules/consultas/models.py
from sqlalchemy import BigInteger, Boolean, Column, Integer, String, Date, Text, Time, ForeignKey, Index, text, desc
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from core.database import Base


class ConsultaHistorialModel(Base):
    __tablename__ = "consultas_historial"

    id = Column(Integer, primary_key=True, autoincrement=True)
    consulta_id = Column(Integer, ForeignKey("consultas.id", ondelete="CASCADE"), nullable=False, index=True)
    estado = Column(String(50), nullable=False)
    registro = Column(Text, nullable=False)
    usuario = Column(String(100), nullable=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    especialidad = Column(String(100), nullable=True)
    servicio = Column(String(50), nullable=True)
    comentario = Column(Text, nullable=True)
    created_at = Column(Text, nullable=True, server_default=text("NOW()"))

    consulta = relationship("ConsultaModel", back_populates="historial")


class ConsultaModel(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    expediente = Column(String(20), nullable=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_consulta = Column(Integer, nullable=False, index=True)
    especialidad = Column(String(50), nullable=False)
    especialidad_id = Column(Integer, ForeignKey("especialidades.id", ondelete="SET NULL"), nullable=True, index=True)
    servicio = Column(String(50), nullable=False)
    documento = Column(String(20), nullable=False)
    fecha_consulta = Column(Date, nullable=False, index=True)
    hora_consulta = Column(Time, nullable=False)
    indicadores = Column(JSONB, nullable=True)
    ciclo = Column(JSONB, nullable=True)
    orden = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True)
    egreso = Column(JSONB, nullable=True)
    registro_medico = Column(String(50), nullable=True)
    condicion_egreso = Column(String(100), nullable=True)
    fecha_egreso = Column(Date, nullable=True)
    ultimo_estado = Column(String(50), nullable=True, index=True)

    paciente = relationship("PacienteModel", back_populates="consultas")
    especialidad_ref = relationship("EspecialidadModel", lazy="joined")
    ciclos = relationship("CiclosConsulta", back_populates="consulta")
    laboratorios = relationship("Laboratorios", back_populates="consulta")
    rayos_x = relationship("RayosX", back_populates="consulta")
    eventos = relationship("EventoConsultaModel", back_populates="consulta")
    historial = relationship("ConsultaHistorialModel", back_populates="consulta", order_by="ConsultaHistorialModel.id",
                              cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_consulta_paciente_tipo_fecha", "paciente_id", "tipo_consulta", "fecha_consulta"),
        Index("idx_consulta_fecha_desc", text("fecha_consulta DESC")),
        Index("idx_consulta_tipo_especialidad", "tipo_consulta", "especialidad"),
        Index("idx_consulta_servicio_documento", "servicio", "documento"),
        Index("idx_consulta_documento_fecha", "documento", "fecha_consulta"),
        Index("idx_consulta_ultimo_estado", "ultimo_estado"),
    )
