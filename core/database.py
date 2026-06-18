from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv(override=True)

POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secreto123")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "hospital")

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{quote_plus(POSTGRES_PASSWORD)}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "connect_timeout": 10,
        "options": "-c client_encoding=UTF8"
    }
)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Conexión a PostgreSQL exitosa")
except Exception as e:
    print(f"Error conectando a PostgreSQL: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ────────────────────────────────
# SIGSAS DATABASE
# ────────────────────────────────

SIGSAS_USER = os.getenv("SIGSAS_USER", "postgres")
SIGSAS_PASSWORD = os.getenv("SIGSAS_PASSWORD", "postgres")
SIGSAS_HOST = os.getenv("SIGSAS_HOST", "localhost")
SIGSAS_PORT = os.getenv("SIGSAS_PORT", "5432")
SIGSAS_DB = os.getenv("SIGSAS_DB", "sigsas")

SIGSAS_DATABASE_URL = f"postgresql+psycopg2://{SIGSAS_USER}:{quote_plus(SIGSAS_PASSWORD)}@{SIGSAS_HOST}:{SIGSAS_PORT}/{SIGSAS_DB}"

sigsas_engine = create_engine(
    SIGSAS_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "connect_timeout": 10,
        "options": "-c client_encoding=UTF8"
    }
)

try:
    with sigsas_engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Conexión a SIGSAS exitosa")
except Exception as e:
    print(f"⚠️  SIGSAS no disponible ({e}), se usará cuando esté configurada")

SigsasSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sigsas_engine)


def get_sigsas_db() -> Session:
    db = SigsasSessionLocal()
    try:
        yield db
    finally:
        db.close()
