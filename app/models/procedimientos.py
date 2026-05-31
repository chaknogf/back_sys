# app/models/procedimientos.py
from sqlalchemy import Column, Integer, String, Text, Date, CHAR, TIMESTAMP, CheckConstraint, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.db import Base  # Asume que tienes tu base declarativa

class Procedimiento(Base):
    __tablename__ = "procedimientos"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, primary_key=True, index=True)
    abreviatura = Column(String(10), unique=True, nullable=True)
    nombre = Column(String(200), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    anestesia = Column(Integer, nullable=True, default=0)
    
    # Relaciones
    proce_medicos = relationship("ProceMedico", back_populates="procedimiento")

class ProceMedico(Base):
    __tablename__ = "proce_medicos"
    __table_args__ = (
        CheckConstraint("cantidad >= 1", name="proce_medicos_cantidad_check"),
        CheckConstraint("sexo IN ('M', 'F')", name="proce_medicos_sexo_check"),
        {"schema": "public"}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=True)
    lugar_servicio = Column(String(10), nullable=True)
    sexo = Column(CHAR(1), nullable=True)
    id_procedimiento = Column(Integer, ForeignKey("public.procedimientos.id", ondelete="SET NULL"), nullable=True)
    especialidad = Column(String(10), nullable=True)
    cantidad = Column(Integer, nullable=False, default=1)
    responsable = Column(String(20), nullable=True)
    anestesia = Column(Integer, nullable=True, default=0)
    created_by = Column(String(10), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    procedimiento = relationship("Procedimiento", back_populates="proce_medicos")
   