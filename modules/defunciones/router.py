from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from modules.pacientes.models import PacienteModel
from modules.pacientes.service import agregar_evento
from modules.defunciones.schemas import (
    DefuncionCreate, DefuncionUpdate, DefuncionOut, DefuncionListResponse,
    PacientesFallecidosResponse, RegistrarDefuncionRequest,
)
from modules.defunciones.service import (
    crear_defuncion as service_crear,
    listar_defunciones as service_listar,
    obtener_defuncion as service_obtener,
    actualizar_defuncion as service_actualizar,
    eliminar_defuncion as service_eliminar,
    buscar_pacientes_fallecidos as service_buscar_fallecidos,
)

router = APIRouter(
    prefix="/defunciones",
    tags=["Defunciones"],
)


@router.post("/", response_model=DefuncionOut, status_code=201)
def crear_defuncion(
    data: DefuncionCreate,
    db: Session = Depends(get_db),
):
    return service_crear(data, registrador_id=None, db=db)


@router.post("/registrar/{paciente_id}", response_model=DefuncionOut, status_code=201)
def registrar_defuncion(
    paciente_id: int,
    data: RegistrarDefuncionRequest,
    db: Session = Depends(get_db),
):
    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if paciente.estado == "F":
        raise HTTPException(status_code=400, detail="El paciente ya tiene estado Fallecido")

    create_data = DefuncionCreate(
        paciente_id=paciente_id,
        **data.model_dump(exclude_unset=True),
    )
    resultado = service_crear(create_data, registrador_id=None, db=db)

    paciente.estado = "F"
    agregar_evento(paciente, usuario="sistema", accion="ACTUALIZADO")
    db.commit()

    return resultado


@router.get("/", response_model=DefuncionListResponse)
def listar_defunciones(
    q: Optional[str] = Query(None, description="Búsqueda por nombre del fallecido, madre o médico"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha defunción desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha defunción hasta (YYYY-MM-DD)"),
    es_fetal: Optional[bool] = Query(None, description="Filtrar por defunción fetal"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    defunciones, total = service_listar(
        db=db, q=q, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        es_fetal=es_fetal, skip=skip, limit=limit,
    )
    return DefuncionListResponse(total=total, defunciones=defunciones)


@router.get("/pacientes", response_model=PacientesFallecidosResponse)
def buscar_pacientes_fallecidos(
    q: Optional[str] = Query(None, description="Búsqueda por nombre"),
    expediente: Optional[str] = Query(None, description="Filtrar por expediente"),
    cui: Optional[str] = Query(None, description="Filtrar por CUI"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    pacientes, total = service_buscar_fallecidos(
        db=db, q=q, expediente=expediente, cui=cui,
        skip=skip, limit=limit,
    )
    return PacientesFallecidosResponse(total=total, pacientes=pacientes)


@router.get("/{defuncion_id}", response_model=DefuncionOut)
def obtener_defuncion(
    defuncion_id: int,
    db: Session = Depends(get_db),
):
    return service_obtener(defuncion_id, db)


@router.patch("/{defuncion_id}", response_model=DefuncionOut)
def actualizar_defuncion(
    defuncion_id: int,
    data: DefuncionUpdate,
    db: Session = Depends(get_db),
):
    return service_actualizar(defuncion_id, data, db)


@router.delete("/{defuncion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_defuncion(
    defuncion_id: int,
    db: Session = Depends(get_db),
):
    return service_eliminar(defuncion_id, db)
