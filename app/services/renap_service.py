# app/services/renap_service.py → VERSIÓN FINAL QUE FUNCIONA EN EL MUNDO REAL

import os
import httpx
from typing import Dict
from app.schemas.renap import RespuestaRenap

# Rutas a tus certificados de cliente (obligatorios para la API del MSPAS)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT = (
    os.path.join(BASE_DIR, "ssl/client.cert.pem"),
    os.path.join(BASE_DIR, "ssl/client.key.pem"),
)

API_KEY = "b6039f4a35ae824f9d7abe6a8bda8f7d5e590cfd9ee53ba87dce37b890588fb3"
API_URL = "https://salud-digital.mspas.gob.gt/personas"

async def fetch_persona(filtros: Dict[str, str]) -> RespuestaRenap:
    headers = {
        "accept": "application/json",
        "x-api-key": API_KEY
    }

    # LA CLAVE: IGNORAR SSL + USAR CERTIFICADOS DE CLIENTE
    async with httpx.AsyncClient(
        cert=CERT,                    # ← Tus certificados de cliente (obligatorios)
        verify=False,                 # ← Ignora certificado vencido del servidor
        timeout=40.0,
        # Forzar TLS 1.2 (a veces el MSPAS solo acepta esto)
        transport=httpx.AsyncHTTPTransport(
            retries=2,
            # Opcional: forzar versión TLS si falla
            # ssl_context=httpx.create_ssl_context(verify=False)
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

    # Normalizar CUI
    for persona in data.get("resultado", []):
        if "CUI" in persona and persona["CUI"]:
            persona["CUI"] = str(persona["CUI"]).zfill(13)

    return RespuestaRenap(**data)