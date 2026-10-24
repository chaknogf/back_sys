"""Rate limiting compartido entre workers/réplicas.

Usa almacenamiento en Redis cuando está configurado (necesario para escalar
horizontalmente: todos los workers/réplicas deben compartir el contador). Si
Redis no está disponible, cae a memoria local con una advertencia explícita.
"""

import logging

from slowapi import Limiter

from core.config import ENVIRONMENT, REDIS_URL
from modules.audit_log.service import obtener_ip

logger = logging.getLogger("core.limiter")


def _client_ip(request) -> str:
    """Clave de rate limit basada en la IP real del cliente (respeta X-Forwarded-For)."""
    return obtener_ip(request) or "unknown"


def _redis_disponible() -> bool:
    """Comprueba conectividad con Redis antes de usarlo como storage."""
    try:
        import redis

        client = redis.Redis.from_url(REDIS_URL, socket_connect_timeout=2)
        client.ping()
        return True
    except Exception as e:  # pragma: no cover - depende del entorno
        logger.warning("Redis no disponible para rate limit: %s", e)
        return False


def _build_limiter() -> Limiter:
    if REDIS_URL and _redis_disponible():
        logger.info("Rate limit con almacenamiento compartido en Redis")
        return Limiter(
            key_func=_client_ip,
            storage_uri=REDIS_URL,
            in_memory_fallback_enabled=True,
        )

    if ENVIRONMENT == "production":
        logger.error(
            "Rate limit en memoria local: no se compartirá entre workers/réplicas. "
            "Configure REDIS_URL y verifique que Redis esté disponible."
        )
    return Limiter(key_func=_client_ip)


limiter = _build_limiter()
