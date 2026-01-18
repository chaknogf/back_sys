# app/routes/pacientes.py
"""
Router de pacientes - CORREGIDO
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, cast, String, text, or_
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
# BÚSQUEDA AVANZADA - CORREGIDA
# =============================================================================
@router.get("/", response_model=PacienteListResponse)
def buscar_pacientes(
    q: Optional[str] = Query(None, description="Búsqueda libre"),
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

    return PacienteListResponse(
        total=total,
        pacientes=pacientes
    )


# =============================================================================
# AUTOCOMPLETE - CORREGIDO
# =============================================================================
@router.get("/buscar", response_model=List[PacienteSimple])
def autocomplete(
    q: str = Query(..., min_length=1),  # CAMBIO: min_length=1 en lugar de 3
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Búsqueda rápida para autocomplete
    Busca en CUI, expediente y nombre completo
    """
    q_clean = q.strip().upper()
    
    # Construir query
    resultados = db.query(PacienteModel).filter(
        or_(
            cast(PacienteModel.cui, String).ilike(f"%{q_clean}%"),
            PacienteModel.expediente.ilike(f"%{q_clean}%"),
            PacienteModel.nombre_completo.ilike(f"%{q_clean}%")
        )
    ).limit(15).all()

    return [
        PacienteSimple(
            id=p.id,
            cui=p.cui,
            expediente=p.expediente,
            nombre_completo=p.nombre_completo or "",
            fecha_nacimiento=p.fecha_nacimiento
        )
        for p in resultados
    ]


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

    # Limpiar campos vacíos (convertir "" a None)
    for field in ["cui", "expediente", "pasaporte"]:
        if data.get(field) in ["", " ", None]:
            data[field] = None

    # Generar expediente si se solicita y no existe
    if auto_expediente and not data.get("expediente"):
        data["expediente"] = generar_expediente(db)

    try:
        nuevo = PacienteModel(**data)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        
        # Mensajes de error más específicos
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
# OBTENER PACIENTE POR ID
# =============================================================================
@router.get("/{paciente_id}", response_model=PacienteOut)
def obtener_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Obtener un paciente específico por ID"""
    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(
            status_code=404, 
            detail=f"Paciente con ID {paciente_id} no encontrado"
        )
    return paciente


# =============================================================================
# ACTUALIZAR PACIENTE
# =============================================================================
# =============================================================================
# ACTUALIZAR PACIENTE (OPTIMIZADO)
# =============================================================================

@router.patch("/{paciente_id}", response_model=PacienteOut)
def actualizar_paciente(
    paciente_id: int,
    paciente_update: PacienteUpdate,
    accion_expediente: str = Query(
        default="mantener",
        regex="^(mantener|generar|sobrescribir)$",
        description="'mantener': no modifica expediente | 'generar': genera si no existe | 'sobrescribir': genera nuevo"
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Actualizar datos de un paciente existente con control de expediente.
    
    **Acciones de expediente:**
    - `mantener` (default): No modifica el expediente actual
    - `generar`: Genera expediente solo si el paciente no tiene uno
    - `sobrescribir`: Genera un nuevo expediente (sobrescribe el existente)
    
    **Ejemplos:**
    ```
    PATCH /pacientes/123
    PATCH /pacientes/123?accion_expediente=generar
    PATCH /pacientes/123?accion_expediente=sobrescribir
    ```
    """
    
    # Obtener paciente
    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(
            status_code=404,
            detail=f"Paciente con ID {paciente_id} no encontrado"
        )

    try:
        # Obtener solo los datos que fueron enviados (exclude_unset=True)
        datos_update = paciente_update.model_dump(exclude_unset=True)

        # 🔧 MANEJO DE EXPEDIENTE
        if accion_expediente == "generar":
            # Generar SOLO si no tiene expediente
            if not paciente.expediente or paciente.expediente.strip() == "":
                datos_update["expediente"] = generar_expediente(db)
            # Si ya tiene, remover del update para mantenerlo
            elif "expediente" in datos_update:
                del datos_update["expediente"]

        elif accion_expediente == "sobrescribir":
            # Generar SIEMPRE un nuevo expediente
            datos_update["expediente"] = generar_expediente(db)

        # elif accion_expediente == "mantener":
        #   No hacer nada - comportamiento por defecto

        # 🔄 Aplicar cambios al paciente
        for key, value in datos_update.items():
            setattr(paciente, key, value)

        # 💾 Guardar cambios
        db.commit()
        db.refresh(paciente)
        
        return paciente

    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()

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
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar paciente"
        )
# =============================================================================
# ELIMINAR PACIENTE
# =============================================================================
@router.delete("/{paciente_id}", status_code=204)
def eliminar_paciente(
    paciente_id: int,
    fisico: bool = Query(False, description="True=eliminación física, False=lógica"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Eliminar un paciente
    - fisico=False: Eliminación lógica (cambia estado a 'I')
    - fisico=True: Eliminación física (borra el registro)
    """
    
    # Solo admin puede eliminar físicamente
    if fisico and current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Solo administradores pueden eliminar físicamente"
        )

    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(
            status_code=404, 
            detail=f"Paciente con ID {paciente_id} no encontrado"
        )

    if fisico:
        # Eliminación física
        db.delete(paciente)
    else:
        # Eliminación lógica
        paciente.estado = "I"

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