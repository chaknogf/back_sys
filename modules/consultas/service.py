# modules/consultas/service.py
from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import String, cast, desc, func, text, or_, and_, case
from sqlalchemy.orm.attributes import flag_modified
from typing import Optional, List
from datetime import datetime, date, time, timedelta

from modules.pacientes.models import PacienteModel
from modules.consultas.models import ConsultaModel
from modules.ciclos.models import CiclosConsulta
from modules.laboratorios.models import Laboratorios
from modules.rayos_x.models import RayosX
from modules.consultas.schemas import (
    CicloConsultaUpdate, ConsultaListado, ConsultaOut,
    ConsultaUpdate, ConsultaBusqueda, RegistroConsultaCreate, RegistroConsultaOut,
    Indicador, CicloClinico, Egreso, ConsultaHistoriaResumidaOut, ConsultaListResponse
)
from modules.expediente.service import generar_expediente, generar_emergencia


def _agregar_ciclo(consulta, nuevo_ciclo, current_user):
    nuevo_ciclo["registro"] = datetime.now().isoformat()
    nuevo_ciclo["usuario"] = current_user.username
    nuevo_ciclo.setdefault("estado", "actualizado")

    historial = consulta.ciclo
    if not historial or isinstance(historial, dict):
        historial = []
    elif not isinstance(historial, list):
        historial = []

    consulta.ciclo = historial + [nuevo_ciclo]
    consulta.ultimo_estado = nuevo_ciclo["estado"]
    flag_modified(consulta, "ciclo")


def buscar_consultas_activas(
    db: Session,
    paciente_id: Optional[int] = None,
    expediente: Optional[str] = None,
    documento: Optional[str] = None,
    cui: Optional[int] = None,
    primer_nombre: Optional[str] = None,
    segundo_nombre: Optional[str] = None,
    primer_apellido: Optional[str] = None,
    segundo_apellido: Optional[str] = None,
    tipo_consulta: Optional[int] = None,
    especialidad: Optional[str] = None,
    servicio: Optional[str] = None,
    fecha: Optional[date] = None,
    ultimo_estado: Optional[str] = None,
    activo: bool = True,
    archivo: bool = True,
    skip: int = 0,
    limit: int = 50,
):
    query = (
        db.query(ConsultaModel)
        .join(PacienteModel, ConsultaModel.paciente_id == PacienteModel.id)
    )

    query = query.filter(ConsultaModel.activo.is_(activo))

    if not archivo:
        query = query.filter(
            or_(
                ConsultaModel.ultimo_estado.is_(None),
                ConsultaModel.ultimo_estado != "archivo"
            )
        )

    if ultimo_estado is not None:
        query = query.filter(ConsultaModel.ultimo_estado == ultimo_estado)

    if paciente_id is not None:
        query = query.filter(ConsultaModel.paciente_id == paciente_id)

    if tipo_consulta is not None:
        query = query.filter(ConsultaModel.tipo_consulta == tipo_consulta)

    if documento is not None:
        query = query.filter(ConsultaModel.documento == documento)

    if especialidad:
        query = query.filter(ConsultaModel.especialidad == especialidad)

    if servicio:
        query = query.filter(ConsultaModel.servicio == servicio)

    if fecha:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        query = query.filter(
            ConsultaModel.fecha_consulta.between(inicio, fin)
        )

    if expediente:
        query = query.filter(
            or_(
                ConsultaModel.expediente == expediente,
                PacienteModel.expediente == expediente
            )
        )

    if cui is not None:
        query = query.filter(PacienteModel.cui == cui)

    if primer_nombre:
        query = query.filter(
            cast(PacienteModel.nombre["primer_nombre"], String)
            .ilike(f"%{primer_nombre}%")
        )

    if segundo_nombre:
        query = query.filter(
            cast(PacienteModel.nombre["segundo_nombre"], String)
            .ilike(f"%{segundo_nombre}%")
        )

    if primer_apellido:
        query = query.filter(
            cast(PacienteModel.nombre["primer_apellido"], String)
            .ilike(f"%{primer_apellido}%")
        )

    if segundo_apellido:
        query = query.filter(
            cast(PacienteModel.nombre["segundo_apellido"], String)
            .ilike(f"%{segundo_apellido}%")
        )

    total = query.count()
    resultados = (
        query
        .distinct()
        .order_by(ConsultaModel.id.desc())
        .limit(limit).offset(skip)
        .all()
    )

    return ConsultaListResponse(
        total=total,
        consultas=resultados
    )


def reingresos_consulta_tipo3(
    db: Session,
    skip: int = 0,
    limit: int = 50,
):
    desde = date.today() - timedelta(days=15)
    hasta = date.today()

    rn_subq = (
        db.query(
            ConsultaModel.id,
            func.row_number().over(
                partition_by=ConsultaModel.paciente_id,
                order_by=ConsultaModel.fecha_consulta.asc()
            ).label('rn')
        )
        .filter(
            ConsultaModel.tipo_consulta == 3,
            ConsultaModel.activo.is_(True),
            ConsultaModel.fecha_consulta.between(desde, hasta)
        )
        .subquery()
    )

    query = (
        db.query(ConsultaModel)
        .join(PacienteModel, ConsultaModel.paciente_id == PacienteModel.id)
        .join(rn_subq, ConsultaModel.id == rn_subq.c.id)
        .filter(rn_subq.c.rn > 1)
    )

    total = query.count()
    resultados = (
        query
        .distinct()
        .order_by(ConsultaModel.fecha_consulta.desc())
        .limit(limit).offset(skip)
        .all()
    )

    return ConsultaListResponse(
        total=total,
        consultas=resultados
    )


def consultas_activas_mayores_30_dias(
    db: Session,
    skip: int = 0,
    limit: int = 50,
):
    corte = date.today() - timedelta(days=30)
    query = (
        db.query(ConsultaModel)
        .join(PacienteModel, ConsultaModel.paciente_id == PacienteModel.id)
        .filter(
            ConsultaModel.tipo_consulta == 2,
            ConsultaModel.activo.is_(True),
            or_(
                ConsultaModel.ultimo_estado.is_(None),
                ConsultaModel.ultimo_estado != "archivo"
            ),
            ConsultaModel.fecha_consulta <= corte
        )
    )

    total = query.count()
    resultados = (
        query
        .distinct()
        .order_by(ConsultaModel.fecha_consulta.asc())
        .limit(limit).offset(skip)
        .all()
    )

    return ConsultaListResponse(
        total=total,
        consultas=resultados
    )


def obtener_consulta(consulta_id: int, db: Session):
    consulta = db.get(ConsultaModel, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    return consulta


def registrar_consulta(datos: RegistroConsultaCreate, db: Session, current_user):
    paciente = db.get(PacienteModel, datos.paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    expediente_consulta: str | None = None
    documento_consulta: str | None = None

    if datos.tipo_consulta in (1, 2):
        if paciente.expediente:
            expediente_consulta = paciente.expediente
        else:
            expediente_consulta = generar_expediente(db)
            paciente.expediente = expediente_consulta
            db.add(paciente)

    elif datos.tipo_consulta == 3:
        documento_consulta = generar_emergencia(db)

    else:
        raise HTTPException(status_code=400, detail="Tipo de consulta inválido")

    indicadores_dict = datos.indicadores.model_dump() if datos.indicadores else {}
    empleado_publico = indicadores_dict.get("empleado_publico", False)

    if not empleado_publico and paciente.datos_extra:
        socioeconomicos = paciente.datos_extra.get("socioeconomicos", {})
        if socioeconomicos.get("empleado_publico") == "S":
            empleado_publico = True

    personal_hospital = indicadores_dict.get("personal_hospital")
    if personal_hospital is None and paciente.datos_extra:
        ph = paciente.datos_extra.get("socioeconomicos", {}).get("personal_hospital")
        if ph is True or ph == "S":
            personal_hospital = "S"
        elif ph is False or ph == "N":
            personal_hospital = "N"

    indicadores_completos = {
        "estudiante_publico": indicadores_dict.get("estudiante_publico", False),
        "empleado_publico": empleado_publico,
        "personal_hospital": personal_hospital,
        "accidente_laboral": indicadores_dict.get("accidente_laboral", False),
        "discapacidad": indicadores_dict.get("discapacidad", False),
        "accidente_transito": indicadores_dict.get("accidente_transito", False),
        "arma_fuego": indicadores_dict.get("arma_fuego", False),
        "arma_blanca": indicadores_dict.get("arma_blanca", False),
        "ambulancia": indicadores_dict.get("ambulancia", False),
        "embarazo": indicadores_dict.get("embarazo", False),
    }

    ciclo_inicial = CicloClinico(
        estado="admision",
        registro=datetime.now().isoformat(),
        usuario=current_user.username,
        especialidad=datos.especialidad,
        servicio=datos.servicio
    )

    ciclo_historial = [ciclo_inicial.model_dump(mode="json")]

    hoy = date.today()
    ultimo_orden = (
        db.query(func.coalesce(func.max(ConsultaModel.orden), 0))
        .filter(
            ConsultaModel.fecha_consulta == hoy,
            ConsultaModel.tipo_consulta == datos.tipo_consulta,
            ConsultaModel.especialidad == datos.especialidad
        )
        .scalar()
    ) or 0

    nueva_consulta = ConsultaModel(
        paciente_id=datos.paciente_id,
        expediente=expediente_consulta,
        documento=documento_consulta,
        tipo_consulta=datos.tipo_consulta,
        especialidad=datos.especialidad,
        servicio=datos.servicio,
        fecha_consulta=hoy,
        hora_consulta=datetime.now().time(),
        indicadores=indicadores_completos,
        ciclo=ciclo_historial,
        orden=ultimo_orden + 1,
        ultimo_estado="admision",
    )

    db.add(nueva_consulta)

    try:
        db.commit()
        db.refresh(nueva_consulta)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar consulta: {str(e)}"
        )

    return RegistroConsultaOut(
        id=nueva_consulta.id,
        expediente=nueva_consulta.expediente,
        paciente_id=nueva_consulta.paciente_id,
        tipo_consulta=nueva_consulta.tipo_consulta,
        especialidad=nueva_consulta.especialidad,
        servicio=nueva_consulta.servicio,
        documento=nueva_consulta.documento,
        fecha_consulta=nueva_consulta.fecha_consulta,
        hora_consulta=nueva_consulta.hora_consulta,
        indicadores=Indicador(**nueva_consulta.indicadores),
        ciclo=[CicloClinico(**c) for c in nueva_consulta.ciclo],
        orden=nueva_consulta.orden
    )


def actualizar_consulta(consulta_id: int, update_data: ConsultaUpdate, db: Session, current_user):
    consulta = db.get(ConsultaModel, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    ESTADO_ARCHIVADO = "archivo"
    esta_archivado = consulta.ultimo_estado == ESTADO_ARCHIVADO

    datos = update_data.model_dump(exclude_unset=True, exclude={'ciclo'})

    if esta_archivado:
        datos.pop('ultimo_estado', None)
        datos.pop('activo', None)

    if "paciente_id" in datos:
        paciente = db.get(PacienteModel, datos["paciente_id"])
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        if paciente.expediente:
            datos["expediente"] = paciente.expediente

    if "tipo_consulta" in datos and datos["tipo_consulta"] != consulta.tipo_consulta:
        if datos["tipo_consulta"] == 3:
            datos["documento"] = generar_emergencia(db)
        else:
            paciente = db.get(PacienteModel, consulta.paciente_id)
            if paciente and paciente.expediente:
                datos["documento"] = paciente.expediente

    if "indicadores" in datos:
        if isinstance(datos["indicadores"], Indicador):
            datos["indicadores"] = datos["indicadores"].model_dump()

        indicadores_actuales = consulta.indicadores or {}
        indicadores_nuevos = datos["indicadores"] or {}
        datos["indicadores"] = {**indicadores_actuales, **indicadores_nuevos}

    if "egreso" in datos:
        if isinstance(datos["egreso"], Egreso):
            datos["egreso"] = datos["egreso"].model_dump(exclude_none=True)

        egreso_actual = consulta.egreso or {}
        egreso_nuevo = datos["egreso"] or {}

        if "registro" not in egreso_nuevo:
            egreso_nuevo["registro"] = datetime.now().isoformat()

        datos["egreso"] = {**egreso_actual, **egreso_nuevo}

    if update_data.ciclo is not None:
        nuevo_ciclo = update_data.ciclo.model_dump_clean(mode='json')
        _agregar_ciclo(consulta, nuevo_ciclo, current_user)

    recalcular_orden = any(
        key in datos
        for key in ["fecha_consulta", "tipo_consulta", "especialidad"]
    )

    if recalcular_orden:
        fecha = datos.get("fecha_consulta", consulta.fecha_consulta)
        tipo = datos.get("tipo_consulta", consulta.tipo_consulta)
        especialidad = datos.get("especialidad", consulta.especialidad)

        ultimo_orden = (
            db.query(func.coalesce(func.max(ConsultaModel.orden), 0))
            .filter(
                ConsultaModel.fecha_consulta == fecha,
                ConsultaModel.tipo_consulta == tipo,
                ConsultaModel.especialidad == especialidad,
                ConsultaModel.id != consulta_id
            )
            .scalar()
        ) or 0

        datos["orden"] = ultimo_orden + 1

    for key, value in datos.items():
        setattr(consulta, key, value)

    if esta_archivado:
        consulta.ultimo_estado = ESTADO_ARCHIVADO

    try:
        db.commit()
        db.refresh(consulta)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar la consulta: {str(e)}"
        )

    return consulta


def desactivar_consulta(consulta_id: int, db: Session, current_user):
    consulta = db.get(ConsultaModel, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    if consulta.ultimo_estado == "archivo":
        raise HTTPException(
            status_code=400,
            detail="La consulta ya se encuentra borrada"
        )

    _agregar_ciclo(
        consulta,
        {"estado": "borrado"},
        current_user
    )

    consulta.activo = False

    try:
        db.commit()
        db.refresh(consulta)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al archivar la consulta: {str(e)}"
        )

    return consulta


def eliminar_consulta(consulta_id: int, db: Session, current_user=None):
    consulta = db.get(ConsultaModel, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    try:
        db.query(CiclosConsulta).filter(
            CiclosConsulta.consulta_id == consulta_id
        ).delete(synchronize_session=False)
        db.query(Laboratorios).filter(
            Laboratorios.consulta_id == consulta_id
        ).delete(synchronize_session=False)
        db.query(RayosX).filter(
            RayosX.consulta_id == consulta_id
        ).delete(synchronize_session=False)

        db.delete(consulta)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar la consulta: {str(e)}"
        )

    return {"detail": f"Consulta {consulta_id} eliminada permanentemente"}


def sincronizar_indicadores(db: Session, desde: date, hasta: date, current_user):
    consultas = (
        db.query(ConsultaModel)
        .join(PacienteModel, ConsultaModel.paciente_id == PacienteModel.id)
        .filter(ConsultaModel.fecha_consulta.between(desde, hasta))
        .all()
    )

    actualizados = 0
    saltados = 0

    for consulta in consultas:
        paciente = consulta.paciente

        indicadores = consulta.indicadores or {}
        cambio = False

        if paciente and paciente.datos_extra:
            socioeconomicos = paciente.datos_extra.get("socioeconomicos", {})
            socio_empleado = socioeconomicos.get("empleado_publico")
            socio_estudiante = socioeconomicos.get("estudiante_publico")
            socio_ph = socioeconomicos.get("personal_hospital")

            if socio_empleado == "S" and not indicadores.get("empleado_publico"):
                indicadores["empleado_publico"] = True
                cambio = True
            if socio_estudiante == "S" and not indicadores.get("estudiante_publico"):
                indicadores["estudiante_publico"] = True
                cambio = True

            ph_actual = indicadores.get("personal_hospital")
            if socio_ph is True or socio_ph == "S":
                if ph_actual not in ("S", "N"):
                    indicadores["personal_hospital"] = "S"
                    cambio = True
            elif socio_ph is False or socio_ph == "N":
                if ph_actual not in ("S", "N"):
                    indicadores["personal_hospital"] = "N"
                    cambio = True

        ph_actual = indicadores.get("personal_hospital")
        if ph_actual is True:
            indicadores["personal_hospital"] = "S"
            cambio = True
        elif ph_actual is False:
            indicadores["personal_hospital"] = "N"
            cambio = True

        if cambio:
            consulta.indicadores = indicadores
            flag_modified(consulta, "indicadores")
            actualizados += 1
        else:
            saltados += 1

    db.commit()

    return {
        "mensaje": "Sincronización completada",
        "total_consultas_en_rango": len(consultas),
        "actualizados": actualizados,
        "saltados": saltados,
        "desde": desde.isoformat(),
        "hasta": hasta.isoformat(),
        "usuario": current_user.username,
    }
