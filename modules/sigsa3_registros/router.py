from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from modules.users.models import UserModel
from .schemas import (
    Sigsa3RegistroCreate,
    Sigsa3RegistroUpdate,
    Sigsa3RegistroOut,
    Sigsa3RegistroListResponse,
)
from .service import (
    listar_registros as service_listar,
    obtener_registro as service_obtener,
    crear_registro as service_crear,
    actualizar_registro as service_actualizar,
    eliminar_registro as service_eliminar,
)

router = APIRouter(
    prefix="/sigsa3-registros",
    tags=["SIGSA-3 Registros"],
)


@router.get("/", response_model=Sigsa3RegistroListResponse)
def listar(
    paciente_id: Optional[int] = Query(None, description="Filtrar por ID de paciente"),
    medico_id: Optional[int] = Query(None, description="Filtrar por ID de médico"),
    personal_salud_id: Optional[int] = Query(None, description="Filtrar por ID de personal de salud"),
    consulta_id: Optional[int] = Query(None, description="Filtrar por ID de consulta"),
    tipo_consulta_id: Optional[int] = Query(None, description="Filtrar por tipo de consulta"),
    especialidad_id: Optional[int] = Query(None, description="Filtrar por especialidad"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    q: Optional[str] = Query(None, max_length=200, description="Búsqueda general (paciente, expediente, médico, CIE-10, especialidad)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    registros, total = service_listar(
        db=db,
        paciente_id=paciente_id,
        medico_id=medico_id,
        personal_salud_id=personal_salud_id,
        consulta_id=consulta_id,
        tipo_consulta_id=tipo_consulta_id,
        especialidad_id=especialidad_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        q=q,
        skip=skip,
        limit=limit,
    )
    return Sigsa3RegistroListResponse(total=total, registros=registros)


@router.get("/{registro_id}", response_model=Sigsa3RegistroOut)
def obtener(
    registro_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_obtener(registro_id, db)


@router.post("/", response_model=Sigsa3RegistroOut, status_code=status.HTTP_201_CREATED)
def crear(
    data: Sigsa3RegistroCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_crear(data, db)


@router.patch("/{registro_id}", response_model=Sigsa3RegistroOut)
def actualizar(
    registro_id: int,
    data: Sigsa3RegistroUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_actualizar(registro_id, data, db)


@router.delete("/{registro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    registro_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_eliminar(registro_id, db)
