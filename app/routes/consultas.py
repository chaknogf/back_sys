# app/routes/consultas.py
"""
Router de consultas médicas - Búsqueda avanzada, creación inteligente y CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text
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


# =============================================================================
# BÚSQUEDA AVANZADA EN VISTA MATERIALIZADA (ULTRARRÁPIDA)
# =============================================================================


@router.get("/", response_model=List[ConsultaOut])
def buscar_consultas(
    paciente_id: Optional[int] = None,
    cui: Optional[str] = None,
    fecha: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    query = db.query(ConsultaModel).join(PacienteModel)

    if paciente_id:
        query = query.filter(ConsultaModel.paciente_id == paciente_id)
    if cui:
        query = query.filter(PacienteModel.cui == cui)
    if fecha:
        query = query.filter(ConsultaModel.fecha_consulta == fecha)

    resultados = query.all()
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
    consulta = db.query(ConsultaModel).filter(ConsultaModel.id == consulta_id).first()
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
    # Verificar paciente
    paciente = db.get(PacienteModel, consulta_in.paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Generar expediente si no tiene
    if not paciente.expediente:
        paciente.expediente = generar_expediente(db)
        db.add(paciente)
        db.flush()

    # Generar número de emergencia si aplica
    documento = consulta_in.documento
    if consulta_in.tipo_consulta == 3:  # Emergencia
        documento = generar_emergencia(db)

    # Calcular orden
    ultimo_orden = db.query(func.coalesce(func.max(ConsultaModel.orden), 0)).filter(
        ConsultaModel.fecha_consulta == consulta_in.fecha_consulta,
        ConsultaModel.tipo_consulta == consulta_in.tipo_consulta,
        ConsultaModel.especialidad == consulta_in.especialidad
    ).scalar()

    nueva_consulta = ConsultaModel(
        **consulta_in.model_dump(exclude={"documento"}),
        expediente=paciente.expediente,
        documento=documento or consulta_in.documento,
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