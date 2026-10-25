# modules/ciclos/service.py
"""Consultas y registro de ciclos, incluida la composición de historia clínica."""

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
    skip: int = 0,
    limit: int = 100,
):
    """Ordena por número y aplica el filtro de actividad cuando se especifica.

    Incluye la consulta (con su paciente) para que la vista de historia clínica
    pueda cargarse directamente desde el id de consulta, y resuelve el nombre
    legible de los autores en una sola query adicional."""
    query = (
        db.query(CiclosConsulta)
        .options(
            joinedload(CiclosConsulta.consulta).joinedload(ConsultaModel.paciente)
        )
        .filter(CiclosConsulta.consulta_id == consulta_id)
    )

    if activo is not None:
        query = query.filter(CiclosConsulta.activo.is_(activo))

    ciclos = query.order_by(CiclosConsulta.numero.asc()).offset(skip).limit(limit).all()
    from modules.quirofano.service import resolver_intervenciones_ciclos
    resolver_intervenciones_ciclos(ciclos, db)

    usuarios = {c.usuario for c in ciclos if c.usuario}
    if usuarios:
        nombres = dict(
            db.query(UserModel.username, UserModel.nombre)
            .filter(UserModel.username.in_(usuarios))
            .all()
        )
        for ciclo in ciclos:
            ciclo.usuario_nombre = nombres.get(ciclo.usuario)

    return ciclos


def _adjuntar_usuario_nombre(ciclo, db: Session):
    """Nombre legible de quien registró la nota (el campo usuario guarda el username)."""
    if ciclo is not None:
        ciclo.usuario_nombre = db.query(UserModel.nombre).filter(
            UserModel.username == ciclo.usuario
        ).scalar()
    return ciclo


def obtener_ciclo(ciclo_id: int, db: Session):
    ciclo = (
        db.query(CiclosConsulta)
        .options(joinedload(CiclosConsulta.consulta))
        .filter(CiclosConsulta.id == ciclo_id)
        .first()
    )

    if not ciclo:
        raise HTTPException(status_code=404, detail="Ciclo no encontrado")

    from modules.quirofano.service import resolver_intervenciones_ciclos
    resolver_intervenciones_ciclos([ciclo], db)

    return _adjuntar_usuario_nombre(ciclo, db)


def obtener_ultimo_ciclo_por_consulta(
    consulta_id: int,
    activo: Optional[bool] = True,
    db: Session = None,
):
    """Nota más reciente de una consulta, resuelta en una sola query.

    Ordena por fecha de registro (más reciente primero) con el id como
    desempate y limita a una fila; devuelve ``None`` si no hay notas activas."""
    query = (
        db.query(CiclosConsulta)
        .options(
            joinedload(CiclosConsulta.consulta).joinedload(ConsultaModel.paciente)
        )
        .filter(CiclosConsulta.consulta_id == consulta_id)
    )

    if activo is not None:
        query = query.filter(CiclosConsulta.activo.is_(activo))

    ciclo = (
        query.order_by(
            CiclosConsulta.registro.desc().nullslast(),
            CiclosConsulta.id.desc(),
        )
        .first()
    )

    if ciclo:
        from modules.quirofano.service import resolver_intervenciones_ciclos
        resolver_intervenciones_ciclos([ciclo], db)

    return _adjuntar_usuario_nombre(ciclo, db)


def crear_ciclo(data: CicloConsultaBase, db: Session, current_user):
    """Asigna el siguiente número y confirma el ciclo; la restricción única respalda la secuencia."""
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
        datos_medicos=data.datos_medicos,
        uisau=data.uisau,
        quirofano=data.quirofano
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


def obtener_ultimo_odontograma(paciente_id: int, db: Session):
    """Odontograma más reciente con piezas registradas para un paciente.

    Permite que una nueva nota odontológica continúe el registro anterior
    sin volver a capturarlo desde cero."""
    from modules.pacientes.models import PacienteModel

    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    consulta_ids = [
        fila[0]
        for fila in db.query(ConsultaModel.id)
        .filter(ConsultaModel.paciente_id == paciente_id)
        .all()
    ]
    if not consulta_ids:
        return None

    ciclos = (
        db.query(CiclosConsulta)
        .filter(CiclosConsulta.consulta_id.in_(consulta_ids))
        .order_by(CiclosConsulta.registro.desc().nullslast(), CiclosConsulta.id.desc())
        .all()
    )
    for ciclo in ciclos:
        datos_medicos = ciclo.datos_medicos
        if not isinstance(datos_medicos, dict):
            continue
        odontologia = datos_medicos.get('odontologia')
        if not isinstance(odontologia, dict):
            continue
        odontograma = odontologia.get('odontograma')
        if isinstance(odontograma, dict) and odontograma.get('dientes'):
            return odontograma

    return None


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


def obtener_historia_clinica(paciente_id: int, db: Session, skip: int = 0, limit: int = 50):
    """Obtiene una página de la historia clínica agrupada por consulta."""
    from modules.pacientes.models import PacienteModel

    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Obtener todas las consultas del paciente
    consulta_query = db.query(ConsultaModel).filter(ConsultaModel.paciente_id == paciente_id)
    total_consultas = consulta_query.count()
    consultas = (
        consulta_query
        .order_by(ConsultaModel.fecha_consulta.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    if not consultas:
        return {
            "paciente_id": paciente_id,
            "paciente_nombre": paciente.nombre_completo,
            "paciente_expediente": paciente.expediente,
            "consultas": [],
            "total_consultas": total_consultas,
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
    from modules.quirofano.service import resolver_intervenciones_ciclos
    resolver_intervenciones_ciclos(ciclos, db)

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
                "uisau": c.uisau if isinstance(c.uisau, dict) else None,
                "quirofano": c.quirofano if isinstance(c.quirofano, dict) else None,
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
        "total_consultas": total_consultas,
        "total_ciclos": total_ciclos,
    }
