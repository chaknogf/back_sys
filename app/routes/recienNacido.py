# app/routes/recienNacido.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from app.database.db import get_db
from app.models.pacientes import PacienteModel
from app.schemas.paciente import PacienteOut, PacienteCreateDerivado, Nombre
from app.database.security import get_current_user
from app.models.user import UserModel
from app.routes.pacientes import agregar_evento
from app.utils.expediente import generar_expediente

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


def calcular_edad(fecha_nacimiento: date) -> int:
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


def construir_datos_extra_derivados(madre: PacienteModel) -> dict:
    datos_extra = {}

    # Heredar datos demográficos de la madre
    madre_demo = (madre.datos_extra or {}).get("demografico", {})
    demografico = {
        k: madre_demo[k]
        for k in ("pueblo", "idioma", "nacionalidad")
        if madre_demo.get(k)
    }
    if demografico:
        datos_extra["demografico"] = demografico

    # Obtener identificador de la madre (prioridad: CUI > Pasaporte > PersonaID)
    idpersona_madre = None
    if madre.cui:
        idpersona_madre = str(madre.cui)
    elif madre.pasaporte:
        idpersona_madre = madre.pasaporte
    elif madre.datos_extra:
        persona_id = madre.datos_extra.get("personaid")
        if persona_id:
            idpersona_madre = str(persona_id)

    # Obtener teléfono de contacto de la madre
    telefono_madre = None
    if madre.contacto and isinstance(madre.contacto, dict):
        telefono_madre = madre.contacto.get("telefonos")

    # Crear referencia a la madre como responsable
    datos_extra["referencias"] = [{
        "nombre": madre.nombre_completo,
        "parentesco": "MADRE",
        "telefono": telefono_madre,
        "expediente": madre.expediente,
        "idpersona": idpersona_madre,
        "responsable": True
    }]

    return datos_extra


@router.post("/madre-hijo/{madre_id}", response_model=PacienteOut, status_code=201)
def crear_paciente_desde_madre(
    madre_id: int,
    payload: PacienteCreateDerivado,
    db: Session = Depends(get_db),
    auto_expediente: bool = Query(
        True,
        description="Generar expediente automáticamente"
    ),
    current_user: UserModel = Depends(get_current_user)
):
    madre = db.get(PacienteModel, madre_id)
    if not madre:
        raise HTTPException(404, "Madre no encontrada")

    if madre.sexo != "F" or not madre.fecha_nacimiento:
        raise HTTPException(400, "Paciente no elegible como madre")

    if calcular_edad(madre.fecha_nacimiento) < 12:
        raise HTTPException(400, "Paciente no elegible como madre")

    # Construir datos extra heredados de la madre (incluye referencias)
    datos_extra = construir_datos_extra_derivados(madre)
    
    # Agregar información de origen
    datos_extra["origen"] = {
        "tipo": "MADRE",
        "paciente_id": madre.id,
        "expediente": madre.expediente
    }

    # Agregar datos neonatales del payload
    if payload.datos_extra:
        datos_extra["neonatales"] = payload.datos_extra.model_dump()

    # Generar expediente automáticamente si se solicita
    expediente = generar_expediente(db) if auto_expediente else None

    # Extraer nombre de la madre de forma segura
    nombre_madre = madre.nombre or {}

    # Construir nombre del hijo/a usando Pydantic para validación
    nombre_hijo = Nombre(
        primer_nombre="HIJA" if payload.sexo == "F" else "HIJO",
        segundo_nombre=nombre_madre.get("primer_nombre"),
        otro_nombre=" ".join(
            filter(None, [
                nombre_madre.get("segundo_nombre"),
                nombre_madre.get("otro_nombre")
            ])
        ) or None,
        primer_apellido=nombre_madre.get("primer_apellido") or "PENDIENTE",
        segundo_apellido=nombre_madre.get("segundo_apellido"),
        apellido_casada=nombre_madre.get("apellido_casada"),
    )

    # Crear el nuevo paciente
    nuevo = PacienteModel(
        nombre=nombre_hijo.model_dump(),
        sexo=payload.sexo,
        fecha_nacimiento=payload.fecha_nacimiento,
        contacto=madre.contacto,
        expediente=expediente,
        datos_extra=datos_extra,
        estado=payload.estado,
    )

    # Evento de creación
    agregar_evento(
        nuevo,
        usuario=current_user.username,
        accion="CREADO"
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo