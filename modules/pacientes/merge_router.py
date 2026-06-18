"""
Router de MERGE_PACIENTE: Fusiona múltiples registros de pacientes en uno solo.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List
from datetime import datetime, timezone

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from .models import PacienteModel


router = APIRouter(prefix="/pacientes", tags=["merge_paciente"])


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
        "detalle": detalle,
    }

    if paciente.metadatos is None:
        paciente.metadatos = []

    paciente.metadatos.append(evento)

    flag_modified(paciente, "metadatos")


def merge_telefonos(principal, duplicado):
    """
    Fusiona teléfonos de contacto manejando tanto strings como arrays.
    Elimina duplicados y mantiene el orden.
    """
    tel_pri = (principal.contacto or {}).get("telefonos", [])
    tel_dup = (duplicado.contacto or {}).get("telefonos", [])

    if isinstance(tel_pri, str):
        tel_pri = [tel_pri] if tel_pri.strip() else []
    elif tel_pri is None:
        tel_pri = []

    if isinstance(tel_dup, str):
        tel_dup = [tel_dup] if tel_dup.strip() else []
    elif tel_dup is None:
        tel_dup = []

    if not isinstance(tel_pri, list):
        tel_pri = []
    if not isinstance(tel_dup, list):
        tel_dup = []

    def limpiar(lista):
        limpia = []
        for t in lista:
            if t is not None:
                t_str = str(t).strip()
                if t_str and t_str != "":
                    limpia.append(t_str)
        return limpia

    tel_pri = limpiar(tel_pri)
    tel_dup = limpiar(tel_dup)

    if not tel_dup:
        return

    telefonos_finales = list(dict.fromkeys(tel_pri + tel_dup))

    if principal.contacto is None:
        principal.contacto = {}

    principal.contacto["telefonos"] = telefonos_finales

    flag_modified(principal, "contacto")


def merge_campos_unicos(principal, duplicado, db: Session):
    """
    Maneja el merge de campos con constraint UNIQUE.
    Si el duplicado tiene un valor y el principal no, lo asigna.
    Si ambos tienen valores diferentes, los guarda en datos_extra del principal.
    """
    campos_unicos = ["cui", "expediente", "pasaporte"]
    campos_alternativos = {}

    for campo in campos_unicos:
        valor_principal = getattr(principal, campo, None)
        valor_dup = getattr(duplicado, campo, None)

        if valor_dup is not None:
            if valor_principal is None:
                setattr(principal, campo, valor_dup)
            elif valor_principal != valor_dup:
                if campo not in campos_alternativos:
                    campos_alternativos[campo] = []

                campos_alternativos[campo].append(str(valor_dup))

    if campos_alternativos:
        if principal.datos_extra is None:
            principal.datos_extra = {}

        if "merge" not in principal.datos_extra:
            principal.datos_extra["merge"] = {}

        for campo, valores in campos_alternativos.items():
            if campo not in principal.datos_extra["merge"]:
                principal.datos_extra["merge"][campo] = []

            for valor in valores:
                if valor not in principal.datos_extra["merge"][campo]:
                    principal.datos_extra["merge"][campo].append(valor)

        flag_modified(principal, "datos_extra")

    return campos_alternativos


def merge_referencias(principal, duplicado):
    """
    Fusiona las referencias evitando duplicados por nombre y parentesco.
    """
    if not duplicado.referencias:
        return

    referencias_actuales = principal.referencias or []

    refs_existentes = set()
    for ref in referencias_actuales:
        nombre = ref.get("nombre", "").strip().upper()
        parentesco = ref.get("parentesco", "").strip().lower()
        refs_existentes.add((nombre, parentesco))

    for ref_dup in duplicado.referencias:
        nombre = ref_dup.get("nombre", "").strip().upper()
        parentesco = ref_dup.get("parentesco", "").strip().lower()

        if (nombre, parentesco) not in refs_existentes:
            referencias_actuales.append(ref_dup)
            refs_existentes.add((nombre, parentesco))

    principal.referencias = referencias_actuales
    flag_modified(principal, "referencias")


@router.post("/merge", status_code=200)
def merge_pacientes(
    principal_id: int = Query(..., description="ID del paciente principal"),
    ids: List[int] = Query(..., min_items=2, description="IDs de pacientes a fusionar"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    ids_unicos = list(set(ids))
    if principal_id not in ids_unicos:
        raise HTTPException(
            status_code=400,
            detail="El ID del paciente principal debe estar incluido en la lista de IDs"
        )

    pacientes = (
        db.query(PacienteModel)
        .filter(PacienteModel.id.in_(ids_unicos))
        .all()
    )

    if len(pacientes) != len(ids_unicos):
        ids_encontrados = {p.id for p in pacientes}
        ids_faltantes = set(ids_unicos) - ids_encontrados
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron los siguientes IDs: {list(ids_faltantes)}"
        )

    if len(pacientes) < 2:
        raise HTTPException(
            status_code=400,
            detail="Se requieren al menos dos pacientes válidos para fusionar",
        )

    principal = next((p for p in pacientes if p.id == principal_id), None)

    if not principal:
        raise HTTPException(
            status_code=400,
            detail="El paciente principal no está en la lista de pacientes encontrados"
        )

    duplicados = [p for p in pacientes if p.id != principal_id]

    try:
        for dup in duplicados:
            if dup.estado == "I":
                raise HTTPException(
                    status_code=400,
                    detail=f"El paciente ID {dup.id} ya está marcado como inactivo"
                )

            merge_telefonos(principal, dup)

            campos_alt = merge_campos_unicos(principal, dup, db)

            for campo in ["sexo", "fecha_nacimiento"]:
                valor_principal = getattr(principal, campo, None)
                valor_dup = getattr(dup, campo, None)

                if valor_principal is None and valor_dup is not None:
                    setattr(principal, campo, valor_dup)

            if dup.datos_extra:
                if principal.datos_extra is None:
                    principal.datos_extra = {}

                for key, value in dup.datos_extra.items():
                    if key not in principal.datos_extra:
                        principal.datos_extra[key] = value
                    elif key == "campos_alternativos_merge":
                        if "campos_alternativos_merge" not in principal.datos_extra:
                            principal.datos_extra["campos_alternativos_merge"] = {}
                        principal.datos_extra["campos_alternativos_merge"].update(value)

                flag_modified(principal, "datos_extra")

            merge_referencias(principal, dup)

            if hasattr(dup, 'consultas'):
                for consulta in dup.consultas:
                    consulta.paciente_id = principal.id

            dup.cui = None
            dup.expediente = None
            dup.pasaporte = None

            dup.estado = "I"

            agregar_evento(
                dup,
                usuario=current_user.username,
                accion="MERGE_PACIENTE",
                expediente_duplicado=True,
                detalle=f"Fusionado en paciente principal ID {principal.id}",
            )

            detalle_base = f"Fusionado paciente ID {dup.id} en este registro"
            if campos_alt:
                detalle_base += f". Campos alternativos guardados: {', '.join(campos_alt.keys())}"

            agregar_evento(
                principal,
                usuario=current_user.username,
                accion="MERGE_PACIENTE",
                expediente_duplicado=False,
                detalle=detalle_base,
            )

        db.commit()
        db.refresh(principal)

        return {
            "paciente_principal": principal.id,
            "pacientes_fusionados": [p.id for p in duplicados],
            "total_fusionados": len(duplicados),
            "campos_alternativos": principal.datos_extra.get("merge", {}) if principal.datos_extra else {},
            "telefonos_fusionados": principal.contacto.get("telefonos", []) if principal.contacto else [],
            "referencias_totales": len(principal.referencias) if principal.referencias else 0,
            "estado": "merge_completado",
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error durante el merge: {str(e)}"
        )
