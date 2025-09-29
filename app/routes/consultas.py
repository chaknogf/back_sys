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
        
        

@router.get("/consultas/", response_model=List[VistaConsultas], tags=["consultas"])
async def get_consultas(
    paciente_id: Optional[int] = Query(None),
    consulta_id: Optional[int] = Query(None),
    especialidad: Optional[str] = Query(None),
    servicio: Optional[str] = Query(None),
    tipo_consulta: Optional[int] = Query(None),
    documento: Optional[str] = Query(None),
    fecha_consulta: Optional[str] = Query(None),
    ciclo: Optional[str] = Query(None),
    primer_nombre: Optional[str] = Query(None),
    segundo_nombre: Optional[str] = Query(None),
    primer_apellido: Optional[str] = Query(None),
    segundo_apellido: Optional[str] = Query(None),
    expediente: Optional[str] = Query(None),
    cui: Optional[int] = Query(None),
    fecha_nacimiento: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        query = db.query(VistaConsultasModel).order_by(desc(VistaConsultasModel.id_consulta))

        if paciente_id:
            query = query.filter(VistaConsultasModel.id_paciente == paciente_id)
        if consulta_id:
            query = query.filter(VistaConsultasModel.id_consulta == consulta_id)
        if especialidad:
            query = query.filter(VistaConsultasModel.especialidad == especialidad)
        if servicio:
            query = query.filter(VistaConsultasModel.servicio == servicio)
        if tipo_consulta:
            query = query.filter(VistaConsultasModel.tipo_consulta == tipo_consulta)
        if documento:
            query = query.filter(VistaConsultasModel.documento == documento)
        if fecha_consulta:
            query = query.filter(VistaConsultasModel.fecha_consulta == fecha_consulta)
        if ciclo:
            query = query.filter(
                cast(VistaConsultasModel.ciclo, JSONB).contains({"estado": ciclo})
            )
        if primer_nombre:
            query = query.filter(VistaConsultasModel.primer_nombre.ilike(f"%{primer_nombre}%"))
        if segundo_nombre:
            query = query.filter(VistaConsultasModel.segundo_nombre.ilike(f"%{segundo_nombre}%"))
        if primer_apellido:
            query = query.filter(VistaConsultasModel.primer_apellido.ilike(f"%{primer_apellido}%"))
        if segundo_apellido:
            query = query.filter(VistaConsultasModel.segundo_apellido.ilike(f"%{segundo_apellido}%"))
        if expediente:
            query = query.filter(VistaConsultasModel.expediente == expediente)
        if cui:
            query = query.filter(VistaConsultasModel.cui == cui)
        if fecha_nacimiento:
            query = query.filter(VistaConsultasModel.fecha_nacimiento == fecha_nacimiento)

        result = query.offset(skip).limit(limit).all()
        return result

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/consulta/", response_model=ConsultaUpdate, tags=["consultas"])
async def get_consulta(
    id_consulta: Optional[int] = Query(None),
    expediente: Optional[str] = Query(None),
    documento: Optional[str] = Query(None),
    # token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        query = db.query(ConsultaModel).order_by(desc(ConsultaModel.id))
        if id_consulta:
            query = query.filter(ConsultaModel.id == id_consulta)

        if expediente:
            query = query.filter(ConsultaModel.expediente == expediente)
        if documento:
            query = query.filter(ConsultaModel.documento == documento)

        db_consulta = query.first()

        if not db_consulta:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")

        return db_consulta

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {str(e)}")
    finally:
        db.close()



@router.post("/consulta/crear/", response_model=ConsultaUpdate, status_code=201, tags=["consultas"])
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

            # Convertir el objeto pydantic a dict
            consulta_dict = consulta.model_dump()
            consulta_dict["orden"] = nuevo_orden

            # ⚡ Si tipo_consulta == 3, generar correlativo y asignar al documento
            if consulta.tipo_consulta == 3:
                correlativo = generar_emergencia(db)
                consulta_dict["documento"] = correlativo

            # Crear el objeto consulta
            new_consulta = ConsultaModel(**consulta_dict)
            db.add(new_consulta)
            db.flush()  # forzar insert en la transacción

        db.refresh(new_consulta)

        return JSONResponse(
            status_code=201,
            content={
                "message": "Consulta creada exitosamente",
                "id": new_consulta.id,
                "orden": new_consulta.orden,
                "documento": new_consulta.documento
            }
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
@router.put("/consulta/actualizar/{consulta_id}", tags=["consultas"])
async def update_consulta(
    consulta_id: int,
    consulta: ConsultaUpdate,
    # token: str = Depends(oauth2_scheme),
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
    # token: str = Depends(oauth2_scheme),
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
