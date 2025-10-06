from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import String, desc, cast, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text
from typing import Optional, List
from app.database.db import SessionLocal
from app.models.pacientes import PacienteModel
from app.schemas.paciente import PacienteBase, PacienteCreate, PacienteOut, PacienteUpdate
from fastapi.security import OAuth2PasswordBearer
from app.utils.expediente import generar_expediente

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
@router.get("/pacientes/", response_model=List[PacienteUpdate], tags=["pacientes"])
async def get_pacientes(
    id: Optional[int] = Query(None),
    identificador: Optional[str] = Query(None),
    primer_nombre: Optional[str] = Query(None),
    segundo_nombre: Optional[str] = Query(None),
    primer_apellido: Optional[str] = Query(None),
    segundo_apellido: Optional[str] = Query(None),
    nombre_completo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    fecha_nacimiento: Optional[str] = Query(None),
    fecha_defuncion: Optional[str] = Query(None),
    sexo: Optional[str] = Query(None),
    referencia: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    🔍 Endpoint para obtener pacientes filtrados dinámicamente.
    Admite múltiples parámetros opcionales para búsqueda flexible.
    """
    try:
        query = db.query(PacienteModel).order_by(desc(PacienteModel.id))

        # --- Filtros básicos ---
        if id:
            query = query.filter(PacienteModel.id == id)

        if identificador:
            query = query.filter(
                (PacienteModel.cui.cast(String).ilike(f"%{identificador}%")) |
                (PacienteModel.expediente.ilike(f"%{identificador}%")) |
                (PacienteModel.pasaporte.ilike(f"%{identificador}%")) |
                (PacienteModel.otro_id.ilike(f"%{identificador}%"))
            )

        # --- Filtros por nombre ---
        nombre_filtros = {
            "primer_nombre": primer_nombre,
            "segundo_nombre": segundo_nombre,
            "primer_apellido": primer_apellido,
            "segundo_apellido": segundo_apellido
        }

        for campo, valor in nombre_filtros.items():
            if valor:
                query = query.filter(
                    func.unaccent(PacienteModel.nombre[campo].astext).ilike(
                        func.unaccent(f"%{valor}%")
                    )
                )

        # --- Filtro por referencia (JSONB) ---
        if referencia:
            query = query.filter(
                text("""
                    EXISTS (
                        SELECT 1 FROM jsonb_each_text(pacientes.referencias) AS ref
                        WHERE ref.value::jsonb->>'nombre' ILIKE :referencia
                    )
                """)
            ).params(referencia=f"%{referencia}%")

        # --- Otros filtros ---
        if estado:
            query = query.filter(PacienteModel.estado == estado)

        if sexo:
            query = query.filter(PacienteModel.sexo == sexo)

        # --- Filtros por fechas ---
        if fecha_nacimiento:
            try:
                fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
                query = query.filter(PacienteModel.fecha_nacimiento == fecha_nac)
            except ValueError:
                raise HTTPException(status_code=422, detail="Formato de fecha_nacimiento inválido (use YYYY-MM-DD)")

        if fecha_defuncion and hasattr(PacienteModel, "fecha_defuncion"):
            try:
                fecha_def = datetime.strptime(fecha_defuncion, "%Y-%m-%d").date()
                query = query.filter(PacienteModel.fecha_defuncion == fecha_def)
            except ValueError:
                raise HTTPException(status_code=422, detail="Formato de fecha_defuncion inválido (use YYYY-MM-DD)")

        # --- Ejecución final con paginación ---
        pacientes = query.offset(skip).limit(limit).all()

        return JSONResponse(status_code=200, content=jsonable_encoder(pacientes))

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Error al consultar pacientes",
                "type": type(e).__name__,
                "msg": str(e),
                "args": e.args,
                "orig": str(getattr(e, "orig", None)),
                "diag": str(getattr(e, "diag", None)),
                "params": str(getattr(e, "params", None))
            }
        )  


@router.post("/paciente/crear/", response_model=PacienteOut, status_code=201, tags=["pacientes"])
async def create_paciente(
    paciente: PacienteCreate,
    generar_expediente: bool = Query(
        default=False, 
        description="Si es True, genera expediente automáticamente. Si es False, usa el expediente del payload o deja vacío."
    ),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Crea un nuevo paciente.

    Parámetros:
    - **generar_expediente**: 
        - `true`: Genera expediente automáticamente (ignora el expediente en el payload)
        - `false`: Usa el expediente proporcionado o lo deja vacío
    """
    try:
        paciente_data = paciente.model_dump()

        # Normalizar campos vacíos
        paciente_data["cui"] = paciente_data.get("cui") or None
        paciente_data["expediente"] = paciente_data.get("expediente") or None

        # Generar expediente automáticamente si se solicita
        if generar_expediente:
            paciente_data["expediente"] = generar_numero_expediente(db)

        # Validar duplicados solo si hay valor
        if paciente_data.get("cui"):
            exists_cui = db.query(PacienteModel).filter(PacienteModel.cui == paciente_data["cui"]).first()
            if exists_cui:
                raise HTTPException(status_code=400, detail="Ya existe un paciente con ese CUI")

        if paciente_data.get("expediente"):
            exists_expediente = db.query(PacienteModel).filter(PacienteModel.expediente == paciente_data["expediente"]).first()
            if exists_expediente:
                raise HTTPException(status_code=400, detail="Ya existe un paciente con ese expediente")

        # Crear paciente
        new_paciente = PacienteModel(**paciente_data)
        db.add(new_paciente)
        db.commit()
        db.refresh(new_paciente)

        return new_paciente

    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()
        # if 'unique' in error_msg or 'duplicate' in error_msg:
        #     detail = "Ya existe un paciente con ese CUI o expediente"
        if 'foreign key' in error_msg:
            detail = "Referencia inválida a otra tabla"
        elif 'not null' in error_msg:
            detail = "Faltan campos requeridos"
        else:
            detail = "Error de integridad de datos"
        raise HTTPException(status_code=400, detail=detail)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear paciente")
        
@router.put("/paciente/actualizar/{paciente_id}", response_model=PacienteOut, tags=["pacientes"])
async def update_paciente(
    paciente_id: int,
    paciente: PacienteUpdate,
    accion_expediente: Optional[str] = Query(
        default="mantener",
        regex="^(mantener|generar|sobrescribir)$",
        description="Acción sobre el expediente: 'mantener' (no tocar), 'generar' (solo si no tiene), 'sobrescribir' (forzar nuevo)"
    ),
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Actualiza un paciente existente con opciones de manejo de expediente.
    
    Parámetros de expediente (accion_expediente):
    - **mantener** (default): No modifica el expediente actual
    - **generar**: Genera expediente solo si el paciente no tiene uno
    - **sobrescribir**: Genera un nuevo expediente (sobrescribe el existente)
    
    Ejemplos:
    - `PUT /paciente/actualizar/123?accion_expediente=mantener` → No toca expediente
    - `PUT /paciente/actualizar/123?accion_expediente=generar` → Genera si no tiene
    - `PUT /paciente/actualizar/123?accion_expediente=sobrescribir` → Genera nuevo (sobrescribe)
    """
    try:
        db_paciente = db.query(PacienteModel).filter(
            PacienteModel.id == paciente_id
        ).first()
        
        if not db_paciente:
            raise HTTPException(
                status_code=404,
                detail="Paciente no encontrado"
            )

        # ✅ Obtener datos a actualizar (sin el expediente por ahora)
        update_data = paciente.model_dump(exclude_unset=True)
        
        # ✅ Manejar el expediente según la acción solicitada
        if accion_expediente == "generar":
            # Genera expediente SOLO si no tiene
            if not db_paciente.expediente or db_paciente.expediente.strip() == "":
                expediente_generado = generar_expediente(db)
                update_data["expediente"] = expediente_generado
            # Si ya tiene expediente, lo mantiene (no hace nada)
            elif "expediente" in update_data:
                # Remover el expediente del update_data para no sobrescribir
                del update_data["expediente"]
                
        elif accion_expediente == "sobrescribir":
            # Genera un nuevo expediente SIEMPRE (sobrescribe)
            expediente_generado = generar_expediente(db)
            update_data["expediente"] = expediente_generado
            
        elif accion_expediente == "mantener":
            # No toca el expediente actual
            # Si viene expediente en el payload, lo usa (permite update manual)
            pass  # Comportamiento por defecto
        
        # ✅ Aplicar todas las actualizaciones
        for key, value in update_data.items():
            setattr(db_paciente, key, value)

        db.commit()
        db.refresh(db_paciente)
        
        # ✅ Retornar el paciente actualizado completo
        return db_paciente
        
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()
        
        if 'unique' in error_msg or 'duplicate' in error_msg:
            detail = "Ya existe un paciente con ese CUI o expediente"
        else:
            detail = "Error de integridad de datos"
        
        raise HTTPException(status_code=400, detail=detail)
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar paciente"
        )

@router.delete("/paciente/eliminar/{paciente_id}", tags=["pacientes"])
async def delete_paciente(
    paciente_id: int,
    # token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
        db_paciente = db.query(PacienteModel).filter(PacienteModel.id == paciente_id).first()
        if not db_paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        db.delete(db_paciente)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Paciente eliminado exitosamente"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
