from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Parámetros de conexión
USER = "admin_user"
PASSWORD = "turbo"
HOST = "localhost"
PORT = "3309"
DATABASE = "pluton"  # Asegúrate de que esta base de datos exista


SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"charset": "utf8mb4"})  # Añadir charset para compatibilidad

# Crear una sesión local para interactuar con la base de datos
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la clase base para los modelos
Base = declarative_base()

