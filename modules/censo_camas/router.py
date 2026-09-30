from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, status, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_admin_user
from modules.users.models import UserModel
from .schemas import (
    CensoCamasCreate,
    CensoCamasUpdate,
    CensoCamasOut,
    CensoCamasListResponse,
    CensoDiarioResumen,
    CensoEstadisticasResponse,
    HospitalizacionEspecialidadResponse,
    CopiarDiaRequest,
    CopiarDiaResponse,
    CensoCamasEliminarPorPeriodoRequest,
    CensoCamasEliminarPorPeriodoResponse,
)
from .service import (
    crear_registro as service_crear,
    upsert_registro as service_upsert,
    listar_registros as service_listar,
    obtener_registro as service_obtener,
    actualizar_registro as service_actualizar,
    eliminar_registro as service_eliminar,
    eliminar_por_periodo as service_eliminar_periodo,
    resumen_diario as service_resumen,
    bulk_create as service_bulk,
    estadisticas as service_estadisticas,
    importar_csv as service_importar_csv,
    importar_csv_transversal as service_importar_csv_transversal,
    hospitalizacion_por_especialidad as service_hospitalizacion,
    copiar_dia_anterior as service_copiar_dia,
)

router = APIRouter(
    prefix="/censo-camas",
    tags=["Censo de Camas"]
)


@router.post("/", response_model=CensoCamasOut, status_code=status.HTTP_201_CREATED)
def crear_registro(data: CensoCamasCreate, db: Session = Depends(get_db)):
    return service_crear(data, db)


@router.post("/upsert", response_model=CensoCamasOut)
def upsert_registro(data: CensoCamasCreate, db: Session = Depends(get_db)):
    return service_upsert(data, db)


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def bulk_create(registros: list[CensoCamasCreate], db: Session = Depends(get_db)):
    return service_bulk(registros, db)


@router.post("/importar-csv")
async def importar_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV (.csv)")
    contenido = (await file.read()).decode("utf-8")
    return service_importar_csv(contenido, db)


@router.post("/importar-csv-transversal")
async def importar_csv_transversal(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Importa la hoja de censo en matriz: dos encabezados y una fila por variable."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV (.csv)")
    crudo = await file.read()
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            contenido = crudo.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise HTTPException(
            status_code=400,
            detail="No se pudo decodificar el archivo. Use UTF-8 o Latin-1",
        )
    return service_importar_csv_transversal(contenido, db)


@router.get("/", response_model=CensoCamasListResponse)
def listar_registros(
    fecha: Optional[date] = Query(None, description="Filtrar por fecha exacta"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    servicio_id: Optional[int] = Query(None, description="Filtrar por servicio"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    registros, total = service_listar(
        db=db, fecha=fecha, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        servicio_id=servicio_id, skip=skip, limit=limit,
    )
    return CensoCamasListResponse(total=total, registros=registros)


@router.get("/resumen/{fecha}", response_model=CensoDiarioResumen)
def resumen_diario(fecha: date, db: Session = Depends(get_db)):
    return service_resumen(fecha, db)


@router.get("/hospitalizacion-por-especialidad", response_model=HospitalizacionEspecialidadResponse)
def hospitalizacion_por_especialidad(
    desde: date = Query(..., description="Fecha desde (YYYY-MM-DD)"),
    hasta: date = Query(..., description="Fecha hasta (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    return service_hospitalizacion(desde, hasta, db)


@router.post("/copiar-dia-anterior", response_model=CopiarDiaResponse)
def copiar_dia_anterior(data: CopiarDiaRequest, db: Session = Depends(get_db)):
    return service_copiar_dia(data.origen, data.destino, data.servicio_id, db)


@router.get("/estadisticas", response_model=CensoEstadisticasResponse)
def estadisticas(
    desde: date = Query(..., description="Fecha desde (YYYY-MM-DD)"),
    hasta: date = Query(..., description="Fecha hasta (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    return service_estadisticas(desde, hasta, db)


@router.delete("/eliminar-por-periodo", response_model=CensoCamasEliminarPorPeriodoResponse)
def eliminar_por_periodo(
    data: CensoCamasEliminarPorPeriodoRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return service_eliminar_periodo(data.desde, data.hasta, db)


@router.get("/{registro_id}", response_model=CensoCamasOut)
def obtener_registro(registro_id: int, db: Session = Depends(get_db)):
    return service_obtener(registro_id, db)


@router.put("/{registro_id}", response_model=CensoCamasOut)
def actualizar_registro(registro_id: int, data: CensoCamasUpdate, db: Session = Depends(get_db)):
    return service_actualizar(registro_id, data, db)


@router.delete("/{registro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_registro(registro_id: int, db: Session = Depends(get_db)):
    return service_eliminar(registro_id, db)
