from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, date, time, timedelta
from core.database import get_db
from modules.users.models import UserModel
from modules.procedimientos.models import Procedimiento as ProcedimientoModel
from modules.procedimientos.models import ProceMedico as ProceMedicoModel
from modules.procedimientos.schemas import (
    ProcedimientoBase,
    ProcedimientoCreate,
    ProcedimientoUpdate,
    ProcedimientoOut,
    ProcedimientoResponse,
    ProceMedicoBase,
    ProceMedicoCreate,
    ProceMedicoUpdate,
    ProceMedicoOut,
    ProceMedicoInDB,
    ProceMedicoResponse,
    ProcedimientosListResponse
)
from core.security import get_current_user

router = APIRouter(
    prefix="/procedimientos",
    tags=["Procedimientos"]
)


@router.get("/catalogo", response_model=list[ProcedimientoOut])
def listar_procedimientos(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    return (
        db.query(ProcedimientoModel)
        .order_by(ProcedimientoModel.nombre)
        .all()
    )
    
@router.get("/catalogo/{id}", response_model=ProcedimientoOut)
def obtener_procedimiento(
    id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    procedimiento = (
        db.query(ProcedimientoModel)
        .filter(ProcedimientoModel.id == id)
        .first()
    )

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento no encontrado"
        )

    return procedimiento

@router.post("/catalogo", response_model=ProcedimientoOut)
def crear_procedimiento(
    datos: ProcedimientoCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(ProcedimientoModel).filter(
        (ProcedimientoModel.nombre == datos.nombre) |
        (ProcedimientoModel.abreviatura == datos.abreviatura)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un procedimiento con ese nombre o abreviatura"
        )
    
    procedimiento = ProcedimientoModel(
        **datos.model_dump()
    )

    db.add(procedimiento)
    db.commit()
    db.refresh(procedimiento)

    return procedimiento

@router.put("/catalogo/{id}", response_model=ProcedimientoOut)
def actualizar_procedimiento(
    id: int,
    datos: ProcedimientoUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    procedimiento = (
        db.query(ProcedimientoModel)
        .filter(ProcedimientoModel.id == id)
        .first()
    )

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento no encontrado"
        )
    
    if datos.nombre or datos.abreviatura:
        conflict = db.query(ProcedimientoModel).filter(
            ProcedimientoModel.id != id,
            (ProcedimientoModel.nombre == datos.nombre) |
            (ProcedimientoModel.abreviatura == datos.abreviatura)
        ).first()
        
        if conflict:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro procedimiento con ese nombre o abreviatura"
            )

    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(procedimiento, key, value)

    db.commit()
    db.refresh(procedimiento)

    return procedimiento

@router.delete("/catalogo/{id}")
def eliminar_procedimiento(
    id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    procedimiento = (
        db.query(ProcedimientoModel)
        .filter(ProcedimientoModel.id == id)
        .first()
    )

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento no encontrado"
        )
    
    count = db.query(ProceMedicoModel).filter(
        ProceMedicoModel.id_procedimiento == id
    ).count()
    
    if count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el procedimiento porque tiene {count} registros asociados"
        )

    db.delete(procedimiento)
    db.commit()

    return {
        "message": "Procedimiento eliminado"
    }
    
    
@router.get("/", response_model=ProcedimientosListResponse)
def listar_procedimientos_medicos(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    especialidad: Optional[str] = Query(None),
    lugar_servicio: Optional[str] = Query(None),
    id_procedimiento: Optional[int] = Query(None),
    mes: Optional[int] = Query(None, ge=1, le=12),
    anio: Optional[int] = Query(None, ge=2000, le=2100),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None)
):
    query = (
        db.query(ProceMedicoModel)
        .options(joinedload(ProceMedicoModel.procedimiento))
    )

    if especialidad:
        query = query.filter(
            ProceMedicoModel.especialidad == especialidad
        )

    if lugar_servicio:
        query = query.filter(
            ProceMedicoModel.lugar_servicio == lugar_servicio
        )

    if id_procedimiento:
        query = query.filter(
            ProceMedicoModel.id_procedimiento == id_procedimiento
        )

    if fecha_inicio:
        query = query.filter(
            ProceMedicoModel.fecha >= fecha_inicio
        )

    if fecha_fin:
        query = query.filter(
            ProceMedicoModel.fecha <= fecha_fin
        )

    elif mes and anio:
        fecha_inicio_mes = date(anio, mes, 1)

        if mes == 12:
            fecha_fin_mes = date(anio + 1, 1, 1)
        else:
            fecha_fin_mes = date(anio, mes + 1, 1)

        query = query.filter(
            ProceMedicoModel.fecha >= fecha_inicio_mes,
            ProceMedicoModel.fecha < fecha_fin_mes
        )

    elif anio:
        query = query.filter(
            ProceMedicoModel.fecha >= date(anio, 1, 1),
            ProceMedicoModel.fecha <= date(anio, 12, 31)
        )

    total = query.count()

    procedimientos = (
        query.order_by(ProceMedicoModel.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return ProcedimientosListResponse(
        total=total,
        procedimientos=procedimientos
    )


@router.get("/{id}", response_model=ProceMedicoResponse)
def obtener_procedimiento_medico(
    id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_procedimiento: bool = Query(False, description="Incluir información del procedimiento")
):
    query = db.query(ProceMedicoModel)
    
    if include_procedimiento:
        query = query.options(joinedload(ProceMedicoModel.procedimiento))
    
    procedimiento = query.filter(ProceMedicoModel.id == id).first()

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento médico no encontrado"
        )
    
    response = ProceMedicoResponse.model_validate(procedimiento)
    
    if include_procedimiento and procedimiento.procedimiento:
        response.procedimiento_info = ProcedimientoOut.model_validate(procedimiento.procedimiento)

    return response


@router.post("/", response_model=ProceMedicoOut, status_code=201)
def crear_procedimiento_medico(
    datos: ProceMedicoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if datos.id_procedimiento:
        existe = (
            db.query(ProcedimientoModel)
            .filter(
                ProcedimientoModel.id == datos.id_procedimiento
            )
            .first()
        )

        if not existe:
            raise HTTPException(
                status_code=404,
                detail="Procedimiento no encontrado"
            )

    nuevo = ProceMedicoModel(
        **datos.model_dump(exclude={'created_by'}),
        created_by=current_user.username[:10] if current_user.username else None
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.put("/{id}", response_model=ProceMedicoOut)
def actualizar_procedimiento_medico(
    id: int,
    datos: ProceMedicoUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    procedimiento = (
        db.query(ProceMedicoModel)
        .filter(ProceMedicoModel.id == id)
        .first()
    )

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento médico no encontrado"
        )

    if datos.id_procedimiento:
        existe = (
            db.query(ProcedimientoModel)
            .filter(
                ProcedimientoModel.id == datos.id_procedimiento
            )
            .first()
        )

        if not existe:
            raise HTTPException(
                status_code=404,
                detail="Procedimiento no encontrado"
            )

    for campo, valor in datos.model_dump(
        exclude_unset=True
    ).items():
        setattr(procedimiento, campo, valor)

    db.commit()
    db.refresh(procedimiento)

    return procedimiento


@router.delete("/{id}")
def eliminar_procedimiento_medico(
    id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    procedimiento = (
        db.query(ProceMedicoModel)
        .filter(ProceMedicoModel.id == id)
        .first()
    )

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento médico no encontrado"
        )

    db.delete(procedimiento)
    db.commit()

    return {
        "message": "Procedimiento médico eliminado"
    }


@router.get("/estadisticas/resumen")
def obtener_estadisticas(
    anio: int = Query(..., ge=2000, le=2100),
    mes: Optional[int] = Query(None, ge=1, le=12),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ProceMedicoModel)
    
    if mes:
        fecha_inicio = date(anio, mes, 1)
        if mes == 12:
            fecha_fin = date(anio + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin = date(anio, mes + 1, 1) - timedelta(days=1)
    else:
        fecha_inicio = date(anio, 1, 1)
        fecha_fin = date(anio, 12, 31)
    
    query = query.filter(
        ProceMedicoModel.fecha >= fecha_inicio,
        ProceMedicoModel.fecha <= fecha_fin
    )
    
    total_procedimientos = query.count()
    total_cantidad = query.with_entities(func.sum(ProceMedicoModel.cantidad)).scalar() or 0
    
    top_procedimientos = (
        db.query(
            ProcedimientoModel.nombre,
            func.count(ProceMedicoModel.id).label('total')
        )
        .join(ProceMedicoModel, ProceMedicoModel.id_procedimiento == ProcedimientoModel.id)
        .filter(
            ProceMedicoModel.fecha >= fecha_inicio,
            ProceMedicoModel.fecha <= fecha_fin
        )
        .group_by(ProcedimientoModel.id)
        .order_by(func.count(ProceMedicoModel.id).desc())
        .limit(5)
        .all()
    )
    
    return {
        "anio": anio,
        "mes": mes,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "total_registros": total_procedimientos,
        "total_cantidad_procedimientos": total_cantidad,
        "top_procedimientos": [
            {"nombre": p.nombre, "total": p.total} for p in top_procedimientos
        ]
    }
