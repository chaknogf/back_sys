from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv(override=True)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY no configurada. "
        "Copia .env.example a .env y genera una clave con: "
        "python -c \"import secrets; print(secrets.token_hex(32))\""
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ────────────────────────────────
# CONCURRENCIA Y ESCALABILIDAD
# ────────────────────────────────
# Número de workers para producción (uvicorn/gunicorn)
WORKERS_PER_NODE = int(os.getenv("WORKERS", "4"))
# Pool de conexiones por worker (pool_size * workers <= max_connections de PostgreSQL)
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM", "ticshosptecpan@gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_TLS = os.getenv("MAIL_TLS", "true").lower() == "true"
MAIL_SSL = os.getenv("MAIL_SSL", "false").lower() == "true"

CIE10_LLM_API_KEY = os.getenv("CIE10_LLM_API_KEY", "")
CIE10_LLM_MODEL = os.getenv("CIE10_LLM_MODEL", "phi3:mini")
CIE10_LLM_PROVIDER = os.getenv("CIE10_LLM_PROVIDER", "ollama")
CIE10_LLM_BASE_URL = os.getenv("CIE10_LLM_BASE_URL", "https://api.openai.com/v1")

# Chat Inteligente (NL→SQL)
CHAT_LLM_API_KEY = os.getenv("CHAT_LLM_API_KEY", "")
CHAT_LLM_MODEL = os.getenv("CHAT_LLM_MODEL", "phi3:mini")
CHAT_LLM_PROVIDER = os.getenv("CHAT_LLM_PROVIDER", "ollama")
CHAT_LLM_BASE_URL = os.getenv("CHAT_LLM_BASE_URL", "https://api.openai.com/v1")

# Usuario read-only para chat (opcional, misma DB si no se configura)
POSTGRES_RO_USER = os.getenv("POSTGRES_RO_USER", "")
POSTGRES_RO_PASSWORD = os.getenv("POSTGRES_RO_PASSWORD", "")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Opencode server (gateway a modelos como Claude, GPT, Zen, etc.)
OPENCODE_SERVER_URL = os.getenv("OPENCODE_SERVER_URL", "http://127.0.0.1:4096")
OPENCODE_SERVER_PASSWORD = os.getenv("OPENCODE_SERVER_PASSWORD", "")

