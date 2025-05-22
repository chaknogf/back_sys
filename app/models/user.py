from sqlalchemy import CHAR, Column, Integer, String, TIMESTAMP, func
from app.database.db import Base

class UserModel(Base):
   __tablename__ = "users"

   id = Column(Integer, primary_key=True, index=True)
   nombre = Column(String(100), nullable=False)
   username = Column(String(50), unique=True, nullable=False)
   email = Column(String(100), unique=True, nullable=False)
   password = Column(String(255), nullable=False)
   role = Column(String(50), nullable=False)
   estado = Column(CHAR(1), default='A')
