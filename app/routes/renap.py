# renapDPI/router/renap.py
from fastapi import APIRouter, HTTPException, Query
from app.services.renap_service import fetch_persona
from app.models.renap import RespuestaRenap

router = APIRouter()

@router.get("/renap-persona", response_model=RespuestaRenap, tags=["RENAP"])
async def buscar_persona(
    cui: str | None = Query(None, description="CUI de la persona"),
    primer_nombre: str | None = Query(None, description="Primer nombre"),
    segundo_nombre: str | None = Query(None, description="Segundo nombre"),
    primer_apellido: str | None = Query(None, description="Primer apellido"),
    segundo_apellido: str | None = Query(None, description="Segundo apellido"),
    fecha_nacimiento: str | None = Query(None, description="Fecha de nacimiento en formato dd/mm/yyyy")
):
    filtros = {}
    if cui:
        filtros["cui"] = cui
    else:
        if primer_nombre:
            filtros["primer_nombre"] = primer_nombre
        if segundo_nombre:
            filtros["segundo_nombre"] = segundo_nombre
        if primer_apellido:
            filtros["primer_apellido"] = primer_apellido
        if segundo_apellido:
            filtros["segundo_apellido"] = segundo_apellido
        if fecha_nacimiento:
            filtros["fecha_nacimiento"] = fecha_nacimiento

    if not filtros:
        raise HTTPException(status_code=400, detail="No se proporcionaron filtros válidos")
    try:
        return await fetch_persona(filtros)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando RENAP: {str(e)}")