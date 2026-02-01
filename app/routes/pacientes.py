# app/routes/pacientes.py
"""
Router de pacientes - CORREGIDO
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, cast, String, text, or_
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import date, datetime, time, timezone
from app.database.db import get_db
from app.models.consultas import ConsultaModel
from app.models.pacientes import PacienteModel
from app.schemas.paciente import (
    
    PacienteCreate, PacienteOut, PacienteUpdate, PacienteSimple, PacienteListResponse, MetadataEvento, PacientesConConsultas
) 
from app.utils.expediente import generar_expediente
from app.database.security import get_current_user
from app.models.user import UserModel


router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

def agregar_evento(
    paciente,
    usuario,
    accion,
    expediente_duplicado: bool | None = None,
    detalle: str = ""
):
    evento = {
        "usuario": usuario or "sistema",
        "registro": datetime.now(timezone.utc).isoformat(),
        "accion": accion,
        "expediente_duplicado": expediente_duplicado,
        "detalle": detalle
    }

    if paciente.metadatos is None:
        paciente.metadatos = []

    paciente.metadatos.append(evento)
    
def normalizar_metadatos(paciente):
    if not paciente.metadatos:
        return

    for m in paciente.metadatos:
        if not m.get("accion"):
            m["accion"] = "ACTUALIZADO"
        if not m.get("usuario"):
            m["usuario"] = "sistema"
        if m.get("registro") and not isinstance(m["registro"], str):
            m["registro"] = m["registro"].isoformat()

# =============================================================================
# BÚSQUEDA AVANZADA - CORREGIDA
# =============================================================================
@router.get("/", response_model=PacienteListResponse)
def buscar_pacientes(
    q: Optional[str] = Query(None, description="Búsqueda libre"),
    id: Optional[int] = Query(None),
    cui: Optional[str] = Query(None),
    expediente: Optional[str] = Query(None),
    nombre: Optional[str] = Query(None),
    sexo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),  # CAMBIO: era "A" por defecto, ahora None
    fecha_nac: Optional[str] = Query(None, description="YYYY-MM-DD"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Búsqueda de pacientes con filtros opcionales
    Si no se envían filtros, devuelve todos los pacientes (paginados)
    """
    
    # Empezar con query base
    query = db.query(PacienteModel).order_by(desc(PacienteModel.id))
    
    # Filtro por defecto: excluir inactivos
    query = query.filter(PacienteModel.estado != "I")
    # Solo aplicar filtros si se proporcionan
    if q:
        q_clean = q.strip().upper()
        query = query.filter(
            or_(
                # Búsqueda en CUI
                cast(PacienteModel.cui, String).ilike(f"%{q_clean}%"),
                # Búsqueda en expediente
                PacienteModel.expediente.ilike(f"%{q_clean}%"),
                # Búsqueda en nombre_completo (columna calculada)
                PacienteModel.nombre_completo.ilike(f"%{q_clean}%"),
                # O búsqueda en JSONB de nombre
                func.jsonb_extract_path_text(PacienteModel.nombre, 'primer_nombre').ilike(f"%{q_clean}%"),
                func.jsonb_extract_path_text(PacienteModel.nombre, 'segundo_nombre').ilike(f"%{q_clean}%"),
                func.jsonb_extract_path_text(PacienteModel.nombre, 'otro_nombre').ilike(f"%{q_clean}%"),
                func.jsonb_extract_path_text(PacienteModel.nombre, 'primer_apellido').ilike(f"%{q_clean}%"),
                func.jsonb_extract_path_text(PacienteModel.nombre, 'segundo_apellido').ilike(f"%{q_clean}%"),
                func.jsonb_extract_path_text(PacienteModel.nombre, 'apellido_casada').ilike(f"%{q_clean}%")
            )
        )

    if cui:
        if cui.isdigit():
            query = query.filter(PacienteModel.cui == int(cui))
        else:
            # Si no es numérico, buscar como string
            query = query.filter(cast(PacienteModel.cui, String).ilike(f"%{cui}%"))

    if expediente:
        query = query.filter(PacienteModel.expediente.ilike(f"%{expediente}%"))

    if nombre:
        nombre_clean = nombre.strip().upper()
        query = query.filter(
            or_(
                PacienteModel.nombre_completo.ilike(f"%{nombre_clean}%"),
                func.jsonb_extract_path_text(PacienteModel.nombre, 'primer_nombre').ilike(f"%{nombre_clean}%"),
                func.jsonb_extract_path_text(PacienteModel.nombre, 'segundo_nombre').ilike(f"%{nombre_clean}%"),
                func.jsonb_extract_path_text(PacienteModel.nombre, 'primer_apellido').ilike(f"%{nombre_clean}%"),
                func.jsonb_extract_path_text(PacienteModel.nombre, 'segundo_apellido').ilike(f"%{nombre_clean}%")
            )
        )
    if id:
        query = query.filter(PacienteModel.id == id)
    if sexo:
        query = query.filter(PacienteModel.sexo == sexo.upper())

    if estado:
        query = query.filter(PacienteModel.estado == estado.upper())

    if fecha_nac:
        try:
            query = query.filter(PacienteModel.fecha_nacimiento == fecha_nac)
        except:
            pass  # Ignorar si el formato es inválido

    # Contar total ANTES de paginar
    total = query.count()
    
    # Aplicar paginación
    pacientes = query.offset(skip).limit(limit).all()

    for p in pacientes:
        if p.metadatos:
            for m in p.metadatos:
                if not m.get("accion"):
                    m["accion"] = "ACTUALIZADO"
                if not m.get("usuario"):
                    m["usuario"] = "sistema"

    return PacienteListResponse(
        total=total,
        pacientes=pacientes
    )


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
        raise HTTPException(
            status_code=404,
            detail=f"Paciente con ID {paciente_id} no encontrado"
        )

    # 🔧 NORMALIZACIÓN DEFENSIVA
    if paciente.metadatos:
        for m in paciente.metadatos:
            if not m.get("accion"):
                m["accion"] = "ACTUALIZADO"
            if not m.get("usuario"):
                m["usuario"] = "sistema"
            if isinstance(m.get("registro"), str) is False:
                m["registro"] = str(m["registro"])

    return paciente


# =============================================================================
# CREAR PACIENTE
# =============================================================================
@router.post("/", response_model=PacienteOut, status_code=201)
def crear_paciente(
    paciente_in: PacienteCreate,
    auto_expediente: bool = Query(False, description="Generar expediente automáticamente"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Crear nuevo paciente
    Si auto_expediente=True y no se proporciona expediente, se genera automáticamente
    """

    data = paciente_in.model_dump()

    # Limpiar campos vacíos
    for field in ("cui", "expediente", "pasaporte"):
        if not data.get(field) or str(data.get(field)).strip() == "":
            data[field] = None

    # Generar expediente si se solicita
    if auto_expediente and not data.get("expediente"):
        data["expediente"] = generar_expediente(db)

    try:
        nuevo = PacienteModel(**data)

        # 🔹 evento CREADO (antes del commit, pero ya existe la entidad)
        agregar_evento(
            nuevo,
            usuario=current_user.username,
            accion="CREADO"
        )

        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo

    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()

        if "cui" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un paciente con el CUI: {data.get('cui')}"
            )
        elif "expediente" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un paciente con el expediente: {data.get('expediente')}"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Datos duplicados o inválidos"
            )


# =============================================================================
# ACTUALIZAR PACIENTE (OPTIMIZADO)
# =============================================================================

@router.patch("/{paciente_id}", response_model=PacienteOut | dict)
def gestionar_paciente(
    paciente_id: int,
    paciente_update: Optional[PacienteUpdate] = None,
    accion: str = Query(
        default="mantener",
        regex="^(mantener|generar|sobrescribir|activar|desactivar)$",
        description="Acción a ejecutar sobre el paciente"
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(
            status_code=404,
            detail=f"Paciente con ID {paciente_id} no encontrado"
        )

    # ============================================================
    # 🟢 ACTIVAR
    # ============================================================
    if accion == "activar":
        if paciente.estado == "A":
            raise HTTPException(
                status_code=400,
                detail="El paciente ya está activo"
            )

        paciente.estado = "A"
        agregar_evento(
            paciente,
            usuario=current_user.username,
            accion="ACTIVADO"
        )
        db.commit()
        db.refresh(paciente)

        return {
            "message": "Paciente activado exitosamente",
            "paciente_id": paciente_id,
            "estado": paciente.estado
        }

    # ============================================================
    # 🔴 DESACTIVAR
    # ============================================================
    if accion == "desactivar":
        if paciente.estado == "I":
            raise HTTPException(
                status_code=400,
                detail="El paciente ya está inactivo"
            )

        paciente.estado = "I"
        agregar_evento(
            paciente,
            usuario=current_user.username,
            accion="DESACTIVADO"
        )
        db.commit()
        db.refresh(paciente)

        return {
            "message": "Paciente desactivado exitosamente",
            "paciente_id": paciente_id,
            "estado": paciente.estado
        }

    # ============================================================
    # ✏️ ACTUALIZAR (mantener | generar | sobrescribir)
    # ============================================================
    if not paciente_update:
        raise HTTPException(
            status_code=400,
            detail="Se requieren datos para actualizar el paciente"
        )

    try:
        datos_update = paciente_update.model_dump(exclude_unset=True)

        expediente_anterior = paciente.expediente
        expediente_generado = False

        if accion == "generar":
            if not paciente.expediente or paciente.expediente.strip() == "":
                datos_update["expediente"] = generar_expediente(db)
                expediente_generado = True
            else:
                datos_update.pop("expediente", None)

        elif accion == "sobrescribir":
            datos_update["expediente"] = generar_expediente(db)
            expediente_generado = True

        elif accion == "mantener":
            datos_update.pop("expediente", None)

        datos_update.pop("metadatos", None)

        for key, value in datos_update.items():
            setattr(paciente, key, value)

        agregar_evento(
            paciente,
            usuario=current_user.username,
            accion="ACTUALIZADO",
            expediente_duplicado=(
                expediente_generado and expediente_anterior is not None
            )
        )

        db.commit()
        db.refresh(paciente)
        normalizar_metadatos(paciente)
        return paciente

    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()

        if "cui" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un paciente con ese CUI"
            )
        elif "expediente" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un paciente con ese expediente"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Datos duplicados o inválidos"
            )

@router.delete("/{paciente_id}/eliminar-permanente", status_code=204)
def eliminar_paciente_permanente(
    paciente_id: int,
    confirmacion: str = Query(..., description="Escribe 'CONFIRMAR' para eliminar permanentemente"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    ⚠️ ELIMINACIÓN FÍSICA PERMANENTE ⚠️
    
    ÚLTIMO RECURSO: Elimina el registro completamente de la base de datos.
    Esta acción NO SE PUEDE DESHACER.
    
    - Solo administradores pueden usar este endpoint
    - Requiere confirmación explícita escribiendo 'CONFIRMAR'
    - Se pierde toda la información del paciente
    """
    
    # Solo admin puede eliminar físicamente
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Solo administradores pueden eliminar permanentemente"
        )
    
    # Validar confirmación
    if confirmacion != "CONFIRMAR":
        raise HTTPException(
            status_code=400,
            detail="Debe escribir 'CONFIRMAR' para eliminar permanentemente"
        )

    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(
            status_code=404, 
            detail=f"Paciente con ID {paciente_id} no encontrado"
        )

    # Eliminación física
    db.delete(paciente)
    db.commit()
    
    return None


# =============================================================================
# ENDPOINT DE DEBUG (QUITAR EN PRODUCCIÓN)
# =============================================================================
@router.get("/debug/count")
def debug_count(db: Session = Depends(get_db)):
    """Endpoint temporal para verificar cuántos pacientes hay"""
    total = db.query(PacienteModel).count()
    activos = db.query(PacienteModel).filter(PacienteModel.estado == "A").count()
    inactivos = db.query(PacienteModel).filter(PacienteModel.estado == "I").count()
    
    # Obtener algunos ejemplos
    ejemplos = db.query(PacienteModel).limit(3).all()
    
    return {
        "total": total,
        "activos": activos,
        "inactivos": inactivos,
        "ejemplos": [
            {
                "id": p.id,
                "expediente": p.expediente,
                "cui": p.cui,
                "nombre_completo": p.nombre_completo,
                "estado": p.estado
            }
            for p in ejemplos
        ]
    }
    

