# app/routes/ciclos_consulta.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.database.db import get_db
from app.models.ciclos_consultas import CiclosConsulta
from app.models.consultas import ConsultaModel
from app.schemas.ciclos_consultas import CicloConsulta, CicloConsultaBase, CicloOut
from app.database.security import get_current_user
from app.models.user import UserModel

router = APIRouter(prefix="/ciclos", tags=["Ciclos Clínicos"])

@router.get("/consulta/{consulta_id}", response_model=List[CicloConsulta])
def obtener_ciclos_por_consulta(
    consulta_id: int,
    activo: Optional[bool] = Query(True),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    query = db.query(CiclosConsulta).filter(
        CiclosConsulta.consulta_id == consulta_id
    )

    if activo is not None:
        query = query.filter(CiclosConsulta.activo.is_(activo))

    ciclos = query.order_by(CiclosConsulta.numero.asc()).all()

    return ciclos

@router.get("/{ciclo_id}", response_model=CicloOut)
def obtener_ciclo(
    ciclo_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    ciclo = (
        db.query(CiclosConsulta)
        .options(joinedload(CiclosConsulta.consulta))
        .filter(CiclosConsulta.id == ciclo_id)
        .first()
    )

    if not ciclo:
        raise HTTPException(status_code=404, detail="Ciclo no encontrado")

    return ciclo

@router.post("/", response_model=CicloConsulta, status_code=201)
def crear_ciclo(
    data: CicloConsultaBase,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # ======================
    # 1. Validar consulta
    # ======================
    consulta = db.get(ConsultaModel, data.consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    # ======================
    # 2. Obtener siguiente número automático
    # ======================
    ultimo_numero = (
        db.query(func.coalesce(func.max(CiclosConsulta.numero), 0))
        .filter(CiclosConsulta.consulta_id == data.consulta_id)
        .scalar()
    ) or 0

    nuevo_numero = ultimo_numero + 1

    # ======================
    # 3. Crear ciclo
    # ======================
    nuevo = CiclosConsulta(
        consulta_id=data.consulta_id,
        numero=nuevo_numero,
        activo=True,
        registro=datetime.utcnow(),
        usuario=current_user.username,
        especialidad=data.especialidad,
        servicio=data.servicio,
        contenido=data.contenido,
        datos_medicos=data.datos_medicos
    )

    db.add(nuevo)

    try:
        db.commit()
        db.refresh(nuevo)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear ciclo: {str(e)}"
        )

    return nuevo