# app/routes/citas.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, time
from app.database.db import get_db
from app.models.user import UserModel
from app.models.citas import CitaModel
from app.schemas.citas import CitaCreate, CitaUpdate, CitaResponse, CitaBase
from app.database.security import get_current_user

router = APIRouter(
    prefix="/citas",
    tags=["Citas"]
)




@router.post("/", response_model=CitaBase)
def crear_cita(
    cita: CitaCreate,
    current_user: UserModel = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    nueva_cita = CitaModel(
        created_by = current_user.id,  
        fecha_registro = cita.fecha_registro,  
        expediente = cita.expediente,
        paciente_id = cita.paciente_id,
        especialidad = cita.especialidad,
        fecha_cita = cita.fecha_cita,
        datos_extra = cita.datos_extra
    )

    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita


@router.get("/", response_model=List[CitaResponse])
def listar_citas(
    id: Optional[int] = None,
    expediente: Optional[str] = None,
    paciente_id: Optional[int] = None,
    especialidad: Optional[str] = None,
    fecha_cita: Optional[date] = None,
    limit: int = 200,
    skip: int = 0,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)):
    query = db.query(CitaModel)
    if fecha_cita is None:
        fecha_cita = date.today()
    if id is not None:
        query = query.filter(CitaModel.id == id)
    if expediente is not None:
        query = query.filter(CitaModel.expediente == expediente)
    if paciente_id is not None:
        query = query.filter(CitaModel.paciente_id == paciente_id)
    if especialidad is not None:
        query = query.filter(CitaModel.especialidad == especialidad)
    if fecha_cita is not None:

        query = query.filter(CitaModel.fecha_cita == fecha_cita)
    return query.order_by(CitaModel.id.desc()).offset(skip).limit(limit).all()


@router.get("/{cita_id}", response_model=CitaResponse)
def obtener_cita(cita_id: int, db: Session = Depends(get_db)):
    cita = db.query(CitaModel).filter(CitaModel.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return cita


@router.put("/{cita_id}", response_model=CitaResponse)
def actualizar_cita(cita_id: int, datos: CitaUpdate, db: Session = Depends(get_db)):
    cita = db.query(CitaModel).filter(CitaModel.id == cita_id).first()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    for key, value in datos.dict(exclude_unset=True).items():
        setattr(cita, key, value)

    db.commit()
    db.refresh(cita)
    return cita


@router.delete("/{cita_id}")
def eliminar_cita(cita_id: int, db: Session = Depends(get_db)):
    cita = db.query(CitaModel).filter(CitaModel.id == cita_id).first()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    db.delete(cita)
    db.commit()

    return {"message": "Cita eliminada correctamente"}