from datetime import date
from typing import Optional
from app.utils.expediente import generar_constancia_nacimiento as generar_cn
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.security import get_current_user
from app.models.user import UserModel
from app.models.constancias_nacimiento import ConstanciaNacimientoModel
from app.models.constancia_nacimiento_historial import ConstanciaNacimientoHistorialModel
from app.schemas.constancia_nacimiento import (
    ConstanciaNacimientoCreate,
    ConstanciaNacimientoHistorialResponse,
    ConstanciaNacimientoUpdate,
    ConstanciaNacimientoResponse
)

router = APIRouter(prefix="/constancias-nacimiento", tags=["Constancias Nacimiento"])


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

@router.get("/", response_model=list[ConstanciaNacimientoResponse])
def listar_constancias(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    id_usuario: Optional[int] = None,
    id_constancia: Optional[int] = None,
    nombre_madre: Optional[str] = None,
    fecha: Optional[date] = None,
    documento: Optional[str] = None,
    limit: int = 100, offset: int = 0
    ):
    query = db.query(ConstanciaNacimientoModel)
    if id_usuario is not None:
        query = query.filter(ConstanciaNacimientoModel.registrador_id == id_usuario)
    if id_constancia is not None:
        query = query.filter(ConstanciaNacimientoModel.id == id_constancia)
    if nombre_madre is not None:
        query = query.filter(ConstanciaNacimientoModel.nombre_madre.ilike(f"%{nombre_madre}%"))
    if fecha is not None:
        query = query.filter(ConstanciaNacimientoModel.fecha_registro == fecha)
    if documento is not None:
        query = query.filter(ConstanciaNacimientoModel.documento == documento)
    constancias = query.offset(offset).limit(limit).all()
    return constancias

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

    # ── Auto-generar documento si aún no tiene ────────────────────────────
    if not constancia.documento:
        constancia.documento = generar_cn(db)

    # Guardar historial antes de modificar
    state = inspect(constancia)
    historial = ConstanciaNacimientoHistorialModel(
        constancia_id=constancia.id,
        datos_anteriores={
            attr.key: getattr(constancia, attr.key)
            for attr in state.mapper.column_attrs
        },
        usuario_id=current_user.id,
        motivo=data.motivo
    )
    db.add(historial)

    update_data = data.model_dump(exclude_unset=True)
    update_data.pop("motivo", None)

    for key, value in update_data.items():
        setattr(constancia, key, value)

    db.commit()
    db.refresh(constancia)

    return constancia

@router.delete("/{constancia_id}")
def eliminar_constancia(
    constancia_id: int, db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    constancia = db.get(ConstanciaNacimientoModel, constancia_id)
    if not constancia:
        raise HTTPException(status_code=404, detail="Constancia no encontrada")

    db.delete(constancia)
    db.commit()
    return {"message": "Constancia eliminada correctamente"}




