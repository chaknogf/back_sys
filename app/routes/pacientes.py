# app/routes/pacientes.py
"""
Router de pacientes - Búsqueda avanzada, creación inteligente y CRUD completo
Sistema hospitalario nacional - Guatemala 2025
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import date

from app.database.db import get_db
from app.models.pacientes import PacienteModel
from app.schemas.paciente import (
    PacienteCreate, PacienteOut, PacienteUpdate, PacienteSimple, PacienteListResponse
) 
from app.utils.expediente import generar_expediente
from app.database.security import get_current_user
from app.models.user import UserModel


router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


# =============================================================================
# BÚSQUEDA AVANZADA ULTRARRÁPIDA (con unaccent + JSONB)
# =============================================================================
@router.get("/", response_model=PacienteListResponse)
def buscar_pacientes(
    q: Optional[str] = Query(None, description="Búsqueda libre: CUI, expediente, nombre, etc."),
    cui: Optional[str] = Query(None),
    expediente: Optional[str] = Query(None),
    nombre: Optional[str] = Query(None),
    sexo: Optional[str] = Query(None),
    estado: Optional[str] = Query("A"),
    fecha_nac: Optional[date] = Query(None, description="YYYY-MM-DD"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    query = db.query(PacienteModel).order_by(desc(PacienteModel.id))

    if q:
        q = q.strip()
        query = query.filter(
            (PacienteModel.cui.cast(str).ilike(f"%{q}%")) |
            (PacienteModel.expediente.ilike(f"%{q}%")) |
            (PacienteModel.nombre_completo.ilike(f"%{q}%"))
        )

    if cui and cui.isdigit():
        query = query.filter(PacienteModel.cui == int(cui))
    if expediente:
        query = query.filter(PacienteModel.expediente.ilike(f"%{expediente}%"))
    if nombre:
        query = query.filter(
            func.unaccent(PacienteModel.nombre_completo).ilike(func.unaccent(f"%{nombre}%"))
        )
    if sexo:
        query = query.filter(PacienteModel.sexo == sexo.upper())
    if estado:
        query = query.filter(PacienteModel.estado == estado.upper())
    if fecha_nac:
        query = query.filter(PacienteModel.fecha_nacimiento == fecha_nac)

    total = query.count()
    pacientes = query.offset(skip).limit(limit).all()

    return PacienteListResponse(total=total, pacientes=pacientes)


# =============================================================================
# AUTOCOMPLETE - IDEAL PARA BÚSQUEDA RÁPIDA EN RECEPCCIÓN
# =============================================================================
@router.get("/buscar", response_model=List[PacienteSimple])
def autocomplete(
    q: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    resultados = db.query(PacienteModel).filter(
        (PacienteModel.cui.cast(str).ilike(f"%{q}%")) |
        (PacienteModel.expediente.ilike(f"%{q}%")) |
        (PacienteModel.nombre_completo.ilike(f"%{q}%"))
    ).limit(15).all()

    return [PacienteSimple.from_orm(p) for p in resultados]


# =============================================================================
# CREAR PACIENTE (INTELIGENTE)
# =============================================================================
@router.post("/", response_model=PacienteOut, status_code=201)
def crear_paciente(
    paciente_in: PacienteCreate,
    generar_expediente: bool = Query(True, description="Generar expediente automáticamente"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    data = paciente_in.model_dump()

    # Limpiar campos vacíos
    for field in ["cui", "expediente", "pasaporte", "otro_id"]:
        if data.get(field) in ["", " ", None]:
            data[field] = None

    # Generar expediente si se solicita
    if generar_expediente:
        data["expediente"] = generar_expediente(db)

    try:
        nuevo = PacienteModel(**data)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except IntegrityError as e:
        db.rollback()
        msg = str(e.orig).lower()
        if "unique" in msg or "duplicate" in msg:
            raise HTTPException(status_code=400, detail="CUI o expediente ya existe")
        raise HTTPException(status_code=400, detail="Datos inválidos o duplicados")


# =============================================================================
# OBTENER PACIENTE POR ID
# =============================================================================
@router.get("/{paciente_id}", response_model=PacienteOut)
def obtener_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente


# =============================================================================
# ACTUALIZAR PACIENTE
# =============================================================================
@router.patch("/{paciente_id}", response_model=PacienteOut)
def actualizar_paciente(
    paciente_id: int,
    update: PacienteUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    datos = update.model_dump(exclude_unset=True)
    for key, value in datos.items():
        setattr(paciente, key, value)

    db.commit()
    db.refresh(paciente)
    return paciente


# =============================================================================
# ELIMINAR PACIENTE (lógico o físico)
# =============================================================================
@router.delete("/{paciente_id}", status_code=204)
def eliminar_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")

    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Opción 1: Eliminación lógica
    paciente.estado = "I"
    db.commit()

    # Opción 2: Eliminación física (descomentar si es necesario)
    # db.delete(paciente)
    # db.commit()

    return None