"""Rutas autenticadas de intervenciones y catálogos quirúrgicos; cambios de catálogo son administrativos."""

from fastapi import APIRouter, Depends, Query, status, UploadFile, File, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, time

from core.dependencies import get_db, get_current_admin_user, get_current_user
from core.uploads import read_upload_limited
from modules.users.models import UserModel

from . import schemas as sch
from . import service as svc
from . import reportes_service as rsvc
from . import reportes_excel as rxl

# Tags por recurso: al ser tags distintos, Swagger los agrupa y los ordena
# según el orden de definición de las rutas de este router.
TAG_INTERVENCIONES = "Quirófano · Intervenciones"
TAG_PROCEDIMIENTOS = "Quirófano · Procedimientos"
TAG_ESTADOS = "Quirófano · Estados de Cirugía"
TAG_FORMATOS = "Quirófano · Formatos"
TAG_PROCEDENCIAS = "Quirófano · Procedencias"
TAG_RANGOS = "Quirófano · Rangos de Especialista"
TAG_QUIROFANOS = "Quirófano · Números de Quirófano"
TAG_REPORTES = "Quirófano · Reportes"

# Convención canónica: rutas de colección sin slash final.
router = APIRouter(prefix="/quirofano")


# ========================
# Intervención Quirúrgica
# ========================
@router.get("/intervenciones", response_model=sch.IntervencionQuirurgicaListResponse, tags=[TAG_INTERVENCIONES])
def listar_intervenciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    expediente: Optional[str] = Query(None),
    consulta_id: Optional[int] = Query(None, description="Filtrar por consulta de hospitalización"),
    consulta_ids: Optional[str] = Query(None, description="IDs de consulta separados por coma"),
    fecha_desde: Optional[date] = Query(None, alias="fecha_desde"),
    fecha_hasta: Optional[date] = Query(None, alias="fecha_hasta"),
    activos: Optional[bool] = Query(True),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_intervenciones(
        db,
        skip=skip,
        limit=limit,
        expediente=expediente,
        consulta_id=consulta_id,
        consulta_ids=consulta_ids,
        fecha_desde=fecha_desde.isoformat() if fecha_desde else None,
        fecha_hasta=fecha_hasta.isoformat() if fecha_hasta else None,
        activo=activos,
        q=q,
    )


@router.get("/intervenciones/{intervencion_id}", response_model=sch.IntervencionQuirurgicaOut, tags=[TAG_INTERVENCIONES])
def obtener_intervencion(
    intervencion_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.obtener_intervencion(intervencion_id, db)


@router.post("/intervenciones", response_model=sch.IntervencionQuirurgicaOut, status_code=status.HTTP_201_CREATED, tags=[TAG_INTERVENCIONES])
def crear_intervencion(
    data: sch.IntervencionQuirurgicaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.crear_intervencion(data, db, created_by=current_user.username)


@router.put("/intervenciones/{intervencion_id}", response_model=sch.IntervencionQuirurgicaOut, tags=[TAG_INTERVENCIONES])
def actualizar_intervencion(
    intervencion_id: int,
    data: sch.IntervencionQuirurgicaUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.actualizar_intervencion(intervencion_id, data, db, created_by=current_user.username)


@router.delete("/intervenciones/{intervencion_id}", tags=[TAG_INTERVENCIONES])
def eliminar_intervencion(
    intervencion_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.eliminar_intervencion(intervencion_id, db)


# ========================
# Procedimiento Quirófano
# ========================
@router.get("/procedimientos-quirofano", response_model=List[sch.ProcedimientoQuirofanoOut], tags=[TAG_PROCEDIMIENTOS])
def listar_procedimientos_quirofano(
    activos: bool = Query(True, description="Solo activos"),
    especialidad_id: Optional[int] = Query(None, description="Filtrar por especialidad"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    incluir_mixtos: bool = Query(
        False,
        description="Incluir procedimientos de 'Todas (mixta)' al filtrar por especialidad",
    ),
    q: Optional[str] = Query(None, description="Buscar por nombre o código"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_procedimientos_quirofano(
        db,
        solo_activos=activos,
        especialidad_id=especialidad_id,
        incluir_mixtos=incluir_mixtos,
        q=q,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/procedimientos-quirofano",
    response_model=sch.ProcedimientoQuirofanoOut,
    status_code=status.HTTP_201_CREATED,
    tags=[TAG_PROCEDIMIENTOS],
)
def crear_procedimiento_quirofano(
    data: sch.ProcedimientoQuirofanoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_procedimiento_quirofano(data, db)


@router.put("/procedimientos-quirofano/{proc_id}", response_model=sch.ProcedimientoQuirofanoOut, tags=[TAG_PROCEDIMIENTOS])
def actualizar_procedimiento_quirofano(
    proc_id: int,
    data: sch.ProcedimientoQuirofanoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_procedimiento_quirofano(proc_id, data, db)


@router.delete("/procedimientos-quirofano/truncar", tags=[TAG_PROCEDIMIENTOS])
def truncar_procedimientos(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.truncar_procedimientos(db)


@router.post("/procedimientos-quirofano/importar-csv", tags=[TAG_PROCEDIMIENTOS])
async def importar_csv_procedimientos(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    """Importa CSV solo para administradores, con UTF-8 y fallback de decodificación cp1252."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV (.csv)")
    raw = await read_upload_limited(file, max_bytes=25 * 1024 * 1024)
    try:
        contenido = raw.decode("utf-8")
    except UnicodeDecodeError:
        contenido = raw.decode("cp1252", errors="replace")
    return svc.importar_csv_procedimientos(contenido, db)


@router.delete("/procedimientos-quirofano/{proc_id}", tags=[TAG_PROCEDIMIENTOS])
def eliminar_procedimiento_quirofano(
    proc_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_procedimiento_quirofano(proc_id, db)


# ========================
# Estado Cirugía
# ========================
@router.get("/estados-cirugia", response_model=List[sch.EstadoCirugiaOut], tags=[TAG_ESTADOS])
def listar_estados_cirugia(
    activos: bool = Query(True, description="Solo activos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_estados_cirugia(db, solo_activos=activos, skip=skip, limit=limit)


@router.post("/estados-cirugia", response_model=sch.EstadoCirugiaOut, status_code=status.HTTP_201_CREATED, tags=[TAG_ESTADOS])
def crear_estado_cirugia(
    data: sch.EstadoCirugiaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_estado_cirugia(data, db)


@router.put("/estados-cirugia/{estado_id}", response_model=sch.EstadoCirugiaOut, tags=[TAG_ESTADOS])
def actualizar_estado_cirugia(
    estado_id: int,
    data: sch.EstadoCirugiaUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_estado_cirugia(estado_id, data, db)


@router.delete("/estados-cirugia/{estado_id}", tags=[TAG_ESTADOS])
def eliminar_estado_cirugia(
    estado_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_estado_cirugia(estado_id, db)


# ========================
# Formato Procedimiento
# ========================
@router.get("/formatos", response_model=List[sch.FormatoProcedimientoOut], tags=[TAG_FORMATOS])
def listar_formatos(
    activos: bool = Query(True, description="Solo activos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_formatos(db, solo_activos=activos, skip=skip, limit=limit)


@router.post("/formatos", response_model=sch.FormatoProcedimientoOut, status_code=status.HTTP_201_CREATED, tags=[TAG_FORMATOS])
def crear_formato(
    data: sch.FormatoProcedimientoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_formato(data, db)


@router.put("/formatos/{formato_id}", response_model=sch.FormatoProcedimientoOut, tags=[TAG_FORMATOS])
def actualizar_formato(
    formato_id: int,
    data: sch.FormatoProcedimientoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_formato(formato_id, data, db)


@router.delete("/formatos/{formato_id}", tags=[TAG_FORMATOS])
def eliminar_formato(
    formato_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_formato(formato_id, db)


# ========================
# Procedencia Procedimiento
# ========================
@router.get("/procedencias", response_model=List[sch.ProcedenciaProcedimientoOut], tags=[TAG_PROCEDENCIAS])
def listar_procedencias(
    activos: bool = Query(True, description="Solo activos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_procedencias(db, solo_activos=activos, skip=skip, limit=limit)


@router.post("/procedencias", response_model=sch.ProcedenciaProcedimientoOut, status_code=status.HTTP_201_CREATED, tags=[TAG_PROCEDENCIAS])
def crear_procedencia(
    data: sch.ProcedenciaProcedimientoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_procedencia(data, db)


@router.put("/procedencias/{procedencia_id}", response_model=sch.ProcedenciaProcedimientoOut, tags=[TAG_PROCEDENCIAS])
def actualizar_procedencia(
    procedencia_id: int,
    data: sch.ProcedenciaProcedimientoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_procedencia(procedencia_id, data, db)


@router.delete("/procedencias/{procedencia_id}", tags=[TAG_PROCEDENCIAS])
def eliminar_procedencia(
    procedencia_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_procedencia(procedencia_id, db)


# ========================
# Rango Especialista
# ========================
@router.get("/rangos-especialista", response_model=List[sch.RangoEspecialistaOut], tags=[TAG_RANGOS])
def listar_rangos_especialista(
    activos: bool = Query(True, description="Solo activos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_rangos_especialista(db, solo_activos=activos, skip=skip, limit=limit)


@router.post("/rangos-especialista", response_model=sch.RangoEspecialistaOut, status_code=status.HTTP_201_CREATED, tags=[TAG_RANGOS])
def crear_rango_especialista(
    data: sch.RangoEspecialistaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_rango_especialista(data, db)


@router.put("/rangos-especialista/{rango_id}", response_model=sch.RangoEspecialistaOut, tags=[TAG_RANGOS])
def actualizar_rango_especialista(
    rango_id: int,
    data: sch.RangoEspecialistaUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_rango_especialista(rango_id, data, db)


@router.delete("/rangos-especialista/{rango_id}", tags=[TAG_RANGOS])
def eliminar_rango_especialista(
    rango_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_rango_especialista(rango_id, db)


# ========================
# Número de Quirófano
# ========================
@router.get("/quirofanos-numero", response_model=List[sch.QuirofanoNumeroOut], tags=[TAG_QUIROFANOS])
def listar_quirofanos_numero(
    activos: bool = Query(True, description="Solo activos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_quirofanos_numero(db, solo_activos=activos, skip=skip, limit=limit)


@router.post("/quirofanos-numero", response_model=sch.QuirofanoNumeroOut, status_code=status.HTTP_201_CREATED, tags=[TAG_QUIROFANOS])
def crear_quirofano_numero(
    data: sch.QuirofanoNumeroCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_quirofano_numero(data, db)


@router.put("/quirofanos-numero/{qn_id}", response_model=sch.QuirofanoNumeroOut, tags=[TAG_QUIROFANOS])
def actualizar_quirofano_numero(
    qn_id: int,
    data: sch.QuirofanoNumeroUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_quirofano_numero(qn_id, data, db)


@router.delete("/quirofanos-numero/{qn_id}", tags=[TAG_QUIROFANOS])
def eliminar_quirofano_numero(
    qn_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_quirofano_numero(qn_id, db)


# ========================
# Configuración de jornada por quirófano
# ========================
@router.get("/config-periodo", response_model=List[sch.QuirofanoConfigPeriodoOut], tags=[TAG_REPORTES])
def listar_config_periodo(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return rsvc.listar_config_periodo(db, skip=skip, limit=limit)


@router.put("/config-periodo/{quirofano_numero_id}", response_model=sch.QuirofanoConfigPeriodoOut, tags=[TAG_REPORTES])
def actualizar_config_periodo(
    quirofano_numero_id: int,
    data: sch.QuirofanoConfigPeriodoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return rsvc.actualizar_config_periodo(db, quirofano_numero_id, data)


# ========================
# Reportes (resumen + Excel)
# ========================
def _params_reporte(
    fecha_desde: date,
    fecha_hasta: date,
    especialidad_id: Optional[int] = Query(None, description="Filtrar por especialidad"),
    quirofano_numero_id: Optional[int] = Query(None, description="Filtrar por quirófano"),
    hora_apertura: Optional[time] = Query(None, description="Hora de apertura (HH:MM)"),
    hora_cierre: Optional[time] = Query(None, description="Hora de cierre (HH:MM)"),
    dias_abiertos: Optional[int] = Query(None, ge=0, description="Días abiertos del período"),
) -> dict:
    return {
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "especialidad_id": especialidad_id,
        "quirofano_numero_id": quirofano_numero_id,
        "hora_apertura": hora_apertura,
        "hora_cierre": hora_cierre,
        "dias_abiertos": dias_abiertos,
    }


@router.get("/reportes/resumen", response_model=sch.ResumenReporteResponse, tags=[TAG_REPORTES])
def reporte_resumen(
    params: dict = Depends(_params_reporte),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return rsvc.generar_reporte(db, **params)


@router.get("/reportes/excel", tags=[TAG_REPORTES])
def reporte_excel(
    params: dict = Depends(_params_reporte),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    reporte = rsvc.generar_reporte(db, **params)
    contenido = rxl.construir_excel_bytes(reporte)
    nombre = f"Control_Quirofanos_{params['fecha_desde']}_{params['fecha_hasta']}.xlsx"
    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )
