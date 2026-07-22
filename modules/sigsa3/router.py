from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field
import io

from core.dependencies import get_db, get_current_user, get_current_admin_user
from modules.users.models import UserModel
from .schemas import Sigsa3Create, Sigsa3Update, Sigsa3Out
from .service import (
    listar_registros as service_listar,
    obtener_registro as service_obtener,
    crear_registro as service_crear,
    actualizar_registro as service_actualizar,
    eliminar_registro as service_eliminar,
    eliminar_por_ids,
    eliminar_por_periodo,
    asociar_medico,
    asociar_paciente_y_consulta,
    importar_excel_csv,
    asociar_paciente,
    listar_no_asociados,
    actualizar_especialidad_por_medico,
    listar_personal_salud,
    crear_personal_salud,
    actualizar_personal_salud,
    eliminar_personal_salud,
    sincronizar_especialidad,
    dx_z34,
    dx_z10,
    truncate_tabla,
    exportar_csv,
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


@router.post("/importar-excel", tags=["SIGSA-3"])
async def importar_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Importa CSV exportado desde Excel con formato SIGSA-3 (columnas con X para tipo_consulta)."""
    return await importar_excel_csv(file, db)


class AsociarPacienteRequest(BaseModel):
    expediente: str = Field(..., max_length=30, description="Expediente del paciente")
    no_historia_clinica: str = Field(..., max_length=30, description="No. historia clínica SIGSA-3")


@router.post("/asociar-paciente", tags=["SIGSA-3"])
def asociar(
    data: AsociarPacienteRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Asocia registros SIGSA-3 con un paciente por expediente y no_historia_clinica."""
    return asociar_paciente(data.expediente, data.no_historia_clinica, db)


@router.get("/no-asociados/", response_model=List[Sigsa3Out], tags=["SIGSA-3"])
def no_asociados(
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lista registros SIGSA-3 que no están asociados a ningún paciente."""
    return listar_no_asociados(db, limit)


class ActualizarEspecialidadRequest(BaseModel):
    personal_salud: str = Field(..., max_length=100, description="Nombre del personal de salud")


@router.post("/actualizar-especialidad", tags=["SIGSA-3"])
def actualizar_especialidad(
    data: ActualizarEspecialidadRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Actualiza especialidad en registros SIGSA-3 usando personal_salud como referencia."""
    return actualizar_especialidad_por_medico(data.personal_salud, db)


@router.get("/dx/z34", tags=["SIGSA-3"])
def diag_z34(
    desde: date = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: date = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Diagnósticos con código CIE-10 Z:34 clasificados por tipo de consulta."""
    return dx_z34(db, desde.isoformat(), hasta.isoformat())


@router.get("/dx/z10", tags=["SIGSA-3"])
def diag_z10(
    desde: date = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: date = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Diagnósticos con código CIE-10 Z:10:4, Z:10:5, Z:10:6 clasificados por tipo de consulta."""
    return dx_z10(db, desde.isoformat(), hasta.isoformat())


# PERSONAL_SALUD CRUD
# ────────────────────────────────


class PersonalSaludCreate(BaseModel):
    nombre: str = Field(..., max_length=200)
    especialidad: str | None = Field(None, max_length=100)
    medico_id: int | None = None


class PersonalSaludUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=200)
    especialidad: str | None = Field(None, max_length=100)
    medico_id: int | None = None


class PersonalSaludOut(BaseModel):
    id: int
    nombre: str
    especialidad: str | None
    medico_id: int | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


@router.get("/personal-salud", response_model=List[PersonalSaludOut], tags=["SIGSA-3", "Personal Salud"])
def listar_personal_salud_endpoint(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lista el catálogo de personal de salud."""
    from modules.sigsa3.models import PersonalSaludModel
    return db.query(PersonalSaludModel).order_by(PersonalSaludModel.nombre).all()


@router.post("/personal-salud", response_model=PersonalSaludOut, status_code=201, tags=["SIGSA-3", "Personal Salud"])
def crear_personal_salud_endpoint(
    data: PersonalSaludCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Agrega una persona al catálogo personal_salud."""
    return crear_personal_salud(data.nombre, data.especialidad, data.medico_id, db)


@router.put("/personal-salud/{ps_id}", response_model=PersonalSaludOut, tags=["SIGSA-3", "Personal Salud"])
def actualizar_personal_salud_endpoint(
    ps_id: int,
    data: PersonalSaludUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Actualiza un registro en personal_salud."""
    return actualizar_personal_salud(ps_id, data.nombre, data.especialidad, data.medico_id, db)


@router.delete("/personal-salud/{ps_id}", tags=["SIGSA-3", "Personal Salud"])
def eliminar_personal_salud_endpoint(
    ps_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Elimina un registro de personal_salud."""
    return eliminar_personal_salud(ps_id, db)


@router.post("/truncate", tags=["SIGSA-3"])
def truncar_tabla(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    """TRUNCATE la tabla sigsa3 (solo admin). Elimina todos los registros permanentemente."""
    return truncate_tabla(db)


@router.get("/exportar-csv", tags=["SIGSA-3"])
def exportar_csv_endpoint(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Exporta todos los registros SIGSA-3 como archivo CSV."""
    csv_content = exportar_csv(db)
    if not csv_content:
        return StreamingResponse(io.StringIO(""), media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=sigsa3.csv",
        })
    return StreamingResponse(io.StringIO(csv_content), media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=sigsa3.csv",
    })


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


class EliminarPorIdsRequest(BaseModel):
    ids: List[int] = Field(..., description="Lista de IDs a eliminar")


@router.post("/eliminar-por-ids", tags=["SIGSA-3"])
def eliminar_ids(
    data: EliminarPorIdsRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Elimina múltiples registros SIGSA-3 por lista de IDs."""
    return eliminar_por_ids(data.ids, db)


class EliminarPorPeriodoRequest(BaseModel):
    desde: date = Field(..., description="Fecha inicio (YYYY-MM-DD)")
    hasta: date = Field(..., description="Fecha fin (YYYY-MM-DD)")


@router.post("/eliminar-por-periodo", tags=["SIGSA-3"])
def eliminar_periodo(
    data: EliminarPorPeriodoRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Elimina registros SIGSA-3 en un rango de fechas."""
    return eliminar_por_periodo(data.desde, data.hasta, db)


@router.post("/asociar-medico", tags=["SIGSA-3"])
def asociar_medico_endpoint(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Asocia medico_id usando personal_salud con medicos.nombre."""
    return asociar_medico(db)


@router.post("/asociar-todo", tags=["SIGSA-3"])
def asociar_todo_endpoint(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Pipeline completo: paciente_id (nombre+expediente, nombre contiene, expediente) y consulta_id (paciente+fecha+tipo, documento+fecha).
    Retorna JSON con el resultado final."""
    try:
        gen = asociar_paciente_y_consulta(db)
        for evento in gen:
            if evento.get("step") == "done":
                return evento
            if evento.get("step") == "error":
                return {"error": evento.get("message", "Error en el pipeline")}
        return {"error": "no se ejecutó el pipeline"}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}


@router.post("/asociar-todo-stream", tags=["SIGSA-3"])
def asociar_todo_stream_endpoint(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Igual que asociar-todo pero retorna eventos SSE con progreso en tiempo real."""
    from fastapi.responses import StreamingResponse
    import json

    def _eventos():
        for evento in asociar_paciente_y_consulta(db):
            yield f"data: {json.dumps(evento, default=str)}\n\n"

    return StreamingResponse(_eventos(), media_type="text/event-stream")


@router.post("/sincronizar-especialidad", tags=["SIGSA-3"])
def sincronizar_especialidad_endpoint(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Sincroniza especialidad desde personal_salud → medicos y sigsa3."""
    return sincronizar_especialidad(db)
