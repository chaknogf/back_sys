from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import String, desc, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text
from typing import Optional, List
from app.database.db import SessionLocal
from app.models.pacientes import PacienteModel
from app.schemas.paciente import PacienteBase, PacienteCreate, PacienteOut, PacienteUpdate
from fastapi.security import OAuth2PasswordBearer
from app.utils.expediente import generar_expediente

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/pacientes/", response_model=List[PacienteUpdate], tags=["pacientes"])
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
    # token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        query = db.query(PacienteModel).order_by(desc(PacienteModel.id))

        if id:
            query = query.filter(PacienteModel.id == id)

        if identificador:
            query = query.filter(
                (PacienteModel.cui.cast(String).ilike(f"%{identificador}%")) |
                (PacienteModel.expediente.ilike(f"%{identificador}%")) |
                (PacienteModel.pasaporte.ilike(f"%{identificador}%")) |
                (PacienteModel.otro_id.ilike(f"%{identificador}%"))
            )

        if nombre_completo:
            query = query.filter(PacienteModel.nombre_completo.ilike(f"%{nombre_completo}%"))

        if primer_nombre:
            query = query.filter(PacienteModel.nombre["primer_nombre"].astext.ilike(f"%{primer_nombre}%"))

        if segundo_nombre:
            query = query.filter(PacienteModel.nombre["segundo_nombre"].astext.ilike(f"%{segundo_nombre}%"))

        if primer_apellido:
            query = query.filter(PacienteModel.nombre["primer_apellido"].astext.ilike(f"%{primer_apellido}%"))

        if segundo_apellido:
            query = query.filter(PacienteModel.nombre["segundo_apellido"].astext.ilike(f"%{segundo_apellido}%"))

        if referencia:
            query = query.filter(
                text("""
                    EXISTS (
                        SELECT 1 FROM jsonb_each_text("pacientes"."referencias") AS ref
                        WHERE ref.value::jsonb->>'nombre' ILIKE :referencia
                    )
                """)
            ).params(referencia=f"%{referencia}%")

        if estado:
            query = query.filter(PacienteModel.estado == estado)

        if sexo:
            query = query.filter(PacienteModel.sexo == sexo)

        if fecha_nacimiento:
            try:
                fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
                query = query.filter(PacienteModel.fecha_nacimiento == fecha_nac)
            except ValueError:
                raise HTTPException(status_code=422, detail="Formato de fecha_nacimiento inválido (use YYYY-MM-DD)")

        if fecha_defuncion and hasattr(PacienteModel, "fecha_defuncion"):
            try:
                fecha_def = datetime.strptime(fecha_defuncion, "%Y-%m-%d").date()
                query = query.filter(PacienteModel.fecha_defuncion == fecha_def)
            except ValueError:
                raise HTTPException(status_code=422, detail="Formato de fecha_defuncion inválido (use YYYY-MM-DD)")

        pacientes = query.offset(skip).limit(limit).all()
        return JSONResponse(status_code=200, content=jsonable_encoder(pacientes))

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar pacientes: {str(e)}")
    


@router.post("/paciente/crear/", status_code=201, tags=["pacientes"])
async def create_paciente(
    paciente: PacienteCreate,
    # token: str = Depends(oauth2_scheme),
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
    
@router.post("/paciente/crearExp/", status_code=201, tags=["pacientes"])
async def create_expediente(
    paciente: PacienteCreate,
    # token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        
        expediente = generar_expediente(db)
        paciente_dict = paciente.model_dump()
        paciente_dict["expediente"] = expediente
        
        new_paciente = PacienteModel(**paciente_dict)
        db.add(new_paciente)
        db.commit()
        db.refresh(new_paciente)
        
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "Paciente creado exitosamente",
                "id": new_paciente.id,
                "expediente": new_paciente.expediente
            }
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear paciente: {str(e)}")

@router.put("/paciente/actualizar/{paciente_id}", tags=["pacientes"])
async def update_paciente(
    paciente_id: int,
    paciente: PacienteUpdate,
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
    # token: str = Depends(oauth2_scheme),
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
