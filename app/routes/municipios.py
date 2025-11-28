# app/routes/municipios.py
"""
Router de municipios de Guatemala (RENAP)
Incluye búsqueda rápida, autocomplete y CRUD protegido
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional

from app.database.db import get_db
from app.models.municipios import MunicipiosModel
from app.schemas.municipios import MunicipioSchema, MunicipioListResponse, MunicipioSimple
from app.database.security import get_current_user
from app.models.user import UserModel


router = APIRouter(prefix="/municipios", tags=["Ubicación"])


# =============================================================================
# LISTAR Y BUSCAR MUNICIPIOS (PÚBLICO - SIN AUTH)
# =============================================================================
@router.get("/", response_model=MunicipioListResponse)
def listar_municipios(
    q: Optional[str] = Query(None, description="Búsqueda por municipio o departamento"),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(MunicipiosModel).order_by(
        MunicipiosModel.departamento, MunicipiosModel.municipio
    )

    if departamento:
        query = query.filter(MunicipiosModel.departamento.ilike(f"%{departamento}%"))
    if q:
        query = query.filter(
            func.unaccent(MunicipiosModel.municipio).ilike(func.unaccent(f"%{q}%"))
            | func.unaccent(MunicipiosModel.departamento).ilike(func.unaccent(f"%{q}%"))
        )

    total = query.count()
    municipios = query.offset(skip).limit(limit).all()

    return MunicipioListResponse(total=total, municipios=municipios)


# =============================================================================
# AUTOCOMPLETE - IDEAL PARA <select> EN FRONTEND
# =============================================================================
@router.get("/select", response_model=List[MunicipioSimple])
def para_select(
    q: Optional[str] = Query(None, min_length=2),
    db: Session = Depends(get_db)
):
    query = db.query(MunicipiosModel).order_by(MunicipiosModel.departamento, MunicipiosModel.municipio)

    if q:
        q = q.strip()
        query = query.filter(
            func.unaccent(MunicipiosModel.municipio).ilike(func.unaccent(f"%{q}%"))
            | func.unaccent(MunicipiosModel.departamento).ilike(func.unaccent(f"%{q}%"))
        )

    resultados = query.limit(20).all()
    return [MunicipioSimple.from_orm(m) for m in resultados]


# =============================================================================
# CRUD PROTEGIDO - SOLO ADMIN
# =============================================================================
@router.post("/", response_model=MunicipioSchema, status_code=201)
def crear_municipio(
    municipio: MunicipioSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")

    if db.query(MunicipiosModel).filter(MunicipiosModel.codigo == municipio.codigo).first():
        raise HTTPException(status_code=400, detail="Código de municipio ya existe")

    nuevo = MunicipiosModel(**municipio.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{codigo}", response_model=MunicipioSchema)
def actualizar_municipio(
    codigo: str,
    datos: MunicipioSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")

    municipio = db.query(MunicipiosModel).filter(MunicipiosModel.codigo == codigo).first()
    if not municipio:
        raise HTTPException(status_code=404, detail="Municipio no encontrado")

    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(municipio, key, value)

    db.commit()
    db.refresh(municipio)
    return municipio


@router.delete("/{codigo}", status_code=204)
def eliminar_municipio(
    codigo: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")

    municipio = db.query(MunicipiosModel).filter(MunicipiosModel.codigo == codigo).first()
    if not municipio:
        raise HTTPException(status_code=404, detail="Municipio no encontrado")

    db.delete(municipio)
    db.commit()
    return None