from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime, timezone

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.audit_log.service import registrar_acceso
from modules.expediente.service import generar_expediente
from .models import PacienteModel
from .schemas import (
    PacienteCreate, PacienteOut, PacienteUpdate, PacienteContacto,
    PacienteListResponse
)
from .service import buscar_pacientes, buscar_neonatales, buscar_personal_hospital, obtener_paciente, crear_paciente, agregar_evento, normalizar_metadatos


router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.get("/", response_model=PacienteListResponse)
def buscar_pacientes_endpoint(
    q: Optional[str] = Query(None, description="Búsqueda libre"),
    id: Optional[int] = Query(None),
    cui: Optional[str] = Query(None),
    expediente: Optional[str] = Query(None),
    nombre: Optional[str] = Query(None),
    primer_nombre: Optional[str] = Query(None),
    segundo_nombre: Optional[str] = Query(None),
    primer_apellido: Optional[str] = Query(None),
    segundo_apellido: Optional[str] = Query(None),
    sexo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    fecha_nac: Optional[str] = Query(None, description="YYYY-MM-DD"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    filters = {k: v for k, v in {
        "q": q, "id": id, "cui": cui, "expediente": expediente,
        "nombre": nombre, "primer_nombre": primer_nombre,
        "segundo_nombre": segundo_nombre, "primer_apellido": primer_apellido,
        "segundo_apellido": segundo_apellido, "sexo": sexo, "estado": estado,
        "fecha_nac": fecha_nac
    }.items() if v is not None}
    resultado = buscar_pacientes(db, filters, skip, limit)
    registrar_acceso(db, current_user.username, "pacientes", "/pacientes/")
    return resultado


@router.get("/neonatales", response_model=PacienteListResponse)
def listar_neonatales(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    id_paciente: Optional[int] = Query(None),
    expediente: Optional[str] = Query(None),
    expediente_madre: Optional[str] = Query(None),
    fecha_nacimiento: Optional[str] = Query(None, description="YYYY-MM-DD"),
    nombre: Optional[str] = Query(None),
    sexo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
):
    filters = {k: v for k, v in {
        "id_paciente": id_paciente, "expediente": expediente,
        "expediente_madre": expediente_madre,
        "fecha_nacimiento": fecha_nacimiento, "nombre": nombre,
        "sexo": sexo, "estado": estado,
    }.items() if v is not None}
    resultado = buscar_neonatales(db, filters, skip, limit)
    registrar_acceso(db, current_user.username, "pacientes", "/pacientes/neonatales")
    return resultado


@router.get("/personal-hospital", response_model=PacienteListResponse)
def listar_personal_hospital(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    resultado = buscar_personal_hospital(db, skip, limit)
    registrar_acceso(db, current_user.username, "pacientes", "/pacientes/personal-hospital")
    return resultado


@router.get("/{paciente_id}", response_model=PacienteOut)
def obtener_paciente_endpoint(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    resultado = obtener_paciente(db, paciente_id)
    registrar_acceso(db, current_user.username, "pacientes", f"/pacientes/{paciente_id}", registro_id=paciente_id)
    return resultado


@router.post("/", response_model=PacienteOut, status_code=201)
def crear_paciente_endpoint(
    paciente_in: PacienteCreate,
    auto_expediente: bool = Query(False, description="Generar expediente automáticamente"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return crear_paciente(db, paciente_in, auto_expediente, current_user.username)


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
        raise HTTPException(status_code=404, detail=f"Paciente con ID {paciente_id} no encontrado")

    if accion == "activar":
        if paciente.estado == "A":
            raise HTTPException(status_code=400, detail="El paciente ya está activo")
        paciente.estado = "A"
        agregar_evento(paciente, usuario=current_user.username, accion="ACTIVADO")
        db.commit()
        db.refresh(paciente)
        return {"message": "Paciente activado exitosamente", "paciente_id": paciente_id, "estado": paciente.estado}

    if accion == "desactivar":
        if paciente.estado == "I":
            raise HTTPException(status_code=400, detail="El paciente ya está inactivo")
        paciente.estado = "I"
        agregar_evento(paciente, usuario=current_user.username, accion="DESACTIVADO")
        db.commit()
        db.refresh(paciente)
        return {"message": "Paciente desactivado exitosamente", "paciente_id": paciente_id, "estado": paciente.estado}

    if not paciente_update:
        raise HTTPException(status_code=400, detail="Se requieren datos para actualizar el paciente")

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
            expediente_duplicado=(expediente_generado and expediente_anterior is not None)
        )

        db.commit()
        db.refresh(paciente)
        normalizar_metadatos(paciente)
        return paciente

    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        if "cui" in error_msg:
            raise HTTPException(status_code=400, detail="Ya existe un paciente con ese CUI")
        elif "expediente" in error_msg:
            raise HTTPException(status_code=400, detail="Ya existe un paciente con ese expediente")
        else:
            raise HTTPException(status_code=400, detail="Datos duplicados o inválidos")


@router.delete("/{paciente_id}/eliminar-permanente", status_code=204)
def eliminar_paciente_permanente(
    paciente_id: int,
    confirmacion: str = Query(..., description="Escribe 'CONFIRMAR' para eliminar permanentemente"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar permanentemente")
    if confirmacion != "CONFIRMAR":
        raise HTTPException(status_code=400, detail="Debe escribir 'CONFIRMAR' para eliminar permanentemente")

    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail=f"Paciente con ID {paciente_id} no encontrado")

    db.delete(paciente)
    db.commit()
    return None


@router.get("/debug/count")
def debug_count(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    total = db.query(PacienteModel).count()
    activos = db.query(PacienteModel).filter(PacienteModel.estado == "A").count()
    inactivos = db.query(PacienteModel).filter(PacienteModel.estado == "I").count()
    ejemplos = db.query(PacienteModel).limit(3).all()
    registrar_acceso(db, current_user.username, "pacientes", "/pacientes/debug/count")
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


@router.get("/expediente/{expediente}", response_model=PacienteContacto)
def expediente_endpoint(
    expediente: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    paciente = db.query(PacienteModel).filter(
        PacienteModel.expediente == expediente
    ).first()

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    registrar_acceso(db, current_user.username, "pacientes", f"/pacientes/expediente/{expediente}", registro_id=paciente.id)
    return paciente
