from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc, cast
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from app.database.db import SessionLocal
from app.models.eventos import EventoConsultaModel
from app.schemas.eventos import EventoConsultaCreate, EventoConsultaBase, EventoConsultaOut
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/eventos/", response_model=List[EventoConsultaBase], tags=["Eventos"])
async def get_eventos(
    id: Optional[int] = Query(None),
    consulta_id: Optional[int] = Query(None),
    tipo_evento: Optional[int] = Query(None),
    datos_clave: Optional[str] = Query(None),
    datos_valor: Optional[str] = Query(None),
    responsable_clave: Optional[str] = Query(None),
    responsable_valor: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        query = db.query(EventoConsultaModel).order_by(desc(EventoConsultaModel.id))

        if id:
            query = query.filter(EventoConsultaModel.id == id)
        if consulta_id:
            query = query.filter(EventoConsultaModel.consulta_id == consulta_id)
        if tipo_evento:
            query = query.filter(EventoConsultaModel.tipo_evento == tipo_evento)
        if datos_clave and datos_valor:
            query = query.filter(EventoConsultaModel.datos[datos_clave].astext == datos_valor)
        if responsable_clave and responsable_valor:
            query = query.filter(EventoConsultaModel.responsable[responsable_clave].astext == responsable_valor)
        if estado:
            query = query.filter(EventoConsultaModel.estado == estado)

        result = query.offset(skip).limit(limit).all()
        return result

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post("/evento/crear/", status_code=201, tags=["Eventos"])
async def create_evento(
    evento: EventoConsultaCreate,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        new_consulta = EventoConsultaModel(**evento.model_dump())
        db.add(new_consulta)
        db.commit()
        return JSONResponse(status_code=201, content={"message": "evento creada exitosamente", "id": new_consulta.id})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/evento/actualizar/{consulta_id}", tags=["Eventos"])
async def update_evento(
    consulta_id: int,
    evento: EventoConsultaBase,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_consulta = db.query(EventoConsultaModel).filter(EventoConsultaModel.id == consulta_id).first()
        if not db_consulta:
            raise HTTPException(status_code=404, detail="evento no encontrada")

        update_data = evento.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_consulta, key, value)

        db.commit()
        return JSONResponse(status_code=200, content={"message": "evento actualizada exitosamente"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/evento/eliminar/{consulta_id}", tags=["Eventos"])
async def delete_evento(
    consulta_id: int,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_consulta = db.query(EventoConsultaModel).filter(EventoConsultaModel.id == consulta_id).first()
        if not db_consulta:
            raise HTTPException(status_code=404, detail="evento no encontrada")

        db.delete(db_consulta)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "evento eliminado exitosamente"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
