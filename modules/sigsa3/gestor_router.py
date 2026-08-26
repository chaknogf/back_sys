from fastapi import APIRouter, Depends, status, Query, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field
import io
import json

from core.dependencies import get_db, get_current_user, get_current_admin_user
from modules.users.models import UserModel
from .schemas import (
    Sigsa3Out, Sigsa3RegistroOut, PendienteDetalle,
    ResolverPendienteRequest, ResolverPendienteResponse,
    ClusterDuplicado, MergeDuplicadosRequest, MergeDuplicadosResponse,
)
from .service import (
    eliminar_por_periodo,
    sincronizar_sigsa3,
    asociar_paciente_y_consulta,
    importar_excel_csv,
    asociar_paciente,
    listar_no_asociados,
    listar_pendientes_detalle,
    resolver_pendiente,
    detectar_duplicados,
    merge_duplicados_sigsa3,
    crear_indices_sigsa3,
    exportar_csv,
    normalizar as service_normalizar,
)

router = APIRouter(
    prefix="/sigsa3",
    tags=["Gestor SIGSA-3"],
)


class AsociarPacienteRequest(BaseModel):
    expediente: str = Field(..., max_length=30, description="Expediente del paciente")
    no_historia_clinica: str = Field(..., max_length=30, description="No. historia clínica SIGSA-3")


class EliminarPorPeriodoRequest(BaseModel):
    desde: date = Field(..., description="Fecha inicio (YYYY-MM-DD)")
    hasta: date = Field(..., description="Fecha fin (YYYY-MM-DD)")


@router.post("/importar-excel")
async def importar_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return await importar_excel_csv(file, db)


@router.post("/asociar-paciente")
def asociar(
    data: AsociarPacienteRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return asociar_paciente(data.expediente, data.no_historia_clinica, db)


@router.get("/no-asociados/", response_model=List[Sigsa3Out])
def no_asociados(
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return listar_no_asociados(db, limit)


@router.get("/pendientes-detalle", response_model=List[PendienteDetalle])
def pendientes_detalle(
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Registros SIGSA-3 sin paciente_id, con top 5 candidatos y scores para revisión humana."""
    return listar_pendientes_detalle(db, limit)


@router.post("/resolver-pendiente", response_model=ResolverPendienteResponse)
def resolver(
    data: ResolverPendienteRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Asocia manualmente un paciente a un registro SIGSA-3 pendiente."""
    return resolver_pendiente(db, data.sigsa3_id, data.paciente_id)


@router.get("/duplicados", response_model=List[ClusterDuplicado])
def duplicados(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Detecta clusters de pacientes con el mismo nombre (duplicados potenciales).
    Retorna clusters ordenados por impacto (más registros SIGSA-3 pendientes primero)."""
    return detectar_duplicados(db)


@router.post("/merge-duplicados", response_model=MergeDuplicadosResponse)
def merge_duplicados(
    data: MergeDuplicadosRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Fusiona pacientes duplicados, reasignando consultas, SIGSA-3, citas,
    defunciones y nacimientos al paciente principal. Los duplicados se desactivan."""
    return merge_duplicados_sigsa3(
        db, data.principal_id, data.duplicado_ids, data.reasignar_sigsa3
    )


@router.post("/crear-indices")
def crear_indices(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    """Crea índices de BD recomendados para acelerar el pipeline. Ejecutar una sola vez."""
    return crear_indices_sigsa3(db)


@router.get("/cache-stats")
def cache_stats():
    """Estadísticas del cache vectorial de nombres."""
    from modules.common.vector_cache import get_vector_cache
    return get_vector_cache().stats()


@router.get("/exportar-csv")
def exportar_csv_endpoint(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    csv_content = exportar_csv(db)
    if not csv_content:
        return StreamingResponse(io.BytesIO(), media_type="text/csv; charset=utf-8", headers={
            "Content-Disposition": "attachment; filename=sigsa3.csv",
        })
    return StreamingResponse(io.BytesIO(csv_content), media_type="text/csv; charset=utf-8", headers={
        "Content-Disposition": "attachment; filename=sigsa3.csv",
    })


@router.post("/eliminar-por-periodo")
def eliminar_periodo(
    data: EliminarPorPeriodoRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return eliminar_por_periodo(data.desde, data.hasta, db)


@router.post("/sincronizar-medico-especialidad")
def sincronizar_medico_especialidad(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Paso 1: asocia medico_id en SIGSA-3 por nombre (personal_salud → personal_salud.medico_id).
    Paso 2: actualiza especialidad en SIGSA-3 desde medicos.especialidad según medico_id."""
    return sincronizar_sigsa3(db)


@router.post("/asociar-pacientes-masivo")
def asociar_pacientes_masivo(
    umbral_submatch: float = Query(None, ge=0.5, le=1.0, description="Mínimo score nombre para auto-asociar (default 0.82)"),
    zona_match: float = Query(None, ge=0.5, le=1.0, description="Score >= este valor → match automático (default 0.85)"),
    zona_revision: float = Query(None, ge=0.5, le=1.0, description="Score >= este valor → zona gris (default 0.70)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        gen = asociar_paciente_y_consulta(db, umbral_submatch=umbral_submatch,
                                          zona_match=zona_match, zona_revision=zona_revision)
        for evento in gen:
            if evento.get("step") == "done":
                return evento
            if evento.get("step") == "error":
                return {"error": evento.get("message", "Error en el pipeline")}
        return {"error": "no se ejecutó el pipeline"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al ejecutar la asociación masiva SIGSA-3",
        )


@router.post("/asociar-pacientes-masivo-stream")
def asociar_pacientes_masivo_stream(
    umbral_submatch: float = Query(None, ge=0.5, le=1.0, description="Mínimo score nombre para auto-asociar (default 0.82)"),
    zona_match: float = Query(None, ge=0.5, le=1.0, description="Score >= este valor → match automático (default 0.85)"),
    zona_revision: float = Query(None, ge=0.5, le=1.0, description="Score >= este valor → zona gris (default 0.70)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    def _eventos():
        for evento in asociar_paciente_y_consulta(db, umbral_submatch=umbral_submatch,
                                                   zona_match=zona_match, zona_revision=zona_revision):
            yield f"data: {json.dumps(evento, default=str)}\n\n"

    return StreamingResponse(_eventos(), media_type="text/event-stream")


@router.post("/normalizar")
def normalizar_sigsa3(
    dry_run: bool = Query(False, description="Solo simular: cuenta y reporta sin migrar ni borrar"),
    ids: str = Query(None, description="IDs de staging a migrar (CSV: '1,2,3'). Por defecto migra todos los elegibles"),
    max_registros: Optional[int] = Query(None, description="Tope máximo de registros a migrar en esta corrida"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Migra registros SIGSA-3 con paciente+medico a sigsa3_registros (normalizado).
    Copia sigsa3_id en el normalizado; al final purga de staging los id migrados.
    Resuelve CIE-10, especialidad y tipo_consulta a FKs del catálogo.
    Reporta los personal_salud que no encontraron coincidencia.

    ⚠️ No lanzar dos veces en paralelo: la corrida masiva no tiene bloqueo."""
    lista_ids = None
    if ids:
        try:
            lista_ids = [int(x.strip()) for x in ids.split(",") if x.strip()]
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="ids debe ser una lista separada por comas de enteros",
            )
    resultado = service_normalizar(db, dry_run=dry_run, ids=lista_ids, max_registros=max_registros)
    return resultado


class SincronizarTodoRequest(BaseModel):
    dry_run: bool = False
    ejecutar_asociacion: bool = True


@router.post("/sincronizar-todo")
def sincronizar_todo(
    data: SincronizarTodoRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Orquesta el flujo completo de sincronización:

    1. sincronizar-medico-especialidad: asocia medico_id por personal_salud.nombre
       y copia especialidad_id desde personal_salud (tabla puente depurada).
    2. asociar-pacientes-masivo: pipeline que llena paciente_id y consulta_id.
    3. normalizar: migra a sigsa3_registros (con sigsa3_id) y purga staging.

    Con dry_run=True no se escribe ni borra nada; reporta lo que pasaría."""
    paso1 = sincronizar_sigsa3(db, dry_run=data.dry_run)
    if data.dry_run:
        resultado_normalizacion = service_normalizar(db, dry_run=True)
        return {
            "sincronizar_medico_especialidad": paso1,
            "asociar_pacientes": "omitido (dry_run)",
            "normalizar": resultado_normalizacion,
        }

    paso2 = None
    if data.ejecutar_asociacion:
        for evento in asociar_paciente_y_consulta(db):
            if evento.get("step") == "done":
                paso2 = evento
                break
            if evento.get("step") == "error":
                paso2 = {"error": evento.get("message", "Error en el pipeline")}
                break
    resultado_normalizacion = service_normalizar(db)
    return {
        "sincronizar_medico_especialidad": paso1,
        "asociar_pacientes": paso2,
        "normalizar": resultado_normalizacion,
    }
