# app/routes/medicos.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.models.medicos import MedicoModel
from app.schemas.medicos import MedicoCreate, MedicoUpdate, MedicoOut

router = APIRouter(
    prefix="/medicos",
    tags=["Medicos"]
)


@router.post("/", response_model=MedicoOut, status_code=status.HTTP_201_CREATED)
def crear_medico(data: MedicoCreate, db: Session = Depends(get_db)):
    medico = MedicoModel(**data.model_dump())
    db.add(medico)
    db.commit()
    db.refresh(medico)
    return medico


@router.get("/", response_model=List[MedicoOut])
def listar_medicos(
    activo: bool | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(MedicoModel)

    if activo is not None:
        query = query.filter(MedicoModel.activo == activo)

    return query.order_by(MedicoModel.nombre).all()


@router.get("/{medico_id}", response_model=MedicoOut)
def obtener_medico(medico_id: int, db: Session = Depends(get_db)):
    medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()

    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    return medico


@router.put("/{medico_id}", response_model=MedicoOut)
def actualizar_medico(
    medico_id: int,
    data: MedicoUpdate,
    db: Session = Depends(get_db)
):
    medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()

    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(medico, key, value)

    db.commit()
    db.refresh(medico)

    return medico


@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medico(medico_id: int, db: Session = Depends(get_db)):
    medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()

    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    try:
        db.delete(medico)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el médico porque está relacionado con otros registros"
        )

    return