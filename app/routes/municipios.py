from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text
from typing import Optional, List
from app.database.db import SessionLocal
from app.models.municipios import MunicipiosModel
from app.schemas.municipios import MunicipioSchema
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/municipios/", response_model=List[MunicipioSchema], name="municipios", tags=["municipios"])
async def get_municipios(
    codigo: Optional[str] = Query(None, description="Código del municipio"),
    municipio: Optional[str] = Query(None, description="Municipio"),
    departamento: Optional[str] = Query(None, description="Departamento"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
    db: SQLAlchemySession = Depends(get_db)):
    try:
        query = db.query(MunicipiosModel).order_by(desc(MunicipiosModel.codigo))
        if codigo:
            query = query.filter(MunicipiosModel.codigo == codigo)
        if municipio:
            query = query.filter(MunicipiosModel.municipio.ilike(f"%{municipio}%"))
        if departamento:
            query = query.filter(MunicipiosModel.departamento.ilike(f"%{departamento}%"))
            
        result = query.offset(skip).limit(limit).all()
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))         
   
@router.post("/municipio/crear/", status_code=201, tags=["municipios"])
async def create_municipio(
    municipio: MunicipioSchema,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        new_municipio = MunicipiosModel(**municipio.model_dump())
        db.add(new_municipio)
        db.commit()
        return JSONResponse(status_code=201, content={"message": "Municipio creado exitosamente", "id": new_municipio.id})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.put("/municipio/actualizar/{codigo}", tags=["municipios"])
async def update_municipio(
    codigo: str,
    municipio: MunicipioSchema,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_municipio = db.query(MunicipiosModel).filter(MunicipiosModel.codigo == codigo).first()
        if not db_municipio:
            raise HTTPException(status_code=404, detail="Municipio no encontrado")

        update_data = municipio.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_municipio, key, value)

        db.commit()
        return JSONResponse(status_code=200, content={"message": "Municipio actualizado exitosamente"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 

@router.delete("/municipio/eliminar/{codigo}", tags=["municipios"])
async def delete_municipio(
    codigo: str,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_municipio = db.query(MunicipiosModel).filter(MunicipiosModel.codigo == codigo).first()
        if not db_municipio:
            raise HTTPException(status_code=404, detail="Municipio no encontrado")

        db.delete(db_municipio)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Municipio eliminado exitosamente"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
