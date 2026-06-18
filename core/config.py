from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv(override=True)

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "e87cbfc88ff202c6442638d03d576513d01c153e8e1bdeb2eebc4832088ec9be"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM", "ticshosptecpan@gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_TLS = os.getenv("MAIL_TLS", "true").lower() == "true"
MAIL_SSL = os.getenv("MAIL_SSL", "false").lower() == "true"

# SIGSAS Database
SIGSAS_USER = os.getenv("SIGSAS_USER", "postgres")
SIGSAS_PASSWORD = os.getenv("SIGSAS_PASSWORD", "postgres")
SIGSAS_DB = os.getenv("SIGSAS_DB", "sigsas")
SIGSAS_HOST = os.getenv("SIGSAS_HOST", "localhost")
SIGSAS_PORT = int(os.getenv("SIGSAS_PORT", "5432"))
