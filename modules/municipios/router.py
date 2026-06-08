from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional

from core.database import get_db
from modules.municipios.models import MunicipiosModel
from modules.municipios.schemas import DepartamentoOut, MunicipioSchema, MunicipioListResponse, MunicipioSimple
from core.security import get_current_user
from modules.users.models import UserModel


router = APIRouter(prefix="/municipios", tags=["Ubicación"])


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


@router.get("/departamentos", response_model=List[DepartamentoOut])
def listar_departamentos(db: Session = Depends(get_db)):
    resultados = (
        db.query(
            func.substr(MunicipiosModel.codigo, 1, 2).label("codigo"),
            MunicipiosModel.departamento.label("departamento")
        )
        .distinct()
        .order_by("codigo")
        .all()
    )

    return resultados
