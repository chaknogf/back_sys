from sqlalchemy import Column, Integer, String, DateTime, Text
from core.database import Base
from datetime import datetime, timezone


class AuditLogModel(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_hora = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    username = Column(String(100), nullable=False)
    tabla = Column(String(100), nullable=False)
    registro_id = Column(Integer, nullable=True)
    endpoint = Column(String(255), nullable=False)
    metodo = Column(String(10), nullable=False, default="GET")
