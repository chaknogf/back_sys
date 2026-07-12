import os
import httpx
from typing import Dict
from .schemas import RespuestaRenap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT = (
    os.path.join(BASE_DIR, "ssl/client.cert.pem"),
    os.path.join(BASE_DIR, "ssl/client.key.pem"),
)

API_KEY = os.getenv("RENAP_API_KEY") or ""
API_URL = "https://salud-digital.mspas.gob.gt/personas"


async def fetch_persona(filtros: Dict[str, str]) -> RespuestaRenap:
    if not API_KEY:
        raise RuntimeError(
            "RENAP_API_KEY no configurada. "
            "Agrega RENAP_API_KEY a tu .env"
        )
    headers = {
        "accept": "application/json",
        "x-api-key": API_KEY
    }

    async with httpx.AsyncClient(
        cert=CERT,
        verify=True,
        timeout=40.0,
        transport=httpx.AsyncHTTPTransport(
            retries=2,
        )
    ) as client:
        try:
            response = await client.get(API_URL, params=filtros, headers=headers)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            try:
                data = e.response.json()
            except:
                data = {"error": True, "mensaje": f"Error HTTP {e.response.status_code}"}
        except Exception as e:
            return RespuestaRenap(
                error=True,
                mensaje=f"Error de red con RENAP: {str(e)[:120]}",
                resultado=[],
                solicitudes_restantes=0
            )

    for persona in data.get("resultado", []):
        if "CUI" in persona and persona["CUI"]:
            persona["CUI"] = str(persona["CUI"]).zfill(13)

    return RespuestaRenap(**data)
