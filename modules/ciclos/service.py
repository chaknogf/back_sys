# modules/ciclos/service.py
from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from modules.ciclos.models import CiclosConsulta
from modules.consultas.models import ConsultaModel
from modules.ciclos.schemas import CicloConsulta, CicloConsultaBase, CicloOut


def obtener_ciclos_por_consulta(
    consulta_id: int,
    activo: Optional[bool] = True,
    db: Session = None,
):
    query = db.query(CiclosConsulta).filter(
        CiclosConsulta.consulta_id == consulta_id
    )

    if activo is not None:
        query = query.filter(CiclosConsulta.activo.is_(activo))

    ciclos = query.order_by(CiclosConsulta.numero.asc()).all()

    return ciclos


def obtener_ciclo(ciclo_id: int, db: Session):
    ciclo = (
        db.query(CiclosConsulta)
        .options(joinedload(CiclosConsulta.consulta))
        .filter(CiclosConsulta.id == ciclo_id)
        .first()
    )

    if not ciclo:
        raise HTTPException(status_code=404, detail="Ciclo no encontrado")

    return ciclo


def crear_ciclo(data: CicloConsultaBase, db: Session, current_user):
    consulta = db.get(ConsultaModel, data.consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    ultimo_numero = (
        db.query(func.coalesce(func.max(CiclosConsulta.numero), 0))
        .filter(CiclosConsulta.consulta_id == data.consulta_id)
        .scalar()
    ) or 0

    nuevo_numero = ultimo_numero + 1

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
