# app/routes/merge_paciente.py
"""
Router de MERGE_PACIENTE: Fusiona múltiples registros de pacientes en uno solo.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List
from datetime import datetime, timezone

from app.database.db import get_db
from app.models.pacientes import PacienteModel
from app.database.security import get_current_user
from app.models.user import UserModel


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
    
    # Marcar metadatos como modificado
    flag_modified(paciente, "metadatos")


def merge_telefonos(principal, duplicado):
    """
    Fusiona teléfonos de contacto manejando tanto strings como arrays.
    Elimina duplicados y mantiene el orden.
    """
    tel_pri = (principal.contacto or {}).get("telefonos", [])
    tel_dup = (duplicado.contacto or {}).get("telefonos", [])

    # Normalizar a listas (puede venir como string o array)
    if isinstance(tel_pri, str):
        tel_pri = [tel_pri] if tel_pri.strip() else []
    elif tel_pri is None:
        tel_pri = []
    
    if isinstance(tel_dup, str):
        tel_dup = [tel_dup] if tel_dup.strip() else []
    elif tel_dup is None:
        tel_dup = []

    # Asegurar que sean listas
    if not isinstance(tel_pri, list):
        tel_pri = []
    if not isinstance(tel_dup, list):
        tel_dup = []

    # Limpiar: eliminar None, vacíos y normalizar espacios
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

    # Si no hay teléfonos del duplicado, no hacer nada
    if not tel_dup:
        return

    # Combinar y eliminar duplicados manteniendo el orden
    telefonos_finales = list(dict.fromkeys(tel_pri + tel_dup))

    # Asegurar que contacto existe
    if principal.contacto is None:
        principal.contacto = {}

    # Guardar como array
    principal.contacto["telefonos"] = telefonos_finales
    
    # Marcar el campo JSONB como modificado
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
        
        # Si el duplicado tiene valor
        if valor_dup is not None:
            # Si el principal no tiene valor, asignar directamente
            if valor_principal is None:
                setattr(principal, campo, valor_dup)
            # Si tienen valores diferentes, guardar el del duplicado como alternativo
            elif valor_principal != valor_dup:
                # Inicializar lista si no existe
                if campo not in campos_alternativos:
                    campos_alternativos[campo] = []
                
                # Agregar solo el valor
                campos_alternativos[campo].append(str(valor_dup))
    
    # Guardar campos alternativos en datos_extra
    if campos_alternativos:
        if principal.datos_extra is None:
            principal.datos_extra = {}
        
        if "merge" not in principal.datos_extra:
            principal.datos_extra["merge"] = {}
        
        # Combinar con valores existentes evitando duplicados
        for campo, valores in campos_alternativos.items():
            if campo not in principal.datos_extra["merge"]:
                principal.datos_extra["merge"][campo] = []
            
            # Evitar duplicados
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
    
    # Crear un set de referencias existentes para comparación rápida
    # Usamos (nombre_normalizado, parentesco) como clave única
    refs_existentes = set()
    for ref in referencias_actuales:
        nombre = ref.get("nombre", "").strip().upper()
        parentesco = ref.get("parentesco", "").strip().lower()
        refs_existentes.add((nombre, parentesco))
    
    # Agregar solo referencias nuevas
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
    # Validar que principal_id esté en la lista
    if principal_id not in ids:
        raise HTTPException(
            status_code=400,
            detail="El ID del paciente principal debe estar incluido en la lista de IDs"
        )
    
    # Obtener pacientes
    pacientes = (
        db.query(PacienteModel)
        .filter(PacienteModel.id.in_(ids))
        .all()
    )

    # Validar que se encontraron todos los pacientes
    if len(pacientes) != len(ids):
        ids_encontrados = {p.id for p in pacientes}
        ids_faltantes = set(ids) - ids_encontrados
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron los siguientes IDs: {list(ids_faltantes)}"
        )

    # Validar mínimo de pacientes
    if len(pacientes) < 2:
        raise HTTPException(
            status_code=400,
            detail="Se requieren al menos dos pacientes válidos para fusionar",
        )

    # Identificar paciente principal
    principal = next((p for p in pacientes if p.id == principal_id), None)

    if not principal:
        raise HTTPException(
            status_code=400,
            detail="El paciente principal no está en la lista de pacientes encontrados"
        )

    # Obtener duplicados
    duplicados = [p for p in pacientes if p.id != principal_id]

    try:
        for dup in duplicados:
            # Validar que el duplicado no esté ya inactivo
            if dup.estado == "I":
                raise HTTPException(
                    status_code=400,
                    detail=f"El paciente ID {dup.id} ya está marcado como inactivo"
                )

            # MERGE TELÉFONOS
            merge_telefonos(principal, dup)

            # MERGE CAMPOS CON CONSTRAINT UNIQUE (cui, expediente, pasaporte)
            campos_alt = merge_campos_unicos(principal, dup, db)

            # MERGE OTROS CAMPOS SIMPLES
            for campo in ["sexo", "fecha_nacimiento"]:
                valor_principal = getattr(principal, campo, None)
                valor_dup = getattr(dup, campo, None)

                if valor_principal is None and valor_dup is not None:
                    setattr(principal, campo, valor_dup)

            # MERGE datos_extra (combinar diccionarios)
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

            # MERGE REFERENCIAS (evitar duplicados)
            merge_referencias(principal, dup)

            # REASIGNAR RELACIONES (consultas)
            if hasattr(dup, 'consultas'):
                for consulta in dup.consultas:
                    consulta.paciente_id = principal.id

            # LIMPIAR CAMPOS UNIQUE DEL DUPLICADO
            dup.cui = None
            dup.expediente = None
            dup.pasaporte = None

            # MARCAR DUPLICADO COMO INACTIVO
            dup.estado = "I"

            # AGREGAR EVENTO AL DUPLICADO
            agregar_evento(
                dup,
                usuario=current_user.username,
                accion="MERGE_PACIENTE",
                expediente_duplicado=True,
                detalle=f"Fusionado en paciente principal ID {principal.id}",
            )

            # AGREGAR EVENTO AL PRINCIPAL
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

        # Commit de todos los cambios
        db.commit()
        db.refresh(principal)

        return {
            "paciente_principal": principal.id,
            "pacientes_fusionados": [p.id for p in duplicados],
            "total_fusionados": len(duplicados),
            "campos_alternativos": principal.datos_extra.get("campos_alternativos_merge", {}) if principal.datos_extra else {},
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