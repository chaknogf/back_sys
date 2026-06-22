from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from .schemas import NacimientoCreate, NacimientoUpdate, NacimientoOut, NacimientoListResponse, LegacyReferenceResponse
from .service import (
    crear_nacimiento_desde_paciente as service_desde_paciente,
    crear_nacimiento as service_crear,
    listar_nacimientos as service_listar,
    obtener_nacimiento as service_obtener,
    actualizar_nacimiento as service_actualizar,
    eliminar_nacimiento as service_eliminar,
    sincronizar_nacimientos as service_sincronizar,
    referenciar_legacy as service_referenciar_legacy,
)

router = APIRouter(
    prefix="/nacimientos",
    tags=["Nacimientos"]
)


@router.post("/desde-paciente/{paciente_id}", response_model=NacimientoOut, status_code=201)
def crear_desde_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
):
    return service_desde_paciente(paciente_id, registrador_id=None, db=db)


@router.post("/", response_model=NacimientoOut, status_code=201)
def crear_nacimiento(
    data: NacimientoCreate,
    db: Session = Depends(get_db),
):
    return service_crear(data, db)


@router.get("/", response_model=NacimientoListResponse)
def listar_nacimientos(
    q: Optional[str] = Query(None, description="Búsqueda por nombre"),
    expediente: Optional[str] = Query(None, description="Filtrar por expediente del neonato"),
    sexo: Optional[str] = Query(None, description="Filtrar por sexo (M/F)"),
    fecha_desde: Optional[date] = Query(None, description="Fecha nacimiento desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha nacimiento hasta (YYYY-MM-DD)"),
    clasificacion: Optional[str] = Query(None, description="Filtrar por clasificación (EBP/MBP/BP/PN)"),
    trabajo_parto: Optional[str] = Query(None, description="Filtrar por trabajo de parto (Prematuro/a Termino/Prolongado)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    nacimientos, total = service_listar(
        db=db, q=q, expediente=expediente, sexo=sexo,
        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        clasificacion=clasificacion, trabajo_parto=trabajo_parto,
        skip=skip, limit=limit,
    )
    return NacimientoListResponse(total=total, nacimientos=nacimientos)


@router.get("/{nacimiento_id}", response_model=NacimientoOut)
def obtener_nacimiento(
    nacimiento_id: int,
    db: Session = Depends(get_db),
):
    return service_obtener(nacimiento_id, db)


@router.patch("/{nacimiento_id}", response_model=NacimientoOut)
def actualizar_nacimiento(
    nacimiento_id: int,
    data: NacimientoUpdate,
    db: Session = Depends(get_db),
):
    return service_actualizar(nacimiento_id, data, db)


@router.delete("/{nacimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_nacimiento(
    nacimiento_id: int,
    db: Session = Depends(get_db),
):
    return service_eliminar(nacimiento_id, db)


@router.post("/sincronizar")
def sincronizar(
    db: Session = Depends(get_db),
):
    resultado = service_sincronizar(db, registrador_id=None)
    return resultado


@router.get("/referenciar-legacy", response_model=LegacyReferenceResponse)
def referenciar_legacy(
    limit: int = Query(500, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    solo_sin_match: bool = Query(False, description="Solo registros legacy sin match en pacientes"),
    db: Session = Depends(get_db),
):
    return service_referenciar_legacy(
        db=db, limit=limit, offset=offset, solo_sin_match=solo_sin_match
    )
