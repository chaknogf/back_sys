from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi_cache.decorator import cache
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.database import get_db
from core.limiter import limiter
from core.security import get_current_user
from modules.users.models import UserModel
from modules.cie10.models import Cie10Model
from modules.cie10.schemas import (
    Cie10Out, Cie10SearchResponse, Cie10ChatRequest, Cie10ChatResponse,
)
from core.config import CIE10_LLM_MODEL, CIE10_LLM_PROVIDER, OLLAMA_HOST
from modules.cie10.service import (
    buscar_cie10, asegurar_catalogo, buscar_relevantes, responder_pregunta,
)
from modules.sigsa3.models import Sigsa3Model


router = APIRouter(prefix="/cie10", tags=["CIE-10"])


@router.get("/", response_model=Cie10SearchResponse)
@cache(expire=300)
def buscar_diagnosticos(
    q: str = Query(..., min_length=1, max_length=200,
                   description="Búsqueda por código o descripción"),
    nivel: Optional[int] = Query(None, ge=0, le=5),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    asegurar_catalogo(db)
    resultados, total = buscar_cie10(db, q=q, nivel=nivel, limit=limit, offset=offset)
    return Cie10SearchResponse(
        total=total,
        resultados=[Cie10Out.model_validate(r) for r in resultados],
        consulta=q,
    )


@router.post("/consultar", response_model=Cie10ChatResponse)
@limiter.limit("5/minute")
def consultar_cie10(
    request: Request,
    body: Cie10ChatRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    asegurar_catalogo(db)
    mensajes = [m.model_dump() for m in body.mensajes]
    try:
        respuesta = responder_pregunta(
            mensajes=mensajes,
            codigos_contexto=body.codigos_contexto,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error del LLM: {str(e)}")

    ultimo_user = next(
        (m.content for m in reversed(body.mensajes) if m.role == "user"),
        "",
    )
    codigos_rels = (
        body.codigos_contexto
        if body.codigos_contexto
        else [c.codigo for c in buscar_relevantes(db, ultimo_user, limite=5)]
    )
    codigos_relacionados = []
    if codigos_rels:
        codigos = (
            db.query(Cie10Model)
            .filter(Cie10Model.codigo.in_(codigos_rels))
            .all()
        )
        codigos_relacionados = [Cie10Out.model_validate(c) for c in codigos]

    return Cie10ChatResponse(
        respuesta=respuesta,
        codigos_relacionados=codigos_relacionados,
        modelo=f"{CIE10_LLM_PROVIDER}:{CIE10_LLM_MODEL}" + (f" @ {OLLAMA_HOST}" if CIE10_LLM_PROVIDER == "ollama" else ""),
        generado_en=datetime.now(timezone.utc),
    )


@router.get("/usados", response_model=List[Cie10Out])
@cache(expire=3600)
def diagnosticos_usados(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    rows = (
        db.query(
            Sigsa3Model.codigo_cie_10,
            func.count(Sigsa3Model.id).label("total"),
        )
        .filter(
            Sigsa3Model.codigo_cie_10.isnot(None),
            Sigsa3Model.codigo_cie_10 != "",
        )
        .group_by(Sigsa3Model.codigo_cie_10)
        .order_by(func.count(Sigsa3Model.id).desc())
        .limit(limit)
        .all()
    )

    codigos = [r.codigo_cie_10 for r in rows if r.codigo_cie_10]
    if not codigos:
        return []

    modelos = (
        db.query(Cie10Model)
        .filter(Cie10Model.codigo.in_(codigos))
        .all()
    )
    mapa = {m.codigo: m for m in modelos}
    resultado = []
    for codigo in codigos:
        if codigo in mapa:
            resultado.append(Cie10Out.model_validate(mapa[codigo]))

    return resultado
