from starlette.middleware.base import BaseHTTPMiddleware

from .service import client_ip_var, obtener_ip


class AuditClientIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        client_ip_var.set(obtener_ip(request))
        return await call_next(request)