# app/database/db.py
"""
Conexión a base de datos y dependencia get_db().
Compatible con SQLAlchemy 2.0+ y FastAPI.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# ======================
# CONFIGURACIÓN BD
# ======================
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secreto123")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "hospital")

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{quote_plus(POSTGRES_PASSWORD)}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ======================
# MOTOR Y SESIÓN
# ======================
engine = create_engine(
    DATABASE_URL,
    echo=False,  # echo=True solo en desarrollo
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"connect_timeout": 10}
)

# Test de conexión al iniciar
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Conexión a PostgreSQL exitosa")
except Exception as e:
    print(f"Error conectando a PostgreSQL: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ======================
# DEPENDENCIA FASTAPI
# ======================
def get_db() -> Session:
    """
    Dependencia de FastAPI para inyectar sesión de BD.
    Uso: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()