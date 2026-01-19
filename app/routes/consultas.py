# app/routes/consultas.py
"""
Router de consultas médicas - Búsqueda avanzada, creación inteligente y CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text, or_
from typing import Optional, List
from datetime import date

from app.database.db import get_db
from app.models.consultas import ConsultaModel, VistaConsultasModel
from app.models.pacientes import PacienteModel
from app.schemas.consultas import ConsultaCreate, ConsultaOut, ConsultaUpdate
from app.schemas.vista_consulta import VistaConsultas
from app.utils.expediente import generar_expediente, generar_emergencia
from app.database.security import get_current_user
from app.models.user import UserModel
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/consultas", tags=["Consultas Médicas"])


@router.get("/", response_model=List[ConsultaOut])
def buscar_consultas(
    paciente_id: Optional[int] = None,
    expediente: Optional[str] = None,
    cui: Optional[int] = None,
    primer_nombre: Optional[str] = None,
    segundo_nombre: Optional[str] = None,
    primer_apellido: Optional[str] = None,
    segundo_apellido: Optional[str] = None,
    tipo_consulta: Optional[int] = None,
    especialidad: Optional[str] = None,
    fecha: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    query = (
        db.query(ConsultaModel)
        .join(PacienteModel, ConsultaModel.paciente_id == PacienteModel.id)
    )

    # ======================
    # Filtros de CONSULTA
    # ======================
    if paciente_id:
        query = query.filter(ConsultaModel.paciente_id == paciente_id)

    if tipo_consulta:
        query = query.filter(ConsultaModel.tipo_consulta == tipo_consulta)

    if especialidad:
        query = query.filter(
            ConsultaModel.especialidad.ilike(f"%{especialidad}%")
        )

    if fecha:
        query = query.filter(ConsultaModel.fecha_consulta == fecha)

    # ======================
    # Filtros de PACIENTE
    # ======================
    if expediente:
        query = query.filter(
            or_(
                ConsultaModel.expediente == expediente,
                PacienteModel.expediente == expediente
            )
        )

    if cui:
        query = query.filter(PacienteModel.cui == cui)

    if primer_nombre:
        query = query.filter(
            PacienteModel.nombre["primer_nombre"].astext.ilike(f"%{primer_nombre}%")
        )

    if segundo_nombre:
        query = query.filter(
            PacienteModel.nombre["segundo_nombre"].astext.ilike(f"%{segundo_nombre}%")
        )

    if primer_apellido:
        query = query.filter(
            PacienteModel.nombre["primer_apellido"].astext.ilike(f"%{primer_apellido}%")
        )

    if segundo_apellido:
        query = query.filter(
            PacienteModel.nombre["segundo_apellido"].astext.ilike(f"%{segundo_apellido}%")
        )

    resultados = (
        query
        .order_by(ConsultaModel.fecha_consulta.desc())
        .all()
    )

    return resultados
# =============================================================================
# OBTENER UNA CONSULTA POR ID
# =============================================================================
@router.get("/{consulta_id}", response_model=ConsultaOut)
def obtener_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    consulta = db.get(ConsultaModel, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    return consulta


# =============================================================================
# CREAR NUEVA CONSULTA (INTELIGENTE)
# =============================================================================
@router.post("/", response_model=ConsultaOut, status_code=201)
def crear_consulta(
    consulta_in: ConsultaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    paciente = db.get(PacienteModel, consulta_in.paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Generar expediente si no tiene
    if not paciente.expediente:
        paciente.expediente = generar_expediente(db)
        db.add(paciente)

    # Documento
    documento = consulta_in.documento
    if consulta_in.tipo_consulta == 3:  # Emergencia
        documento = generar_emergencia(db)

    # Orden
    ultimo_orden = db.query(func.coalesce(func.max(ConsultaModel.orden), 0)).filter(
        ConsultaModel.fecha_consulta == consulta_in.fecha_consulta,
        ConsultaModel.tipo_consulta == consulta_in.tipo_consulta,
        ConsultaModel.especialidad == consulta_in.especialidad
    ).scalar()

    nueva_consulta = ConsultaModel(
        **consulta_in.model_dump(exclude={"documento"}),
        expediente=paciente.expediente,
        documento=documento,
        orden=ultimo_orden + 1
    )

    db.add(nueva_consulta)
    db.commit()
    db.refresh(nueva_consulta)

    return nueva_consulta


# =============================================================================
# ACTUALIZAR CONSULTA
# =============================================================================
@router.patch("/{consulta_id}", response_model=ConsultaOut)
def actualizar_consulta(
    consulta_id: int,
    update_data: ConsultaUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    consulta = db.get(ConsultaModel, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    datos = update_data.model_dump(exclude_unset=True)
    for key, value in datos.items():
        setattr(consulta, key, value)

    db.commit()
    db.refresh(consulta)
    return consulta


# =============================================================================
# ELIMINAR CONSULTA
# =============================================================================
@router.delete("/{consulta_id}", status_code=204)
def eliminar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    consulta = db.get(ConsultaModel, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    db.delete(consulta)
    db.commit()
    return None