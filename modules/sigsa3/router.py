from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from core.dependencies import get_db, get_current_user
from modules.users.models import UserModel
from .schemas import Sigsa3Create, Sigsa3Update, Sigsa3Out
from .service import (
    listar_registros as service_listar,
    obtener_registro as service_obtener,
    crear_registro as service_crear,
    actualizar_registro as service_actualizar,
    eliminar_registro as service_eliminar,
    generar_plantilla_csv,
    importar_csv,
)

router = APIRouter(
    prefix="/sigsa3",
    tags=["SIGSA-3"],
)


@router.get("/", response_model=List[Sigsa3Out])
def listar(
    personal_salud: Optional[str] = Query(None, max_length=100),
    fecha_consulta: Optional[date] = None,
    no_historia_clinica: Optional[str] = Query(None, max_length=30),
    nombre_paciente: Optional[str] = Query(None, max_length=150),
    sexo: Optional[str] = Query(None, max_length=1),
    tipo_consulta: Optional[str] = Query(None, max_length=80),
    especialidad: Optional[str] = Query(None, max_length=100),
    codigo_cie_10: Optional[str] = Query(None, max_length=30),
    q: Optional[str] = Query(None, max_length=200, description="Búsqueda general"),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_listar(
        db=db,
        personal_salud=personal_salud,
        fecha_consulta=fecha_consulta,
        no_historia_clinica=no_historia_clinica,
        nombre_paciente=nombre_paciente,
        sexo=sexo,
        tipo_consulta=tipo_consulta,
        especialidad=especialidad,
        codigo_cie_10=codigo_cie_10,
        q=q,
        limit=limit,
    )


@router.get("/plantilla-csv", tags=["SIGSA-3"])
def descargar_plantilla(
    current_user: UserModel = Depends(get_current_user),
):
    buf = generar_plantilla_csv()
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="plantilla_sigsa3.csv"'},
    )


@router.post("/importar-csv", tags=["SIGSA-3"])
async def importar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return await importar_csv(file, db)


@router.get("/{registro_id}", response_model=Sigsa3Out)
def obtener(
    registro_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_obtener(registro_id, db)


@router.post("/", response_model=Sigsa3Out, status_code=status.HTTP_201_CREATED)
def crear(
    data: Sigsa3Create,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_crear(data, db)


@router.put("/{registro_id}", response_model=Sigsa3Out)
def actualizar(
    registro_id: int,
    data: Sigsa3Update,
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
