# app/routes/citas.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.models.citas import CitaModel
from app.schemas.citas import CitaCreate, CitaUpdate, CitaResponse

router = APIRouter(
    prefix="/citas",
    tags=["Citas"]
)


@router.post("/", response_model=CitaResponse)
def crear_cita(cita: CitaCreate, db: Session = Depends(get_db)):
    nueva_cita = CitaModel(**cita.dict())
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita


@router.get("/", response_model=List[CitaResponse])
def listar_citas(
    id: int = None,
    expediente: str = None,
    paciente_id: int = None,
    especialidad: str = None,
    fecha: str = None,
    limite: int = 200,
    db: Session = Depends(get_db)):
    query = db.query(CitaModel)
    if id is not None:
        query = query.filter(CitaModel.id == id)
    if expediente is not None:
        query = query.filter(CitaModel.expediente == expediente)
    if paciente_id is not None:
        query = query.filter(CitaModel.paciente_id == paciente_id)
    if especialidad is not None:
        query = query.filter(CitaModel.especialidad == especialidad)
    if fecha is not None:
        query = query.filter(CitaModel.agenda == fecha)
    return query.limit(limite).all()


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