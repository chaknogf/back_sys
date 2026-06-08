from sqlalchemy import Column, Integer, String, DateTime, text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from datetime import datetime


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        server_default=text("nextval('users_id_seq')"),
        autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    unidad: Mapped[int] = mapped_column(Integer, nullable=True)
    estado: Mapped[str] = mapped_column(String(1), server_default="A", nullable=False)
    datos_extra: Mapped[dict] = mapped_column(JSON, nullable=True)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
