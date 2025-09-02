# app/services/renap_service.py
import os
from typing import Dict
import httpx
from app.models.renap import RespuestaRenap

# Construir rutas absolutas a los certificados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # app/services
CERT = (
    os.path.join(BASE_DIR, "ssl/client.cert.pem"),
    os.path.join(BASE_DIR, "ssl/client.key.pem"),
)
API_KEY = "b6039f4a35ae824f9d7abe6a8bda8f7d5e590cfd9ee53ba87dce37b890588fb3"


API_URL = "https://salud-digital.mspas.gob.gt/personas"

async def fetch_persona(filtros: Dict[str, str]) -> RespuestaRenap:
    """
    Consulta el endpoint de RENAP con los filtros proporcionados usando solo certificados.
    Maneja automáticamente errores de la API y garantiza compatibilidad con el modelo Pydantic.
    """
    headers = {
        "accept": "application/json",
        "x-api-key": API_KEY
        
    }

    async with httpx.AsyncClient(
        cert=CERT, 
        verify=True, 
        timeout=40.0
        ) as client:
        try:
            # Request GET con certificados
            response = await client.get(API_URL, params=filtros, headers=headers)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            # Si la API responde con error HTTP (400, 401, etc.), devolvemos lo que venga
            data = e.response.json()
        except httpx.RequestError as e:
            # Problemas de conexión
            return RespuestaRenap(
                error=True,
                mensaje=f"Error de conexión con RENAP: {str(e)}",
                resultado=[],
                solicitudes_restantes=0
            )

    # Asegurar que los campos obligatorios existan
    data.setdefault("resultado", [])
    data.setdefault("solicitudes_restantes", 0)

    # Convertir CUI a string si viene como número
    for persona in data.get("resultado", []):
        if "CUI" in persona and persona["CUI"] is not None:
            persona["CUI"] = str(persona["CUI"])

    return RespuestaRenap(**data)