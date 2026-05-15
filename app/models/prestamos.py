from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.orm import relationship
from app.database.db import Base


class Prestamo(Base):
    __tablename__ = "prestamos"
    id = Column(BigInteger, primary_key=True, index=True)
    id_paciente = Column(
        BigInteger,
        ForeignKey("pacientes.id"),
        nullable=False
    )
    id_consulta = Column(
        BigInteger,
        ForeignKey("consultas.id", ondelete="SET NULL"),
        nullable=True
    )
    expediente = Column(String(50))
    fecha_prestamo = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    fecha_limite = Column(DateTime(timezone=True))
    fecha_devolucion = Column(DateTime(timezone=True))
    usuario_entrega = Column(String(20))
    usuario_recibe = Column(String(20))
    solicitante = Column(String(150), nullable=False)
    motivo = Column(Text)
    tipo_documento = Column(
        String(50),
        default="EXPEDIENTE"
    )
    activo = Column(
        Boolean,
        nullable=False,
        default=True
    )
    ubicacion = Column(String(100))
    nota = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    # Relaciones
    paciente = relationship("PacienteModel", lazy="joined")

    consulta = relationship("ConsultaModel", lazy="joined")