from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from database.database import SessionLocal, get_db
from models.consultas_models import Expediente, Consulta
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import desc


# Crear el router de FastAPI
router = APIRouter()

# Modelo de Pydantic para Expediente
class ExpedienteModel(BaseModel):
    id: Optional[int] = None
    paciente_id: Optional[int] = None
    expediente: Optional[str] = None
    hoja_emergencia: Optional[str] = None
    referencia_anterior: Optional[str] = None
    expediente_madre: Optional[str] = None
    created_at: Optional[str] = None

# Modelo de Pydantic para Consultas
class ConsultasModel(BaseModel):
    id: Optional[int] = None
    exp_id: Optional[int] = None
    paciente_id: Optional[int] = None
    historia_clinica: Optional[str] = None
    fecha_consulta: Optional[str] = None
    hora: Optional[str] = None
    fecha_recepcion: Optional[str] = None
    fecha_egreso: Optional[str] = None
    tipo_consulta: Optional[int] = None
    tipo_lesion: Optional[int] = None
    estancia: Optional[int] = None
    especialidad: Optional[int] = None
    servicio: Optional[int] = None
    fallecido: Optional[str] = None
    referido: Optional[str] = None
    contraindicado: Optional[str] = None
    diagnostico: Optional[str] = None
    folios: Optional[int] = None
    medico: Optional[int] = None
    nota: Optional[str] = None
    estatus: Optional[int] = None
    lactancia: Optional[str] = None
    prenatal: Optional[int] = None
    create_user: Optional[str] = None
    update_user: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    grupo_edad: Optional[str] = None
    
class VistaConsultas(BaseModel):
    id: Optional[int] = None
    exp_id: Optional[int] = None
    paciente_id: Optional[int] = None
    historia_clinica: Optional[str] = None
    fecha_consulta: Optional[str] = None
    hora: Optional[str] = None
    fecha_recepcion: Optional[str] = None
    fecha_egreso: Optional[str] = None
    tipo_consulta: Optional[int] = None
    estatus: Optional[int] = None




# Ruta para obtener expedientes
@router.get("/expedientes", tags=["Consultas"])
def get_exp(db: Session = Depends(get_db)):
    try:
        result = (
            db.query(Expediente)
            .order_by(desc(Expediente.id))
            .limit(300)
            .all()
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    except SQLAlchemyError as error:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {error}")
    
@router.get("/consultasALL", tags=["Consultas"])
def get_exp(db: Session = Depends(get_db)):
    try:
        result = (
            db.query(ConsultasModel)
            .order_by(desc(ConsultasModel.id))
            .limit(300)
            .all()
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    except SQLAlchemyError as error:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {error}")

@router.get("/consultasID", tags=["Consultas"])
def get_consultas_id(id: int, db: Session = Depends(get_db)):
    try:
        # Ejecuta la consulta y convierte los resultados a una lista
        result = (
            db.query(Consulta)
            .filter(Consulta.paciente_id == id)
            .all()  # Materializa los resultados
        )
        
        if not result:
            raise HTTPException(
                status_code=404, detail=f"No se encontraron consultas para el paciente con ID {id}"
            )
        
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    except SQLAlchemyError as error:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {error}")
    
@router.get("/consultarapida", tags=["Consultas"])
def get_consultas_id(paciente_id: int, db: Session = Depends(get_db)):
    try:
        # Ejecuta la consulta y convierte los resultados a una lista
        result = (
            db.query(VistaConsultas)
            .filter(VistaConsultas.paciente_id == paciente_id)
            .all()  # Materializa los resultados
        )
        
        if not result:
            raise HTTPException(
                status_code=404, detail=f"No se encontraron consultas para el paciente con ID {id}"
            )
        
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    except SQLAlchemyError as error:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {error}")
    
