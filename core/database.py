from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

from core.config import DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_RECYCLE
from core.config import POSTGRES_RO_USER, POSTGRES_RO_PASSWORD

load_dotenv(override=True)

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "hospital")

if not POSTGRES_USER or not POSTGRES_PASSWORD:
    raise RuntimeError(
        "POSTGRES_USER y POSTGRES_PASSWORD deben configurarse en .env "
        "Copia .env.example a .env y completa los valores."
    )

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{quote_plus(POSTGRES_PASSWORD)}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_recycle=DB_POOL_RECYCLE,
    connect_args={
        "connect_timeout": 10,
        "options": "-c client_encoding=UTF8 -c statement_timeout=300000"
    }
)

# ── Engine read-only (usuario con solo SELECT) ──
_engine_ro = None
if POSTGRES_RO_USER and POSTGRES_RO_PASSWORD:
    DATABASE_URL_RO = (
        f"postgresql+psycopg2://{POSTGRES_RO_USER}:"
        f"{quote_plus(POSTGRES_RO_PASSWORD)}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    _engine_ro = create_engine(
        DATABASE_URL_RO,
        echo=False,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=4,
        pool_recycle=DB_POOL_RECYCLE,
        connect_args={
            "connect_timeout": 10,
            "options": "-c client_encoding=UTF8 -c statement_timeout=30000",
        },
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


_SessionRO = None  # Lazy init


def get_db_readonly() -> Session:
    global _SessionRO
    if _engine_ro:
        if _SessionRO is None:
            _SessionRO = sessionmaker(autocommit=False, autoflush=False, bind=_engine_ro)
        db = _SessionRO()
    else:
        db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

