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
    Si ambos tienen valores diferentes, o si el valor ya existe en otro paciente, los guarda en datos_extra del principal.
    """
    campos_unicos = ["cui", "expediente", "pasaporte"]
    campos_alternativos = {}

    for campo in campos_unicos:
        valor_principal = getattr(principal, campo, None)
        valor_dup = getattr(duplicado, campo, None)

        if valor_dup is not None:
            if valor_principal is None:
                ya_existe = db.query(PacienteModel).filter(
                    getattr(PacienteModel, campo) == valor_dup,
                    PacienteModel.id.notin_([principal.id, duplicado.id]),
                ).first()
                if ya_existe:
                    if campo not in campos_alternativos:
                        campos_alternativos[campo] = []
                    campos_alternativos[campo].append(str(valor_dup))
                else:
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


def merge_contacto(principal, duplicado):
    """Fusiona el contacto: combina teléfonos y rellena los demás campos vacíos."""
    merge_telefonos(principal, duplicado)

    c_pri = principal.contacto or {}
    c_dup = duplicado.contacto or {}
    cambiado = False

    for key, value in c_dup.items():
        if key == "telefonos":
            continue
        valor_pri = c_pri.get(key)
        if (valor_pri is None or valor_pri == "") and value not in (None, ""):
            c_pri[key] = value
            cambiado = True

    if cambiado:
        principal.contacto = c_pri
        flag_modified(principal, "contacto")


def _fill_campos_vacios(principal, duplicado):
    """Copia cualquier campo simple (no JSONB) del duplicado al principal
    si el principal lo tiene vacío."""
    campos = [
        "sexo", "fecha_nacimiento", "idioma_id", "pueblo_id", "nacionalidad",
        "lugar_nacimiento", "discapacidad", "educacion", "estado_civil",
        "es_estudiante_publico", "ocupacion", "es_personal_hospital",
    ]
    for campo in campos:
        valor_pri = getattr(principal, campo, None)
        valor_dup = getattr(duplicado, campo, None)
        if (valor_pri is None or valor_pri == "") and valor_dup not in (None, ""):
            setattr(principal, campo, valor_dup)


def _deep_fill(dest: dict, fuente: dict) -> bool:
    """Relleno profundo: copia de `fuente` los valores no vacíos en las claves de
    `dest` que estén vacías. Devuelve True si algo cambió."""
    cambiado = False
    for key, value in (fuente or {}).items():
        if isinstance(value, dict):
            if isinstance(dest.get(key), dict):
                if _deep_fill(dest[key], value):
                    cambiado = True
            else:
                # No existe el subobjeto: según size de value
                if value:
                    dest[key] = value
                    cambiado = True
        else:
            valor_pri = dest.get(key)
            if (valor_pri is None or valor_pri == "") and value not in (None, ""):
                dest[key] = value
                cambiado = True
    return cambiado


def merge_datos_extra(principal, duplicado):
    """Fusiona datos_extra: relleno profundo de los campos vacíos del principal
    con los valores del duplicado (socio-económicos, demográficos, etc.)."""
    if not duplicado.datos_extra:
        return

    p_extra = principal.datos_extra or {}
    d_extra = duplicado.datos_extra or {}

    cambiado = _deep_fill(p_extra, d_extra)

    # Preservar merge de colisiones previas
    if "campos_alternativos_merge" in d_extra:
        if "campos_alternativos_merge" not in p_extra:
            p_extra["campos_alternativos_merge"] = {}
        if isinstance(d_extra["campos_alternativos_merge"], dict):
            p_extra["campos_alternativos_merge"].update(d_extra["campos_alternativos_merge"])
            cambiado = True

    if cambiado:
        principal.datos_extra = p_extra
        flag_modified(principal, "datos_extra")


def merge_referencias(principal, duplicado):
    """
    Fusiona las referencias evitando duplicados por nombre y parentesco.
    """
    if not duplicado.referencias:
        return

    referencias_actuales = principal.referencias or []

    refs_existentes = set()
    for ref in referencias_actuales:
        nombre = (ref.get("nombre") or "").strip().upper()
        parentesco = (ref.get("parentesco") or "").strip().lower()
        refs_existentes.add((nombre, parentesco))

    for ref_dup in duplicado.referencias:
        nombre = (ref_dup.get("nombre") or "").strip().upper()
        parentesco = (ref_dup.get("parentesco") or "").strip().lower()

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

            if dup.cui is not None:
                if dup.datos_extra is None:
                    dup.datos_extra = {}
                if "personaid" not in dup.datos_extra:
                    dup.datos_extra["personaid"] = str(dup.cui)
                dup.cui = None
                flag_modified(dup, "datos_extra")

            merge_contacto(principal, dup)

            campos_alt = merge_campos_unicos(principal, dup, db)

            _fill_campos_vacios(principal, dup)

            merge_datos_extra(principal, dup)

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
