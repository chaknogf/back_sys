from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc, cast, func
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from app.database.db import SessionLocal
from app.models.consultas import ConsultaModel, VistaConsultasModel
from app.schemas.vista_consulta import VistaConsultas
from app.schemas.consultas import ConsultaBase, ConsultaCreate, ConsultaOut, ConsultaUpdate
from fastapi.security import OAuth2PasswordBearer
from app.utils.expediente import generar_expediente, generar_emergencia

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        


@router.post("/generar/emergencia") #si tipo_consulta fuera 3 
def nuevo_expediente( db: SQLAlchemySession = Depends(get_db)):
    hoja = generar_emergencia(db)
    return {"correlativo": hoja}


@router.post("/consulta/crear/", response_model=ConsultaUpdate,status_code=201, tags=["consultas"])
def create_consulta(
    consulta: ConsultaCreate,
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        with db.begin():
            # Buscar el último orden en ese grupo
            max_orden = db.query(func.max(ConsultaModel.orden)).filter(
                ConsultaModel.tipo_consulta == consulta.tipo_consulta,
                ConsultaModel.especialidad == consulta.especialidad,
                ConsultaModel.fecha_consulta == consulta.fecha_consulta
            ).scalar()

            # Si no existe aún ningún registro en ese grupo, empezamos en 1
            nuevo_orden = (max_orden or 0) + 1

            # Crear el objeto con el orden calculado
            consulta_dict = consulta.model_dump()
            consulta_dict["orden"] = nuevo_orden

            new_consulta = ConsultaModel(**consulta_dict)
            db.add(new_consulta)
            db.flush()  # forzar insert en la transacción

        db.refresh(new_consulta)

        return JSONResponse(
            status_code=201,
            content={
                "message": "Consulta creada exitosamente",
                "id": new_consulta.id,
                "orden": new_consulta.orden
            }
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))