from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.expediente.service import generar_expediente, generar_constancia_nacimiento
from modules.constancias_nacimiento.models import ConstanciaNacimientoModel
from .models import PacienteModel
from .schemas import PacienteOut, PacienteCreateDerivado, Nombre, Referencia
from .service import agregar_evento

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


def calcular_edad(fecha_nacimiento: date) -> int:
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


def construir_datos_extra_derivados(madre: PacienteModel) -> dict:
    madre_extra = madre.datos_extra or {}
    madre_demo = madre_extra.get("demografico", {})

    idpersona_madre = None
    if madre.cui:
        idpersona_madre = str(madre.cui)
    elif madre.pasaporte:
        idpersona_madre = madre.pasaporte
    else:
        persona_id = madre_extra.get("personaid")
        if persona_id:
            idpersona_madre = str(persona_id)

    demograficos = {
        "idioma": madre_demo.get("idioma"),
        "pueblo": madre_demo.get("pueblo"),
        "vecindad": "0406",
        "nacionalidad": "GTM",
        "lugar_nacimiento": "0406"
    }

    demograficos = {k: v for k, v in demograficos.items() if v is not None}

    datos_extra = {
        "idpersona_madre": madre.id,
        "demograficos": demograficos
    }

    return datos_extra


@router.post("/madre-hijo/{madre_id}", response_model=PacienteOut, status_code=201)
def crear_paciente_desde_madre(
    madre_id: int,
    payload: PacienteCreateDerivado,
    db: Session = Depends(get_db),
    auto_expediente: bool = Query(True, description="Generar expediente automáticamente"),
    current_user: UserModel = Depends(get_current_user)
):
    madre = db.get(PacienteModel, madre_id)
    if not madre:
        raise HTTPException(404, "Madre no encontrada")

    if madre.sexo != "F" or not madre.fecha_nacimiento:
        raise HTTPException(400, "Paciente no elegible como madre")

    if calcular_edad(madre.fecha_nacimiento) < 12:
        raise HTTPException(400, "Paciente no elegible como madre")

    datos_extra = construir_datos_extra_derivados(madre)
    datos_extra["origen"] = {
        "tipo": "MADRE",
        "paciente_id": madre.id,
        "expediente": madre.expediente
    }

    if payload.datos_extra:
        datos_extra["neonatales"] = payload.datos_extra.model_dump()

    expediente = generar_expediente(db) if auto_expediente else None

    nombre_madre = madre.nombre or {}
    if not isinstance(nombre_madre, dict):
        nombre_madre = {}

    nombre_hijo = Nombre(
        primer_nombre="Hija de" if payload.sexo == "F" else "Hijo de",
        segundo_nombre=nombre_madre.get("primer_nombre"),
        otro_nombre=" ".join(
            filter(None, [nombre_madre.get("segundo_nombre"), nombre_madre.get("otro_nombre")])
        ) or None,
        primer_apellido=nombre_madre.get("primer_apellido") or "PENDIENTE",
        segundo_apellido=nombre_madre.get("segundo_apellido"),
        apellido_casada=nombre_madre.get("apellido_casada"),
    )

    referencia_hijo = Referencia(
        nombre=madre.nombre_completo,
        parentesco="Madre",
        telefono=madre.contacto.get("telefonos") if madre.contacto else None,
        expediente=madre.expediente,
        idpersona=str(madre.cui) if madre.cui else (
            madre.pasaporte or ((madre.datos_extra or {}).get("personaid"))
        ),
        responsable=True
    )

    nuevo = PacienteModel(
        nombre=nombre_hijo.model_dump(),
        sexo=payload.sexo,
        fecha_nacimiento=payload.fecha_nacimiento,
        contacto=madre.contacto,
        expediente=expediente,
        datos_extra=datos_extra,
        estado=payload.estado,
        referencias=[referencia_hijo.model_dump()]
    )

    agregar_evento(nuevo, usuario=current_user.username, accion="CREADO")

    db.add(nuevo)
    db.flush()

    nombre_madre_str = madre.nombre_completo or " ".join(filter(None, [
        nombre_madre.get("primer_nombre"),
        nombre_madre.get("segundo_nombre"),
        nombre_madre.get("primer_apellido"),
        nombre_madre.get("segundo_apellido"),
    ]))

    madre_demo = (madre.datos_extra or {}).get("demografico", {})
    vecindad_madre = madre_demo.get("vecindad") or madre_demo.get("municipio")

    constancia = ConstanciaNacimientoModel(
        paciente_id=nuevo.id,
        madre_id=madre.id,
        registrador_id=current_user.id,
        documento=generar_constancia_nacimiento(db),
        nombre_madre=nombre_madre_str,
        vecindad_madre=str(vecindad_madre) if vecindad_madre else None,
    )

    db.add(constancia)
    db.commit()
    db.refresh(nuevo)

    return nuevo
