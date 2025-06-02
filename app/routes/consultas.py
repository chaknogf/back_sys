from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc, cast
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from app.database.db import SessionLocal
from app.models.consultas import ConsultaModel
from app.schemas.consultas import ConsultaBase, ConsultaCreate, ConsultaOut, ConsultaUpdate
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/consultas/", response_model=List[ConsultaUpdate], tags=["consultas"])
async def get_consultas(
    id: Optional[int] = Query(None),
    consulta_id: Optional[int] = Query(None),
    especialidad: Optional[int] = Query(None),
    servicio: Optional[int] = Query(None),
    tipo_consulta: Optional[int] = Query(None),
    documento: Optional[str] = Query(None),
    fecha_consulta: Optional[str] = Query(None),
    clico: Optional[str] = Query(None),
    signo: Optional[str] = Query(None),
    antecedente: Optional[str] = Query(None),
    orden: Optional[str] = Query(None),
    estudio: Optional[str] = Query(None),
    detalle_clinico: Optional[str] = Query(None),
    sistema: Optional[str] = Query(None),
    
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        query = db.query(ConsultaModel).order_by(desc(ConsultaModel.id))

        if id:
            query = query.filter(ConsultaModel.id == id)
        if consulta_id:
            query = query.filter(ConsultaModel.consulta_id == consulta_id)
        if especialidad:
            query = query.filter(ConsultaModel.especialidad == especialidad)
        if servicio:
            query = query.filter(ConsultaModel.servicio == servicio)
        if tipo_consulta:
            query = query.filter(ConsultaModel.tipo_consulta == tipo_consulta)
        if documento:
            query = query.filter(ConsultaModel.documento == documento)
        if fecha_consulta:
            query = query.filter(ConsultaModel.fecha_consulta == fecha_consulta)
        if clico:
            query = query.filter(
                cast(ConsultaModel.clico, JSONB).contains([{"clave": clico}])
            )
        if signo:
            query = query.filter(
                cast(ConsultaModel.signos, JSONB).contains([{"clave": signo}])
            )
        if antecedente:
            query = query.filter(
                cast(ConsultaModel.antecedentes, JSONB).contains([{"clave": antecedente}])
            )
        if orden:
            query = query.filter(
                cast(ConsultaModel.ordenes, JSONB).contains([{"clave": orden}])
            )
        if estudio:
            query = query.filter(
                cast(ConsultaModel.estudios, JSONB).contains([{"clave": estudio}])
            )
        if detalle_clinico:
            query = query.filter(
                cast(ConsultaModel.detalle_clinico, JSONB).contains([{"clave": detalle_clinico}])
            )
        if sistema:
            query = query.filter(
                cast(ConsultaModel.sistema, JSONB).contains([{"clave": sistema}])
            )
    
        result = query.offset(skip).limit(limit).all()
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post("/consulta/crear/", status_code=201, tags=["consultas"])
async def create_consulta(
    consulta: ConsultaCreate,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        new_consulta = ConsultaModel(**consulta.model_dump())
        db.add(new_consulta)
        db.commit()
        return JSONResponse(status_code=201, content={"message": "Consulta creada exitosamente", "id": new_consulta.id})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/consulta/actualizar/{consulta_id}", tags=["consultas"])
async def update_consulta(
    consulta_id: int,
    consulta: ConsultaUpdate,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_consulta = db.query(ConsultaModel).filter(ConsultaModel.id == consulta_id).first()
        if not db_consulta:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")

        update_data = consulta.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_consulta, key, value)

        db.commit()
        return JSONResponse(status_code=200, content={"message": "Consulta actualizada exitosamente"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/consulta/eliminar/{consulta_id}", tags=["consultas"])
async def delete_consulta(
    consulta_id: int,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_consulta = db.query(ConsultaModel).filter(ConsultaModel.id == consulta_id).first()
        if not db_consulta:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")

        db.delete(db_consulta)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Consulta eliminado exitosamente"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
