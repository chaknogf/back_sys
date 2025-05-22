from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc, cast
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from app.database.db import SessionLocal
from app.models.pacientes import PacienteModel
from app.schemas.paciente import PacienteBase, PacienteCreate, PacienteOut
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/pacientes/", response_model=List[PacienteBase], tags=["pacientes"])
async def get_pacientes(
    id: Optional[int] = Query(None),
    identificador: Optional[str] = Query(None),
    primer_nombre: Optional[str] = Query(None),
    segundo_nombre: Optional[str] = Query(None),
    primer_apellido: Optional[str] = Query(None),
    segundo_apellido: Optional[str] = Query(None),
    nombre_completo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    fecha_nacimiento: Optional[str] = Query(None),
    fecha_defuncion: Optional[str] = Query(None),
    sexo: Optional[str] = Query(None),
    referencia: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        query = db.query(PacienteModel).order_by(desc(PacienteModel.id))

        if id:
            query = query.filter(PacienteModel.id == id)
        if identificador:
            query = query.filter(PacienteModel.identificadores.op('->>')('valor') == identificador)
        if primer_nombre:
            query = query.filter(PacienteModel.identificadores.op('->>')('primer').ilike(f'%{primer_nombre}%'))  # Use ilike for case-insensitive search (primer_nombre)
        if segundo_nombre:
            query = query.filter(PacienteModel.identificadores.op('->>')('segundo').ilike(f'%{segundo_nombre}%'))
        if primer_apellido:
            query = query.filter(PacienteModel.identificadores.op('->>')('apellido_primero').ilike(f'%{primer_apellido}%'))
        if segundo_apellido:
            query = query.filter(PacienteModel.identificadores.op('->>')('apellido_segundo').ilike(f'%{segundo_apellido}%'))
        if nombre_completo:
            query = query.filter(PacienteModel.identificadores.op('->>')('concat(primer, " ", segundo, " ", apellido_primero, " ", apellido_segundo)').ilike(f'%{nombre_completo}%'))
        if estado:
            query = query.filter(PacienteModel.estado == estado)
        if fecha_nacimiento:
            query = query.filter(PacienteModel.detalles.op('->>')('fecha_nacimiento') == fecha_nacimiento)
        if fecha_defuncion:
            query = query.filter(PacienteModel.detalles.op('->>')('fecha_defuncion') == fecha_defuncion)
        if sexo:
            query = query.filter(PacienteModel.sexo == sexo)
        if referencia:
            query = query.filter(PacienteModel.referencias.op('->>')('nombre').ilike(f'%{referencia}%'))

        result = query.offset(skip).limit(limit).all()
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post("/paciente/crear/", status_code=201, tags=["pacientes"])
async def create_paciente(
    paciente: PacienteCreate,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        new_paciente = PacienteModel(**paciente.model_dump())
        db.add(new_paciente)
        db.commit()
        return JSONResponse(status_code=201, content={"message": "Paciente creado exitosamente", "id": new_paciente.id})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/paciente/actualizar/{paciente_id}", tags=["pacientes"])
async def update_paciente(
    paciente_id: int,
    paciente: PacienteBase,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_paciente = db.query(PacienteModel).filter(PacienteModel.id == paciente_id).first()
        if not db_paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        update_data = paciente.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_paciente, key, value)

        db.commit()
        return JSONResponse(status_code=200, content={"message": "Paciente actualizado exitosamente"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/paciente/eliminar/{paciente_id}", tags=["pacientes"])
async def delete_paciente(
    paciente_id: int,
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_paciente = db.query(PacienteModel).filter(PacienteModel.id == paciente_id).first()
        if not db_paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        db.delete(db_paciente)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Paciente eliminado exitosamente"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
