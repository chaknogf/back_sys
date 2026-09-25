# modules/ciclos/service.py
from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from core.config import APP_TIMEZONE

from modules.ciclos.models import CiclosConsulta
from modules.consultas.models import ConsultaModel
from modules.users.models import UserModel
from modules.ciclos.schemas import CicloConsulta, CicloConsultaBase, CicloOut


def obtener_ciclos_por_consulta(
    consulta_id: int,
    activo: Optional[bool] = True,
    db: Session = None,
):
    query = db.query(CiclosConsulta).filter(
        CiclosConsulta.consulta_id == consulta_id
    )

    if activo is not None:
        query = query.filter(CiclosConsulta.activo.is_(activo))

    ciclos = query.order_by(CiclosConsulta.numero.asc()).all()

    return ciclos


def obtener_ciclo(ciclo_id: int, db: Session):
    ciclo = (
        db.query(CiclosConsulta)
        .options(joinedload(CiclosConsulta.consulta))
        .filter(CiclosConsulta.id == ciclo_id)
        .first()
    )

    if not ciclo:
        raise HTTPException(status_code=404, detail="Ciclo no encontrado")

    # Nombre legible de quien registró la nota (el campo usuario guarda el username).
    ciclo.usuario_nombre = db.query(UserModel.nombre).filter(
        UserModel.username == ciclo.usuario
    ).scalar()

    return ciclo


def crear_ciclo(data: CicloConsultaBase, db: Session, current_user):
    consulta = db.get(ConsultaModel, data.consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    ultimo_numero = (
        db.query(func.coalesce(func.max(CiclosConsulta.numero), 0))
        .filter(CiclosConsulta.consulta_id == data.consulta_id)
        .scalar()
    ) or 0

    nuevo_numero = ultimo_numero + 1

    nuevo = CiclosConsulta(
        consulta_id=data.consulta_id,
        numero=nuevo_numero,
        activo=True,
        registro=datetime.now(APP_TIMEZONE),
        usuario=current_user.username,
        especialidad=data.especialidad,
        especialidad_id=data.especialidad_id,
        servicio=data.servicio,
        contenido=data.contenido,
        datos_medicos=data.datos_medicos
    )

    db.add(nuevo)

    try:
        db.commit()
        db.refresh(nuevo)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear ciclo: {str(e)}"
        )

    return nuevo


def _extraer_resumen(datos_medicos: dict | None) -> str | None:
    """Extrae un resumen legible de datos_medicos."""
    if not datos_medicos:
        return None
    odontologia = datos_medicos.get('odontologia')
    if isinstance(odontologia, dict):
        for campo in ['diagnostico', 'motivo_consulta', 'plan_tratamiento', 'procedimientos']:
            val = odontologia.get(campo)
            if val and isinstance(val, str) and val.strip():
                return val.strip()[:200]
    for campo in ['impresion_clinica', 'detalle_clinicos', 'tratamiento', 'contenido']:
        val = datos_medicos.get(campo)
        if val and isinstance(val, str) and len(val.strip()) > 0:
            return val.strip()[:200]
    return None


def _extraer_odontologia(datos_medicos: dict | None, especialidad: str | None = None) -> dict | None:
    """Devuelve campos odontológicos útiles para la historia clínica resumida."""
    nombre_especialidad = (especialidad or '').upper()
    es_odontologia = nombre_especialidad == 'ODON' or 'ODONTO' in nombre_especialidad
    if not datos_medicos and not es_odontologia:
        return None
    datos_medicos = datos_medicos or {}
    odontologia = datos_medicos.get('odontologia')
    if not isinstance(odontologia, dict):
        if not es_odontologia:
            return None
        odontologia = {
            'motivo_consulta': datos_medicos.get('detalle_clinicos'),
            'diagnostico': datos_medicos.get('impresion_clinica'),
            'plan_tratamiento': datos_medicos.get('tratamiento'),
            'procedimientos': datos_medicos.get('ordenes'),
        }

    odontograma = odontologia.get('odontograma') or {}
    dientes = odontograma.get('dientes') if isinstance(odontograma, dict) else {}
    piezas_afectadas = []
    if isinstance(dientes, dict):
        for numero, pieza in dientes.items():
            if isinstance(pieza, dict) and (pieza.get('estado') or pieza.get('superficies')):
                piezas_afectadas.append(str(numero))

    return {
        'motivo_consulta': odontologia.get('motivo_consulta'),
        'diagnostico': odontologia.get('diagnostico'),
        'plan_tratamiento': odontologia.get('plan_tratamiento'),
        'procedimientos': odontologia.get('procedimientos'),
        'piezas_afectadas': piezas_afectadas,
    }


def _extraer_signos_vitales(datos_medicos: dict | None) -> dict | None:
    """Extrae signos vitales compactos de datos_medicos."""
    if not datos_medicos:
        return None
    sv = datos_medicos.get('signos_vitales')
    if not sv or not isinstance(sv, dict):
        return None
    resultado = {}
    for campo, label in [('pa', 'PA'), ('fc', 'FC'), ('fr', 'FR'),
                          ('sat02', 'SatO2'), ('temp', 'Temp'), ('peso', 'Peso')]:
        val = sv.get(campo)
        if val and str(val).strip():
            resultado[label] = str(val).strip()
    return resultado if resultado else None


def obtener_historia_clinica(paciente_id: int, db: Session):
    """Obtiene la historia clínica completa de un paciente, agrupada por consulta."""
    from modules.pacientes.models import PacienteModel

    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Obtener todas las consultas del paciente
    consultas = (
        db.query(ConsultaModel)
        .filter(ConsultaModel.paciente_id == paciente_id)
        .order_by(ConsultaModel.fecha_consulta.desc())
        .all()
    )

    if not consultas:
        return {
            "paciente_id": paciente_id,
            "paciente_nombre": paciente.nombre_completo,
            "paciente_expediente": paciente.expediente,
            "consultas": [],
            "total_consultas": 0,
            "total_ciclos": 0,
        }

    consulta_ids = [c.id for c in consultas]

    # Obtener todos los ciclos de todas las consultas en una sola query
    ciclos = (
        db.query(CiclosConsulta)
        .filter(CiclosConsulta.consulta_id.in_(consulta_ids))
        .order_by(CiclosConsulta.consulta_id.asc(), CiclosConsulta.numero.asc())
        .all()
    )

    # Obtener nombres de usuarios
    usuario_ids = list(set(c.usuario for c in ciclos if c.usuario))
    usuarios_map = {}
    if usuario_ids:
        usuarios = db.query(UserModel.username, UserModel.nombre).filter(
            UserModel.username.in_(usuario_ids)
        ).all()
        usuarios_map = {u.username: u.nombre for u in usuarios}

    # Agrupar ciclos por consulta_id
    ciclos_por_consulta: dict[int, list] = {}
    for ciclo in ciclos:
        ciclos_por_consulta.setdefault(ciclo.consulta_id, []).append(ciclo)

    # Construir respuesta agrupada
    consultas_agrupadas = []
    total_ciclos = 0

    for consulta in consultas:
        ciclos_consulta = ciclos_por_consulta.get(consulta.id, [])
        ciclos_resumen = []
        for c in ciclos_consulta:
            dm = c.datos_medicos if isinstance(c.datos_medicos, dict) else {}
            ciclos_resumen.append({
                "id": c.id,
                "numero": c.numero,
                "registro": c.registro,
                "usuario": c.usuario,
                "usuario_nombre": usuarios_map.get(c.usuario),
                "especialidad": c.especialidad,
                "servicio": c.servicio,
                "resumen": _extraer_resumen(dm),
                "signos_vitales": _extraer_signos_vitales(dm),
                "impresion_clinica": dm.get("impresion_clinica"),
                "egreso": dm.get("egreso"),
                "odontologia": _extraer_odontologia(dm, c.especialidad or consulta.especialidad),
            })

        consultas_agrupadas.append({
            "consulta": {
                "id": consulta.id,
                "paciente": None,
                "tipo_consulta": consulta.tipo_consulta,
                "especialidad": consulta.especialidad,
                "fecha_consulta": consulta.fecha_consulta,
                "hora_consulta": consulta.hora_consulta,
                "ultimo_estado": consulta.ultimo_estado,
            },
            "ciclos": ciclos_resumen,
            "total_ciclos": len(ciclos_resumen),
        })
        total_ciclos += len(ciclos_resumen)

    return {
        "paciente_id": paciente_id,
        "paciente_nombre": paciente.nombre_completo,
        "paciente_expediente": paciente.expediente,
        "consultas": consultas_agrupadas,
        "total_consultas": len(consultas_agrupadas),
        "total_ciclos": total_ciclos,
    }
