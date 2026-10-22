"""Reporte/resumen de quirófanos: consulta unificada, KPIs y agrupación.

Toda la información que consume el componente HTML (`QuirofanoResumenComponent`)
y el generador de Excel (`reportes_excel.py`) sale de `generar_reporte`, para
garantizar que ambas vistas coincidan. Los tiempos se devuelven en **segundos
enteros** y las horas como cadenas "HH:MM" (o None).
"""

from __future__ import annotations

from datetime import date, time, timedelta

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from modules.especialidades.models import EspecialidadModel
from modules.pacientes.models import PacienteModel
from modules.personal_atencion.models import PersonalAtencionModel
from modules.procedimientos.models import AreaCuerpoIntervenida
from modules.catalogo_procedimientos.models import CatalogoProcedimiento

from .models import (
    IntervencionQuirurgicaModel,
    EstadoCirugiaModel,
    FormatoProcedimientoModel,
    ProcedenciaProcedimientoModel,
    RangoEspecialistaModel,
    QuirofanoNumeroModel,
    QuirofanoConfigPeriodoModel,
)

SEG_DIA = 86400
MAX_DIAS_PERIODO = 366
MAX_FILAS_HOJA = 600
_FIN = "Finalizada"
_CAN = "Cancelada"
_REP = "Reprogramada"


# ========================
# Helpers de tiempo
# ========================
def _t2s(t: time | None) -> int | None:
    if t is None:
        return None
    return t.hour * 3600 + t.minute * 60 + t.second


def _diff_seg(inicio: time | None, fin: time | None) -> int | None:
    """Segundos entre dos horas; si el fin es anterior, cruza medianoche (24 h)."""
    a = _t2s(inicio)
    b = _t2s(fin)
    if a is None or b is None:
        return None
    d = b - a
    if d < 0:
        d += SEG_DIA
    return d


def _fmt_hora(t: time | None) -> str | None:
    return t.strftime("%H:%M") if t else None


def _promedio(valores: list[int]) -> int | None:
    """Promedio entero de valores > 0 (excluye nulos y ceros, como AVERAGEIF <>0)."""
    v = [x for x in valores if x]
    return round(sum(v) / len(v)) if v else None


# ========================
# Configuración de jornada
# ========================
def _config_por_quirofano(db: Session, qn_ids: list[int]) -> dict[int, QuirofanoConfigPeriodoModel]:
    if not qn_ids:
        return {}
    return {
        c.quirofano_numero_id: c
        for c in db.query(QuirofanoConfigPeriodoModel)
        .filter(QuirofanoConfigPeriodoModel.quirofano_numero_id.in_(qn_ids))
        .all()
    }


def listar_config_periodo(db: Session, skip: int = 0, limit: int = 100) -> list[dict]:
    quirofanos = (
        db.query(QuirofanoNumeroModel)
        .filter(QuirofanoNumeroModel.activo == True)  # noqa: E712
        .order_by(QuirofanoNumeroModel.numero)
        .offset(skip)
        .limit(limit)
        .all()
    )
    configs = _config_por_quirofano(db, [q.quirofano_numero_id for q in quirofanos])
    salida = []
    for q in quirofanos:
        c = configs.get(q.quirofano_numero_id)
        salida.append(
            {
                "config_periodo_id": c.config_periodo_id if c else 0,
                "quirofano_numero_id": q.quirofano_numero_id,
                "quirofano_numero_nombre": q.nombre,
                "hora_apertura": c.hora_apertura if c else time(7, 0),
                "hora_cierre": c.hora_cierre if c else time(16, 0),
                "dias_habiles": c.dias_habiles if c else 0,
                "activo": c.activo if c else True,
            }
        )
    return salida


def actualizar_config_periodo(db: Session, quirofano_numero_id: int, data) -> dict:
    q = (
        db.query(QuirofanoNumeroModel)
        .filter(QuirofanoNumeroModel.quirofano_numero_id == quirofano_numero_id)
        .first()
    )
    if not q:
        raise HTTPException(status_code=404, detail="Número de quirófano no encontrado")

    c = (
        db.query(QuirofanoConfigPeriodoModel)
        .filter(QuirofanoConfigPeriodoModel.quirofano_numero_id == quirofano_numero_id)
        .first()
    )
    if not c:
        c = QuirofanoConfigPeriodoModel(
            quirofano_numero_id=quirofano_numero_id,
            hora_apertura=time(7, 0),
            hora_cierre=time(16, 0),
            dias_habiles=0,
            activo=True,
        )
        db.add(c)

    if data.hora_apertura is not None:
        c.hora_apertura = data.hora_apertura
    if data.hora_cierre is not None:
        c.hora_cierre = data.hora_cierre
    if data.dias_habiles is not None:
        c.dias_habiles = data.dias_habiles
    if data.activo is not None:
        c.activo = data.activo

    if _t2s(c.hora_cierre) <= _t2s(c.hora_apertura):
        raise HTTPException(
            status_code=422,
            detail="La hora de cierre debe ser posterior a la hora de apertura",
        )

    db.commit()
    db.refresh(c)
    return {
        "config_periodo_id": c.config_periodo_id,
        "quirofano_numero_id": c.quirofano_numero_id,
        "quirofano_numero_nombre": q.nombre,
        "hora_apertura": c.hora_apertura,
        "hora_cierre": c.hora_cierre,
        "dias_habiles": c.dias_habiles,
        "activo": c.activo,
    }


# ========================
# Consulta unificada de intervenciones
# ========================
def _query_intervenciones(
    db: Session, fecha_desde: date, fecha_hasta: date, especialidad_id: int | None
):
    p1 = aliased(CatalogoProcedimiento)
    p2 = aliased(CatalogoProcedimiento)
    p3 = aliased(CatalogoProcedimiento)
    p4 = aliased(CatalogoProcedimiento)
    p5 = aliased(CatalogoProcedimiento)

    q = (
        db.query(
            IntervencionQuirurgicaModel,
            PacienteModel,
            PersonalAtencionModel,
            EstadoCirugiaModel,
            FormatoProcedimientoModel,
            ProcedenciaProcedimientoModel,
            RangoEspecialistaModel,
            QuirofanoNumeroModel,
            EspecialidadModel,
            AreaCuerpoIntervenida,
            p1.nombre,
            p2.nombre,
            p3.nombre,
            p4.nombre,
            p5.nombre,
        )
        .select_from(IntervencionQuirurgicaModel)
        .outerjoin(PacienteModel, PacienteModel.id == IntervencionQuirurgicaModel.paciente_id)
        .outerjoin(PersonalAtencionModel, PersonalAtencionModel.id == IntervencionQuirurgicaModel.personal_atencion_id)
        .outerjoin(
            EstadoCirugiaModel,
            EstadoCirugiaModel.estado_cirugia_id == IntervencionQuirurgicaModel.estado_cirugia_id,
        )
        .outerjoin(
            FormatoProcedimientoModel,
            FormatoProcedimientoModel.formato_procedimiento_id
            == IntervencionQuirurgicaModel.formato_procedimiento_id,
        )
        .outerjoin(
            ProcedenciaProcedimientoModel,
            ProcedenciaProcedimientoModel.procedencia_procedimiento_id
            == IntervencionQuirurgicaModel.procedencia_procedimiento_id,
        )
        .outerjoin(
            RangoEspecialistaModel,
            RangoEspecialistaModel.rango_especialista_id
            == IntervencionQuirurgicaModel.rango_especialista_id,
        )
        .outerjoin(
            QuirofanoNumeroModel,
            QuirofanoNumeroModel.quirofano_numero_id
            == IntervencionQuirurgicaModel.quirofano_numero_id,
        )
        .outerjoin(EspecialidadModel, EspecialidadModel.id == IntervencionQuirurgicaModel.especialidad_id)
        .outerjoin(
            AreaCuerpoIntervenida,
            AreaCuerpoIntervenida.id == IntervencionQuirurgicaModel.id_area_cuerpo_intervenida,
        )
        .outerjoin(p1, p1.id == IntervencionQuirurgicaModel.procedimiento_principal_id)
        .outerjoin(p2, p2.id == IntervencionQuirurgicaModel.procedimiento_2_id)
        .outerjoin(p3, p3.id == IntervencionQuirurgicaModel.procedimiento_3_id)
        .outerjoin(p4, p4.id == IntervencionQuirurgicaModel.procedimiento_4_id)
        .outerjoin(p5, p5.id == IntervencionQuirurgicaModel.procedimiento_5_id)
        .filter(
            IntervencionQuirurgicaModel.activo == True,  # noqa: E712
            IntervencionQuirurgicaModel.fecha >= fecha_desde,
            IntervencionQuirurgicaModel.fecha <= fecha_hasta,
        )
    )
    if especialidad_id is not None:
        q = q.filter(IntervencionQuirurgicaModel.especialidad_id == especialidad_id)
    return q.order_by(
        QuirofanoNumeroModel.numero.asc().nulls_last(),
        IntervencionQuirurgicaModel.fecha.asc(),
        IntervencionQuirurgicaModel.hora_inicio_intervencion.asc().nulls_last(),
        IntervencionQuirurgicaModel.intervencion_id.asc(),
    ).all()


def _fila_desde_registro(row, no: int) -> dict:
    (
        interv,
        paciente,
        medico,
        estado,
        formato,
        procedencia,
        rango,
        quirofano,
        especialidad,
        area,
        proc1,
        proc2,
        proc3,
        proc4,
        proc5,
    ) = row

    nombres = [
        (interv.procedimiento_principal or proc1),
        (interv.procedimiento_2 or proc2),
        (interv.procedimiento_3 or proc3),
        (interv.procedimiento_4 or proc4),
        (interv.procedimiento_5 or proc5),
    ]
    nombres = [n.strip() for n in nombres if n and n.strip()]

    return {
        "no": no,
        "intervencion_id": interv.intervencion_id,
        "quirofano_numero_id": interv.quirofano_numero_id,
        "fecha": interv.fecha,
        "paciente_nombre": getattr(paciente, "nombre_completo", None) if paciente else None,
        "rango_medico": getattr(rango, "nombre", None) if rango else None,
        "especialidad": getattr(especialidad, "nombre", None) if especialidad else None,
        "medico": getattr(medico, "nombre", None) if medico else None,
        "procedencia": getattr(procedencia, "nombre", None) if procedencia else None,
        "formato": getattr(formato, "nombre", None) if formato else None,
        "procedimiento_1": nombres[0] if len(nombres) > 0 else None,
        "procedimiento_2": nombres[1] if len(nombres) > 1 else None,
        "procedimiento_3": nombres[2] if len(nombres) > 2 else None,
        "procedimiento_4": nombres[3] if len(nombres) > 3 else None,
        "procedimiento_5": nombres[4] if len(nombres) > 4 else None,
        "procedimientos": " + ".join(nombres) if nombres else None,
        "area_cuerpo": interv.area_cuerpo_intervenida
        or (getattr(area, "nombre", None) if area else None),
        "observaciones": interv.observaciones,
        "hora_inicio_anestesia": _fmt_hora(interv.hora_inicio_anestesia),
        "hora_inicio_intervencion": _fmt_hora(interv.hora_inicio_intervencion),
        "hora_finaliza_intervencion": _fmt_hora(interv.hora_finaliza_intervencion),
        "hora_finaliza_limpieza": _fmt_hora(interv.hora_finaliza_limpieza_prepara_quirofano),
        "tiempo_intervencion_seg": _diff_seg(
            interv.hora_inicio_intervencion, interv.hora_finaliza_intervencion
        ),
        "tiempo_uso_quirofano_seg": _diff_seg(
            interv.hora_inicio_intervencion, interv.hora_finaliza_limpieza_prepara_quirofano
        ),
        "tiempo_limpieza_seg": _diff_seg(
            interv.hora_finaliza_intervencion,
            interv.hora_finaliza_limpieza_prepara_quirofano,
        ),
        "estado": getattr(estado, "nombre", None) if estado else None,
        "_proc_list": nombres,
    }


# ========================
# KPIs
# ========================
def _kpi(
    filas: list[dict],
    *,
    quirofano_numero_id: int | None,
    numero: int | None,
    nombre: str,
    hora_apertura: time,
    hora_cierre: time,
    dias_abiertos: int,
    es_fallback: bool,
) -> dict:
    fin = [f for f in filas if f["estado"] == _FIN]
    can = [f for f in filas if f["estado"] == _CAN]
    rep = [f for f in filas if f["estado"] == _REP]

    horas_activo = _diff_seg(hora_apertura, hora_cierre) or 0
    tiempo_disponible = horas_activo * dias_abiertos

    uso_fin = sum(f["tiempo_uso_quirofano_seg"] or 0 for f in fin)
    porcentaje_uso = (uso_fin / tiempo_disponible) if tiempo_disponible > 0 else 0.0

    denom_tasa = len(fin) + len(can)
    tasa = (len(can) / denom_tasa) if denom_tasa else 0.0
    denom_tasa_rep = len(fin) + len(can) + len(rep)
    tasa_rep = (len(can) / denom_tasa_rep) if denom_tasa_rep else 0.0

    procedimientos = sum(len(f["_proc_list"]) for f in filas)

    fechas = sorted({f["fecha"] for f in filas})
    intervalo = None
    if len(fechas) > 1 and procedimientos:
        intervalo = (fechas[-1] - fechas[0]).days / procedimientos

    return {
        "quirofano_numero_id": quirofano_numero_id,
        "numero": numero,
        "nombre": nombre,
        "hora_apertura": _fmt_hora(hora_apertura),
        "hora_cierre": _fmt_hora(hora_cierre),
        "es_fallback": es_fallback,
        "dias_abiertos": dias_abiertos,
        "tiempo_disponible_seg": tiempo_disponible,
        "horas_activo_seg": horas_activo,
        "total_intervenciones": len(filas),
        "finalizadas": len(fin),
        "canceladas": len(can),
        "reprogramadas": len(rep),
        "procedimientos_total": procedimientos,
        "intervalos_dias_promedio": intervalo,
        "tiempo_promedio_intervencion_seg": _promedio([f["tiempo_intervencion_seg"] for f in filas]),
        "tiempo_promedio_uso_quirofano_seg": _promedio(
            [f["tiempo_uso_quirofano_seg"] for f in filas]
        ),
        "tiempo_promedio_limpieza_seg": _promedio([f["tiempo_limpieza_seg"] for f in filas]),
        "porcentaje_uso": porcentaje_uso,
        "tasa_cancelacion": tasa,
        "tasa_cancelacion_con_reprogramadas": tasa_rep,
    }


def _resolver_jornada(
    filas: list[dict],
    config: QuirofanoConfigPeriodoModel | None,
    hora_apertura: time | None,
    hora_cierre: time | None,
    dias_abiertos: int | None,
) -> tuple[time, time, int, bool]:
    """Deduce la jornada: prevalece el parámetro explícito, luego los datos del
    período y por último la configuración del quirófano. `es_fallback` indica que
    se usó la configuración (no hubo datos ni parámetros)."""
    anestesias = [f["hora_inicio_anestesia"] for f in filas if f["hora_inicio_anestesia"]]
    limpiezas = [f["hora_finaliza_limpieza"] for f in filas if f["hora_finaliza_limpieza"]]

    fallback = False
    if hora_apertura is not None:
        ap = hora_apertura
    elif anestesias:
        ap = min(time.fromisoformat(h) for h in anestesias)
    else:
        ap = config.hora_apertura if config else time(7, 0)
        fallback = True

    if hora_cierre is not None:
        ci = hora_cierre
    elif limpiezas:
        ci = max(time.fromisoformat(h) for h in limpiezas)
    else:
        ci = config.hora_cierre if config else time(16, 0)
        fallback = True

    if dias_abiertos is not None:
        dias = dias_abiertos
    else:
        dias = len({f["fecha"] for f in filas})
        if dias == 0:
            dias = (config.dias_habiles if config else 0) or 0
            fallback = True

    if _t2s(ci) <= _t2s(ap):
        ci = time(23, 59, 59)

    return ap, ci, dias, fallback


# ========================
# Reporte completo
# ========================
def generar_reporte(
    db: Session,
    *,
    fecha_desde: date,
    fecha_hasta: date,
    especialidad_id: int | None = None,
    quirofano_numero_id: int | None = None,
    hora_apertura: time | None = None,
    hora_cierre: time | None = None,
    dias_abiertos: int | None = None,
) -> dict:
    if fecha_desde > fecha_hasta:
        raise HTTPException(status_code=422, detail="fecha_desde no puede ser mayor que fecha_hasta")
    if (fecha_hasta - fecha_desde).days > MAX_DIAS_PERIODO:
        raise HTTPException(status_code=422, detail=f"El período no puede exceder {MAX_DIAS_PERIODO} días")

    advertencias: list[str] = []
    registros = _query_intervenciones(db, fecha_desde, fecha_hasta, especialidad_id)

    filas = [_fila_desde_registro(r, i) for i, r in enumerate(registros, start=1)]

    # Agrupación por quirófano (incluye grupo "sin quirófano").
    grupos: dict[int | None, list[dict]] = {}
    for f in filas:
        grupos.setdefault(f["quirofano_numero_id"], []).append(f)

    quirofanos = (
        db.query(QuirofanoNumeroModel)
        .filter(QuirofanoNumeroModel.activo == True)  # noqa: E712
        .order_by(QuirofanoNumeroModel.numero)
        .all()
    )
    if quirofano_numero_id is not None:
        quirofanos = [q for q in quirofanos if q.quirofano_numero_id == quirofano_numero_id]
        if not quirofanos:
            raise HTTPException(status_code=404, detail="Número de quirófano no encontrado")

    configs = _config_por_quirofano(
        db, [q.quirofano_numero_id for q in quirofanos]
    )
    por_quirofano: list[dict] = []

    for q in quirofanos:
        rows = grupos.get(q.quirofano_numero_id, [])
        ap, ci, dias, fallback = _resolver_jornada(
            rows, configs.get(q.quirofano_numero_id), hora_apertura, hora_cierre, dias_abiertos
        )
        kpi = _kpi(
            rows,
            quirofano_numero_id=q.quirofano_numero_id,
            numero=q.numero,
            nombre=f"Quirófano #{q.numero}",
            hora_apertura=ap,
            hora_cierre=ci,
            dias_abiertos=dias,
            es_fallback=fallback,
        )
        if len(rows) > MAX_FILAS_HOJA:
            advertencias.append(
                f"El {kpi['nombre']} tiene {len(rows)} intervenciones en el período "
                f"(más de {MAX_FILAS_HOJA}); se conservan todas en el reporte."
            )
        por_quirofano.append({"kpi": kpi, "intervenciones": rows})

    # Grupo sin quirófano (solo si hay datos y no se filtró por quirófano).
    if quirofano_numero_id is None and grupos.get(None):
        rows = grupos[None]
        ap, ci, dias, fallback = _resolver_jornada(rows, None, hora_apertura, hora_cierre, dias_abiertos)
        kpi = _kpi(
            rows,
            quirofano_numero_id=None,
            numero=None,
            nombre="Sin quirófano asignado",
            hora_apertura=ap,
            hora_cierre=ci,
            dias_abiertos=dias,
            es_fallback=fallback,
        )
        por_quirofano.append({"kpi": kpi, "intervenciones": rows})
        advertencias.append(
            f"{len(rows)} intervención(es) no tienen quirófano asignado y no se incluyen "
            "en las hojas Q del Excel."
        )

    # KPI global: suma de disponibilidad y de conteos.
    disponible_total = sum(p["kpi"]["tiempo_disponible_seg"] for p in por_quirofano)
    uso_fin_total = sum(
        f["tiempo_uso_quirofano_seg"] or 0
        for f in filas
        if f["estado"] == _FIN
    )
    finalizadas = sum(1 for f in filas if f["estado"] == _FIN)
    canceladas = sum(1 for f in filas if f["estado"] == _CAN)
    reprogramadas = sum(1 for f in filas if f["estado"] == _REP)
    denom = finalizadas + canceladas
    denom_rep = finalizadas + canceladas + reprogramadas

    kpi_global = {
        "quirofano_numero_id": None,
        "numero": None,
        "nombre": "Global (todos los quirófanos)",
        "hora_apertura": None,
        "hora_cierre": None,
        "es_fallback": False,
        "dias_abiertos": max((p["kpi"]["dias_abiertos"] for p in por_quirofano), default=0),
        "tiempo_disponible_seg": disponible_total,
        "horas_activo_seg": 0,
        "total_intervenciones": len(filas),
        "finalizadas": finalizadas,
        "canceladas": canceladas,
        "reprogramadas": reprogramadas,
        "procedimientos_total": sum(len(f["_proc_list"]) for f in filas),
        "intervalos_dias_promedio": None,
        "tiempo_promedio_intervencion_seg": _promedio(
            [f["tiempo_intervencion_seg"] for f in filas]
        ),
        "tiempo_promedio_uso_quirofano_seg": _promedio(
            [f["tiempo_uso_quirofano_seg"] for f in filas]
        ),
        "tiempo_promedio_limpieza_seg": _promedio([f["tiempo_limpieza_seg"] for f in filas]),
        "porcentaje_uso": (uso_fin_total / disponible_total) if disponible_total > 0 else 0.0,
        "tasa_cancelacion": (canceladas / denom) if denom else 0.0,
        "tasa_cancelacion_con_reprogramadas": (canceladas / denom_rep) if denom_rep else 0.0,
    }

    # Resumen por procedimiento (una fila por procedimiento, no por combinación).
    acumulado: dict[str, dict] = {}
    for f in filas:
        for nombre in f["_proc_list"]:
            item = acumulado.setdefault(nombre, {"cantidad": 0, "tiempos": []})
            item["cantidad"] += 1
            if f["tiempo_intervencion_seg"]:
                item["tiempos"].append(f["tiempo_intervencion_seg"])

    dias_periodo = (fecha_hasta - fecha_desde).days + 1
    procedimientos = []
    for nombre, item in sorted(acumulado.items(), key=lambda kv: (-kv[1]["cantidad"], kv[0])):
        tiempo = _promedio(item["tiempos"])
        procedimientos.append(
            {
                "procedimiento": nombre,
                "cantidad": item["cantidad"],
                "tiempo_promedio_seg": tiempo,
                "porcentaje_uso": (
                    ((tiempo or 0) * item["cantidad"]) / disponible_total
                    if disponible_total > 0
                    else 0.0
                ),
                "intervalo_dias_promedio": (
                    dias_periodo / item["cantidad"] if item["cantidad"] else None
                ),
            }
        )

    # Limpiar la clave interna usada para agrupar procedimientos.
    for p in por_quirofano:
        for fila in p["intervenciones"]:
            fila.pop("_proc_list", None)

    return {
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "generado_en": datetime_now_iso(),
        "filtros": {
            "especialidad_id": especialidad_id,
            "quirofano_numero_id": quirofano_numero_id,
            "hora_apertura": _fmt_hora(hora_apertura),
            "hora_cierre": _fmt_hora(hora_cierre),
            "dias_abiertos": dias_abiertos,
        },
        "kpi_global": kpi_global,
        "por_quirofano": por_quirofano,
        "procedimientos": procedimientos,
        "advertencias": advertencias,
    }


def datetime_now_iso() -> str:
    """Fecha/hora local en ISO sin dependencias externas adicionales."""
    from datetime import datetime

    return datetime.now().replace(microsecond=0).isoformat()
