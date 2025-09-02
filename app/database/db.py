from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from typing import Generator
from urllib.parse import quote_plus
import os

# Cargar variables de entorno
load_dotenv(dotenv_path=".env", override=True)

# Obtener variables del entorno
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secreto123")
POSTGRES_DB = os.getenv("POSTGRES_DB", "hospital")

# Codificar contraseña
password_encoded = quote_plus(POSTGRES_PASSWORD)

# URL de conexión
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{password_encoded}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Crear motor
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# Probar conexión
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("✅ Conexión a PostgreSQL exitosa 🚀")
except Exception as e:
    print(f"❌ Error de conexión a PostgreSQL: {e}")

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarar base
Base = declarative_base()

# Función de dependencia para obtener la sesión
def get_database_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
