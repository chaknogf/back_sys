# app/database/config.py
#SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

"""
Configuración global de la aplicación.
NO poner aquí lógica, solo constantes y variables de entorno.
"""

from datetime import timedelta
import os
from dotenv import load_dotenv

# Cargar .env (si existe)
load_dotenv(override=True)

# ======================
# JWT CONFIG
# ======================
# ¡¡¡CÁMBIALA YA!!! Ejecuta: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "e87cbfc88ff202c6442638d03d576513d01c153e8e1bdeb2eebc4832088ec9be"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h por defecto

# ======================
# MAIL CONFIG (opcional, para usar en otros módulos)
# ======================
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM", "ticshosptecpan@gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_TLS = os.getenv("MAIL_TLS", "true").lower() == "true"
MAIL_SSL = os.getenv("MAIL_SSL", "false").lower() == "true"