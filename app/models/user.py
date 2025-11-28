# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.db import Base
from datetime import datetime

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        server_default=text("nextval('users_id_seq')"),  # ESTA LÍNEA ES LA CLAVE
        autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    unidad: Mapped[int] = mapped_column(Integer, nullable=True)
    estado: Mapped[str] = mapped_column(String(1), server_default="A", nullable=False)
    
    # creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # actualizado_en: Mapped[datetime] = mapped_column(
    #     DateTime(timezone=True), 
    #     server_default=func.now(), 
    #     onupdate=func.now()
    # )