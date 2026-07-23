from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field
import io
import json

from core.dependencies import get_db, get_current_user, get_current_admin_user
from modules.users.models import UserModel
from .schemas import Sigsa3Out
from .service import (
    eliminar_por_periodo,
    sincronizar_sigsa3,
    asociar_paciente_y_consulta,
    importar_excel_csv,
    asociar_paciente,
    listar_no_asociados,
    exportar_csv,
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
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
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


@router.post("/asociar-pacientes-masivo-stream")
def asociar_pacientes_masivo_stream(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    def _eventos():
        for evento in asociar_paciente_y_consulta(db):
            yield f"data: {json.dumps(evento, default=str)}\n\n"

    return StreamingResponse(_eventos(), media_type="text/event-stream")
