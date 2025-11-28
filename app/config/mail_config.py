# app/config/mail_config.py
from fastapi_mail import ConnectionConfig
import os
from dotenv import load_dotenv

load_dotenv(override=True)

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM", "ticshosptecpan@gmail.com"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Hospital Tecpán"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    # ESTA ES LA CLAVE MÁGICA EN LA VERSIÓN NUEVA:
    VALIDATE_CERTS=False,        # ← ¡SOLO ESTA LÍNEA!
)