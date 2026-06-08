from datetime import date
from typing import Optional
from modules.pacientes.models import PacienteModel
from modules.expediente.service import generar_constancia_nacimiento as generar_cn
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import inspect, desc, or_
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal
from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.constancias_nacimiento.models import ConstanciaNacimientoModel
from modules.constancias_nacimiento.models import ConstanciaNacimientoHistorialModel
from modules.constancias_nacimiento.schemas import (
    ConstanciaNacimientoCreate,
    ConstanciaNacimientoHistorialResponse,
    ConstanciaNacimientoListResponse,
    ConstanciaNacimientoUpdate,
    ConstanciaNacimientoResponse
)

router = APIRouter(prefix="/constancias-nacimiento", tags=["Constancias Nacimiento"])


def _serializar(v):
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    return v

@router.post("/", response_model=ConstanciaNacimientoResponse)
def crear_constancia(
    data: ConstanciaNacimientoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    data_dict = data.model_dump(exclude={"registrador_id"})
    nueva = ConstanciaNacimientoModel(**data_dict)
    nueva.registrador_id = current_user.id
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/", response_model=ConstanciaNacimientoListResponse)
def listar_constancias(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    id_usuario:     Optional[int]  = None,
    id_constancia:  Optional[int]  = None,
    nombre_madre:   Optional[str]  = None,
    fecha:          Optional[date] = None,
    documento:      Optional[str]  = None,
    expediente:      Optional[str]  = None,
    limit:  int = 10,
    offset: int = 0,
):
    query = db.query(ConstanciaNacimientoModel)

    if id_usuario is not None:
        query = query.filter(ConstanciaNacimientoModel.registrador_id == id_usuario)

    if id_constancia is not None:
        query = query.filter(ConstanciaNacimientoModel.id == id_constancia)

    if nombre_madre and nombre_madre.strip():
        query = query.filter(
            ConstanciaNacimientoModel.nombre_madre.ilike(f"%{nombre_madre.strip()}%")
        )

    if fecha is not None:
        query = query.filter(ConstanciaNacimientoModel.fecha_registro == fecha)

    if documento and documento.strip():
        query = query.filter(
            ConstanciaNacimientoModel.documento == documento.strip()
        )
    if expediente and expediente.strip():
        exp = expediente.strip()
        query = query.filter(
            or_(
                ConstanciaNacimientoModel.paciente.has(
                    PacienteModel.expediente == exp
                ),
                ConstanciaNacimientoModel.madre.has(
                    PacienteModel.expediente == exp
                )
            )
    )
    total = query.count()
    constancias = (
        query
        .order_by(desc(ConstanciaNacimientoModel.id))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return ConstanciaNacimientoListResponse(constancias=constancias, total=total)

@router.get("/historial/{constancia_id}",
            response_model=list[ConstanciaNacimientoHistorialResponse])
def obtener_historial_constancia(
    constancia_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    historial = db.query(ConstanciaNacimientoHistorialModel).filter_by(constancia_id=constancia_id).all()
    return historial

@router.get("/{constancia_id}", response_model=ConstanciaNacimientoResponse)
def obtener_constanciaNac(
    constancia_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    data = db.query(ConstanciaNacimientoModel).filter(
        ConstanciaNacimientoModel.id == constancia_id
    ).first()

    if not data:
        raise HTTPException(status_code=404, detail="No encontrado")

    return data
    

@router.put("/{constancia_id}", response_model=ConstanciaNacimientoResponse)
def actualizar_constancia(
    constancia_id: int,
    data: ConstanciaNacimientoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    constancia = db.get(ConstanciaNacimientoModel, constancia_id)
    if not constancia:
        raise HTTPException(status_code=404, detail="Constancia no encontrada")

    if not constancia.documento or not constancia.documento.strip():
        constancia.documento = generar_cn(db)

    state = inspect(constancia)
    historial = ConstanciaNacimientoHistorialModel(
        constancia_id=constancia.id,
        datos_anteriores={
            attr.key: _serializar(getattr(constancia, attr.key))
            for attr in state.mapper.column_attrs
        },
    usuario_id=current_user.id,
   
)
    db.add(historial)

    update_data = data.model_dump(exclude_unset=True)
   

    for key, value in update_data.items():
        setattr(constancia, key, value)

    db.commit()
    db.refresh(constancia)

    return constancia

@router.delete("/{constancia_id}")
def eliminar_constancia(
    constancia_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    constancia = db.get(ConstanciaNacimientoModel, constancia_id)
    if not constancia:
        raise HTTPException(status_code=404, detail="Constancia no encontrada")

    db.query(ConstanciaNacimientoHistorialModel)\
      .filter(ConstanciaNacimientoHistorialModel.constancia_id == constancia_id)\
      .delete()

    db.delete(constancia)
    db.commit()
    return {"message": "Constancia eliminada correctamente"}
