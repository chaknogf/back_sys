from sqlalchemy import Column, Integer, String, BigInteger, Boolean, TIMESTAMP, text, Index, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class MedicoModel(Base):
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    colegiado = Column(String(20), unique=True, index=True)
    pasaporte = Column(String(20), index=True)
    dpi = Column(BigInteger, index=True)
    sexo = Column(String(1))
    especialidad_id = Column(Integer, ForeignKey("especialidades.id", ondelete="SET NULL"), nullable=True, index=True)
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(
        TIMESTAMP(timezone=False),
        server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        Index("idx_medicos_activo", "activo"),
        Index("idx_medicos_colegiado", "colegiado"),
        Index("idx_medicos_pasaporte", "pasaporte"),
        Index("idx_medicos_dpi", "dpi"),
        Index("idx_medicos_nombre", "nombre"),
    )

    constancias = relationship(
        "ConstanciaNacimientoModel",
        back_populates="medico"
    )
    especialidad_ref = relationship("EspecialidadModel", lazy="joined")

    @property
    def especialidad_nombre(self):
        return self.especialidad_ref.nombre if self.especialidad_ref else None
