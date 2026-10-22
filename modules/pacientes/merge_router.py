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
from .service import agregar_evento


router = APIRouter(prefix="/pacientes", tags=["merge_paciente"])


_VALORES_BASURA = {"nan", "null", "none", "undefined", "n/a", "na", "0"}


def _es_vacio(valor) -> bool:
    """Determina si un valor debe considerarse 'vacío' para el merge.

    Además de None y cadena vacía, trata como vacío la basura típica de
    importaciones: 'nan', 'null', 'N/A', el string '0', y el 0 numérico.
    No toca valores legítimos (p. ej. 0.0 de coordenadas no existen aquí)."""
    if valor is None:
        return True
    if isinstance(valor, str):
        return valor.strip().lower() in _VALORES_BASURA or valor.strip() == ""
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return valor == 0
    return False



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
                if t_str and not _es_vacio(t_str):
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


def merge_campos_unicos(principal, duplicado, db: Session, valores_dup: dict | None = None):
    """
    Maneja el merge de campos con constraint UNIQUE.
    Si el duplicado tiene un valor y el principal no, lo asigna.
    Si ambos tienen valores diferentes, o si el valor ya existe en otro paciente,
    los guarda en datos_extra del principal.

    `valores_dup` permite pasar un snapshot de los valores del duplicado cuando
    estos ya fueron liberados en el objeto (cui/expediente/pasaporte = None) para
    evitar la violación del UNIQUE durante la transacción.
    """
    campos_unicos = ["cui", "expediente", "pasaporte"]
    campos_alternativos = {}

    for campo in campos_unicos:
        valor_principal = getattr(principal, campo, None)
        if valores_dup is not None and campo in valores_dup:
            valor_dup = valores_dup[campo]
        else:
            valor_dup = getattr(duplicado, campo, None)

        if not _es_vacio(valor_dup):
            if _es_vacio(valor_principal):
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

        # El CUI del registro NO principal se guarda en datos_extra.personaid.
        # Si hay varios CUIs alternos, se agregan al final separados por espacio.
        cuis_alternos = campos_alternativos.get("cui", [])
        if cuis_alternos:
            existentes = str(principal.datos_extra.get("personaid") or "").split()
            for valor in cuis_alternos:
                v = str(valor)
                if v not in existentes:
                    existentes.append(v)
            principal.datos_extra["personaid"] = " ".join(existentes)

        if "merge" not in principal.datos_extra:
            principal.datos_extra["merge"] = {}

        for campo, valores in campos_alternativos.items():
            if campo == "cui":
                continue
            if campo not in principal.datos_extra["merge"]:
                principal.datos_extra["merge"][campo] = []

            for valor in valores:
                if valor not in principal.datos_extra["merge"][campo]:
                    principal.datos_extra["merge"][campo].append(valor)

        flag_modified(principal, "datos_extra")

    return campos_alternativos


def merge_nombre(principal, duplicado):
    """Rellena componentes del nombre del principal que estén vacíos con los del duplicado."""
    from sqlalchemy.orm.attributes import flag_modified

    p_nom = principal.nombre or {}
    d_nom = duplicado.nombre or {}
    cambiado = False
    for key, value in (d_nom or {}).items():
        if (p_nom.get(key) is None or str(p_nom.get(key)).strip() == "") and value not in (None, ""):
            p_nom[key] = value
            cambiado = True
    if cambiado:
        principal.nombre = p_nom
        flag_modified(principal, "nombre")


def merge_contacto(principal, duplicado):
    """Fusiona el contacto: combina teléfonos, completa los campos vacíos o con
    basura del principal con los del duplicado y, si ambos tienen valor, conserva
    el más completo (evita pisar un dato bueno con uno truncado/basura)."""
    merge_telefonos(principal, duplicado)

    c_pri = principal.contacto or {}
    c_dup = duplicado.contacto or {}
    cambiado = False

    for key, value in c_dup.items():
        if key == "telefonos":
            continue
        valor_pri = c_pri.get(key)
        if _es_vacio(valor_pri) and not _es_vacio(value):
            c_pri[key] = value
            cambiado = True
        elif (
            not _es_vacio(valor_pri)
            and not _es_vacio(value)
            and isinstance(valor_pri, str)
            and isinstance(value, str)
            and len(value.strip()) > len(valor_pri.strip())
        ):
            # Ambos con valor: preferir el más completo (más largo).
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
        "pasaporte",
    ]
    for campo in campos:
        valor_pri = getattr(principal, campo, None)
        valor_dup = getattr(duplicado, campo, None)
        if _es_vacio(valor_pri) and not _es_vacio(valor_dup):
            setattr(principal, campo, valor_dup)

    # Metadatos: conservar auditoría del duplicado también
    if duplicado.metadatos:
        if principal.metadatos is None:
            principal.metadatos = []
        existentes = {m.get("registro") for m in principal.metadatos if isinstance(m, dict)}
        for m in duplicado.metadatos:
            if isinstance(m, dict) and m.get("registro") not in existentes:
                principal.metadatos.append(m)
                existentes.add(m.get("registro"))
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(principal, "metadatos")


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
            if _es_vacio(valor_pri) and not _es_vacio(value):
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


def merge_expedientes_anteriores(principal, duplicado):
    """Conserva los expedientes de los duplicados en el principal como lista
    de expedientes anteriores (sin duplicados)."""
    from sqlalchemy.orm.attributes import flag_modified

    exp_dup = duplicado.expediente
    if not exp_dup:
        return
    exp_pri = principal.expediente
    if exp_dup == exp_pri:
        return

    if principal.datos_extra is None:
        principal.datos_extra = {}
    lista = principal.datos_extra.get("expedientes_anteriores")
    if not isinstance(lista, list):
        lista = []
    if exp_dup not in lista:
        lista.append(exp_dup)
    principal.datos_extra["expedientes_anteriores"] = lista
    flag_modified(principal, "datos_extra")


def merge_referencias(principal, duplicado):
    """
    Fusiona las referencias evitando duplicados por nombre y parentesco.
    Si el duplicado trae una referencia con el mismo nombre+parentesco que ya
    existe, completa sus campos vacíos (teléfono, idpersona, expediente, etc.)
    en vez de descartarla por completo.
    """
    if not duplicado.referencias:
        return

    referencias_actuales = principal.referencias or []

    def _clave(ref: dict):
        return (
            (ref.get("nombre") or "").strip().upper(),
            (ref.get("parentesco") or "").strip().lower(),
        )

    por_clave = {_clave(ref): ref for ref in referencias_actuales}

    for ref_dup in duplicado.referencias:
        clave = _clave(ref_dup)
        existente = por_clave.get(clave)
        if existente is None:
            referencias_actuales.append(ref_dup)
            por_clave[clave] = ref_dup
        else:
            # Completar campos vacíos / basura de la referencia existente.
            for k, v in ref_dup.items():
                if _es_vacio(existente.get(k)) and not _es_vacio(v):
                    existente[k] = v

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

            merge_nombre(principal, dup)
            merge_contacto(principal, dup)

            # Capturar los valores únicos del duplicado ANTES de liberarlos, para
            # poder copiarlos al principal luego sin violar el UNIQUE.
            valores_dup = {
                "cui": dup.cui,
                "expediente": dup.expediente,
                "pasaporte": dup.pasaporte,
            }

            # Liberar el UNIQUE del duplicado PRIMERO y persistirlo (flush), para
            # que al copiar su cui/expediente/pasaporte al principal no se viole el
            # constraint por tener el mismo valor en dos filas dentro de la txn.
            # Se conserva el CUI original como referencia (personaid).
            if dup.cui is not None:
                if dup.datos_extra is None:
                    dup.datos_extra = {}
                if "personaid" not in dup.datos_extra:
                    dup.datos_extra["personaid"] = str(dup.cui)
                flag_modified(dup, "datos_extra")

            dup.cui = None
            dup.expediente = None
            dup.pasaporte = None
            db.flush()

            # Copiar campos únicos (cui/expediente/pasaporte) del duplicado al
            # principal si le faltan; si el principal ya tiene valor, el del
            # duplicado queda como alternativa en datos_extra.merge.
            campos_alt = merge_campos_unicos(principal, dup, db, valores_dup)

            _fill_campos_vacios(principal, dup)

            merge_datos_extra(principal, dup)

            merge_referencias(principal, dup)
            merge_expedientes_anteriores(principal, dup)

            if hasattr(dup, 'consultas'):
                for consulta in dup.consultas:
                    consulta.paciente_id = principal.id

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

        # Todos los duplicados se consolidan en una sola transacción para evitar fusiones parciales.
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
