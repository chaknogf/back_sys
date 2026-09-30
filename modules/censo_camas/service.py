"""Reglas y consultas del censo diario; los totales se derivan de sus componentes."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from datetime import date, datetime
import csv
import io
import unicodedata

from modules.censo_camas.models import CensoCamasModel
from modules.censo_camas.schemas import (
    CensoCamasCreate,
    CensoCamasUpdate,
    HospitalizacionEspecialidadItem,
)

_SEXES = ("masculino", "femenino")
_RAW_FIELDS = (
    "ocupados", "egresos", "fallecidos", "referido", "traslado",
    "contraindicados", "otro_ingresos", "ingresos", "huespedes", "emergencia",
)


def _calc_egresos_totales(egresos: int, fallecidos: int, referido: int, traslado: int, contraindicados: int) -> int:
    return egresos + fallecidos + referido + traslado + contraindicados


def _calc_camas_ocupadas(ocupados: int, otro_ingresos: int, ingresos: int, huespedes: int, emergencia: int, egresos_totales: int) -> int:
    return (emergencia + huespedes + ingresos + otro_ingresos + ocupados) - egresos_totales


def _sex_out(r: CensoCamasModel, sexo: str) -> dict:
    values = {field: getattr(r, f"{field}_{sexo}") for field in _RAW_FIELDS}
    egresos_totales = _calc_egresos_totales(
        values["egresos"], values["fallecidos"], values["referido"],
        values["traslado"], values["contraindicados"],
    )
    values["egresos_totales"] = egresos_totales
    values["camas_ocupadas"] = _calc_camas_ocupadas(
        values["ocupados"], values["otro_ingresos"], values["ingresos"],
        values["huespedes"], values["emergencia"], egresos_totales,
    )
    return values


def _aggregate_values(masculino: dict, femenino: dict) -> dict:
    totals = {
        field: masculino[field] + femenino[field]
        for field in _RAW_FIELDS
    }
    totals["egresos_totales"] = sum(
        _calc_egresos_totales(
            values["egresos"], values["fallecidos"], values["referido"],
            values["traslado"], values["contraindicados"],
        )
        for values in (masculino, femenino)
    )
    totals["camas_ocupadas"] = sum(
        _calc_camas_ocupadas(
            values["ocupados"], values["otro_ingresos"], values["ingresos"],
            values["huespedes"], values["emergencia"],
            _calc_egresos_totales(
                values["egresos"], values["fallecidos"], values["referido"],
                values["traslado"], values["contraindicados"],
            ),
        )
        for values in (masculino, femenino)
    )
    return totals


def _refresh_aggregates(registro: CensoCamasModel) -> None:
    by_sex = {
        sexo: {field: getattr(registro, f"{field}_{sexo}") for field in _RAW_FIELDS}
        for sexo in _SEXES
    }
    for field, value in _aggregate_values(by_sex["masculino"], by_sex["femenino"]).items():
        setattr(registro, field, value)


def _to_out(r: CensoCamasModel) -> dict:
    masculino = _sex_out(r, "masculino")
    femenino = _sex_out(r, "femenino")
    totales = {
        **{field: getattr(r, field) for field in _RAW_FIELDS},
        "egresos_totales": r.egresos_totales,
        "camas_ocupadas": r.camas_ocupadas,
    }
    return {
        "id": r.id,
        "fecha": r.fecha,
        "servicio_id": r.servicio_id,
        **totales,
        "masculino": masculino,
        "femenino": femenino,
        "totales": totales,
        "created_at": r.created_at,
        "updated_at": r.updated_at,
    }


def _build_model(data: CensoCamasCreate) -> dict:
    result = {"fecha": data.fecha, "servicio_id": data.servicio_id}
    by_sex = {}
    for sexo in _SEXES:
        by_sex[sexo] = getattr(data, sexo).model_dump()
        result.update({f"{field}_{sexo}": value for field, value in by_sex[sexo].items()})
    result.update(_aggregate_values(by_sex["masculino"], by_sex["femenino"]))
    return result


def _apply_update(registro: CensoCamasModel, data: CensoCamasUpdate) -> None:
    for sexo in _SEXES:
        sex_data = getattr(data, sexo)
        if sex_data is not None:
            for field, value in sex_data.model_dump(exclude_unset=True).items():
                setattr(registro, f"{field}_{sexo}", value)
    _refresh_aggregates(registro)


def _replace_values(registro: CensoCamasModel, data: CensoCamasCreate) -> None:
    for field, value in _build_model(data).items():
        if field not in ("fecha", "servicio_id"):
            setattr(registro, field, value)


def crear_registro(data: CensoCamasCreate, db: Session) -> dict:
    existe = db.query(CensoCamasModel).filter(
        CensoCamasModel.fecha == data.fecha,
        CensoCamasModel.servicio_id == data.servicio_id,
    ).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un registro para esa fecha y servicio"
        )
    registro = CensoCamasModel(**_build_model(data))
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return _to_out(registro)


def upsert_registro(data: CensoCamasCreate, db: Session) -> dict:
    existe = db.query(CensoCamasModel).filter(
        CensoCamasModel.fecha == data.fecha,
        CensoCamasModel.servicio_id == data.servicio_id,
    ).first()
    if existe:
        _replace_values(existe, data)
        db.commit()
        db.refresh(existe)
        return _to_out(existe)
    registro = CensoCamasModel(**_build_model(data))
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return _to_out(registro)


def listar_registros(
    db: Session,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    servicio_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[dict], int]:
    query = db.query(CensoCamasModel)
    count_query = db.query(func.count(CensoCamasModel.id))

    if fecha:
        query = query.filter(CensoCamasModel.fecha == fecha)
        count_query = count_query.filter(CensoCamasModel.fecha == fecha)
    if fecha_desde:
        query = query.filter(CensoCamasModel.fecha >= fecha_desde)
        count_query = count_query.filter(CensoCamasModel.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(CensoCamasModel.fecha <= fecha_hasta)
        count_query = count_query.filter(CensoCamasModel.fecha <= fecha_hasta)
    if servicio_id:
        query = query.filter(CensoCamasModel.servicio_id == servicio_id)
        count_query = count_query.filter(CensoCamasModel.servicio_id == servicio_id)
    total = count_query.scalar()
    limit = min(limit, 500)
    registros = query.order_by(
        CensoCamasModel.fecha.desc(),
        CensoCamasModel.servicio_id,
    ).offset(skip).limit(limit).all()

    return [_to_out(r) for r in registros], total


def obtener_registro(registro_id: int, db: Session) -> dict:
    registro = db.query(CensoCamasModel).filter(CensoCamasModel.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de censo no encontrado")
    return _to_out(registro)


def actualizar_registro(registro_id: int, data: CensoCamasUpdate, db: Session) -> dict:
    registro = db.query(CensoCamasModel).filter(CensoCamasModel.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de censo no encontrado")
    _apply_update(registro, data)
    db.commit()
    db.refresh(registro)
    return _to_out(registro)


def eliminar_registro(registro_id: int, db: Session) -> None:
    registro = db.query(CensoCamasModel).filter(CensoCamasModel.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de censo no encontrado")
    try:
        db.delete(registro)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar, está relacionado con otros registros"
        )
    return None


def eliminar_por_periodo(desde: date, hasta: date, db: Session) -> dict:
    if desde > hasta:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha 'desde' debe ser menor o igual a 'hasta'"
        )
    query = db.query(CensoCamasModel).filter(
        CensoCamasModel.fecha >= desde,
        CensoCamasModel.fecha <= hasta,
    )
    eliminados = query.count()
    if eliminados == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron registros en el periodo {desde} al {hasta}"
        )
    try:
        query.delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al eliminar los registros del periodo"
        )
    return {"desde": desde, "hasta": hasta, "eliminados": eliminados}


def resumen_diario(fecha: date, db: Session) -> dict:
    from modules.encamamiento.models import EncamamientoModel

    servicios = db.query(EncamamientoModel).filter(
        EncamamientoModel.activo == True
    ).order_by(EncamamientoModel.nombre_servicio).all()

    registros = db.query(CensoCamasModel).filter(
        CensoCamasModel.fecha == fecha
    ).all()

    reg_map = {r.servicio_id: r for r in registros}

    total_ocupados = 0
    servicios_resumen = []

    for svc in servicios:
        registro = reg_map.get(svc.id)
        masc = _sex_out(registro, "masculino") if registro else None
        fem = _sex_out(registro, "femenino") if registro else None
        total_ocupados += registro.ocupados if registro else 0

        servicios_resumen.append({
            "servicio_id": svc.id,
            "servicio_nombre": svc.nombre_servicio,
            "camas_censables": svc.camas_censables,
            "masculino": masc,
            "femenino": fem,
        })

    promedio = round(total_ocupados / len(servicios), 2) if servicios else 0

    return {
        "fecha": fecha,
        "servicios": servicios_resumen,
        "total_ocupados": total_ocupados,
        "promedio": promedio,
    }


def bulk_create(registros: list[CensoCamasCreate], db: Session) -> dict:
    creados = 0
    actualizados = 0
    errores = []
    por_clave: dict[tuple[date, int], CensoCamasModel] = {}

    for data in registros:
        try:
            clave = (data.fecha, data.servicio_id)
            existe = por_clave.get(clave)
            if existe is None:
                existe = db.query(CensoCamasModel).filter(
                    CensoCamasModel.fecha == data.fecha,
                    CensoCamasModel.servicio_id == data.servicio_id,
                ).first()
            if existe:
                _replace_values(existe, data)
                por_clave[clave] = existe
                actualizados += 1
            else:
                registro = CensoCamasModel(**_build_model(data))
                db.add(registro)
                por_clave[clave] = registro
                creados += 1
        except Exception as e:
            db.rollback()
            errores.append({
                "fecha": str(data.fecha),
                "servicio_id": data.servicio_id,
                "error": str(e),
            })

    if creados or actualizados:
        db.commit()

    return {
        "creados": creados,
        "actualizados": actualizados,
        "errores": errores,
    }


def estadisticas(desde: date, hasta: date, db: Session) -> dict:
    from modules.encamamiento.models import EncamamientoModel

    dias_en_rango = (hasta - desde).days + 1
    if dias_en_rango < 1:
        raise HTTPException(status_code=400, detail="Rango de fechas inválido")

    servicios = db.query(EncamamientoModel).filter(
        EncamamientoModel.activo == True
    ).order_by(EncamamientoModel.nombre_servicio).all()

    rows = db.execute(text("""
        SELECT servicio_id,
               SUM(camas_ocupadas) AS total_dco,
               SUM(egresos_totales) AS total_egresos
        FROM censo_camas
        WHERE fecha >= :desde AND fecha <= :hasta
        GROUP BY servicio_id
    """), {"desde": desde, "hasta": hasta}).mappings().all()

    agg: dict[int, dict] = {}
    for row in rows:
        agg[row["servicio_id"]] = {
            "dco": int(row["total_dco"] or 0),
            "egresos": int(row["total_egresos"] or 0),
        }

    servicios_stats = []
    global_dco = 0
    global_egresos = 0
    global_camas = 0

    for svc in servicios:
        data = agg.get(svc.id, {"dco": 0, "egresos": 0})
        camas_capacidad = svc.camas_censables * dias_en_rango
        dco = data["dco"]
        egresos = data["egresos"]
        dcd = max(camas_capacidad - dco, 0)
        porcentaje = round((dco / camas_capacidad) * 100, 1) if camas_capacidad > 0 else 0.0
        estancia = round(dco / egresos, 1) if egresos > 0 else 0.0
        rotacion = round(egresos / dcd, 1) if dcd > 0 else 0.0

        servicios_stats.append({
            "servicio_id": svc.id,
            "servicio_nombre": svc.nombre_servicio,
            "camas_censables": svc.camas_censables,
            "dias_en_rango": dias_en_rango,
            "dco": dco,
            "egresos_totales": egresos,
            "porcentaje_ocupacion": porcentaje,
            "dcd": dcd,
            "dias_estancia": estancia,
            "rotacion": rotacion,
        })

        global_dco += dco
        global_egresos += egresos
        global_camas += svc.camas_censables

    global_capacidad = global_camas * dias_en_rango
    global_dcd = max(global_capacidad - global_dco, 0)
    global_porcentaje = round((global_dco / global_capacidad) * 100, 1) if global_capacidad > 0 else 0.0
    global_estancia = round(global_dco / global_egresos, 1) if global_egresos > 0 else 0.0
    global_rotacion = round(global_egresos / global_dcd, 1) if global_dcd > 0 else 0.0

    return {
        "desde": desde,
        "hasta": hasta,
        "servicios": servicios_stats,
        "global": {
            "camas_censables_total": global_camas,
            "dias_en_rango": dias_en_rango,
            "dco": global_dco,
            "egresos_totales": global_egresos,
            "porcentaje_ocupacion": global_porcentaje,
            "dcd": global_dcd,
            "dias_estancia": global_estancia,
            "rotacion": global_rotacion,
        },
    }


_SEXO_MAP = {"m": 0, "f": 1, "masculino": 0, "femenino": 1, "0": 0, "1": 1}


def _parse_sexo(val: str) -> int:
    key = val.strip().lower()
    if key in _SEXO_MAP:
        return _SEXO_MAP[key]
    raise ValueError(f"Sexo inválido: '{val}'. Use 0/M/Masculino o 1/F/Femenino")


def importar_csv(contenido_csv: str, db: Session) -> dict:
    from modules.encamamiento.models import EncamamientoModel

    servicios_map: dict[str, int] = {}
    svcs = db.query(EncamamientoModel).filter(
        EncamamientoModel.activo == True
    ).all()
    for s in svcs:
        servicios_map[s.nombre_servicio.upper().strip()] = s.id

    reader = csv.DictReader(io.StringIO(contenido_csv))

    campos_requeridos = {"fecha", "servicio_nombre", "sexo", "ocupados", "egresos",
                         "fallecidos", "referido", "traslado", "contraindicados",
                         "otro_ingresos", "ingresos", "huespedes", "emergencia"}
    if not campos_requeridos.issubset(set(reader.fieldnames or [])):
        faltantes = campos_requeridos - set(reader.fieldnames or [])
        raise HTTPException(
            status_code=400,
            detail=f"Faltan columnas en el CSV: {', '.join(faltantes)}"
        )

    agrupados: dict[tuple[date, int], dict] = {}
    errores = []

    for i, row in enumerate(reader, start=2):
        try:
            fecha = date.fromisoformat(row["fecha"].strip())
            servicio_nombre = row["servicio_nombre"].strip().upper()
            sexo = _parse_sexo(row["sexo"])

            servicio_id = servicios_map.get(servicio_nombre)
            if not servicio_id:
                errores.append({"fila": i, "error": f"Servicio no encontrado: '{row['servicio_nombre']}'"})
                continue

            values = {field: int(row[field]) for field in _RAW_FIELDS}
            key = (fecha, servicio_id)
            combined = agrupados.setdefault(key, {
                "fecha": fecha,
                "servicio_id": servicio_id,
                "masculino": {field: 0 for field in _RAW_FIELDS},
                "femenino": {field: 0 for field in _RAW_FIELDS},
            })
            combined[_SEXES[sexo]] = values

        except HTTPException:
            raise
        except Exception as e:
            errores.append({"fila": i, "error": str(e)})

    creados, actualizados = _persistir_por_fecha_servicio(agrupados, db)

    return {
        "creados": creados,
        "actualizados": actualizados,
        "errores": errores,
    }


def _persistir_por_fecha_servicio(agrupados: dict, db: Session) -> tuple[int, int]:
    """Inserta o actualiza cada grupo por su clave natural (fecha, servicio_id)."""
    creados = 0
    actualizados = 0
    for values in agrupados.values():
        data = CensoCamasCreate(**values)
        existe = db.query(CensoCamasModel).filter(
            CensoCamasModel.fecha == data.fecha,
            CensoCamasModel.servicio_id == data.servicio_id,
        ).first()
        if existe:
            for key, value in _build_model(data).items():
                if key not in ("fecha", "servicio_id"):
                    setattr(existe, key, value)
            actualizados += 1
        else:
            db.add(CensoCamasModel(**_build_model(data)))
            creados += 1

    if creados or actualizados:
        db.commit()

    return creados, actualizados


def hospitalizacion_por_especialidad(desde: date, hasta: date, db: Session) -> dict:
    """Hospitalizaciones activas (tipo_consulta=2) agrupadas por especialidad.

    Cruza `consultas` activas con `pacientes` (sexo, días de estancia) y
    `especialidades`. Además intenta asociar cada especialidad a un servicio de
    encamamiento comparando `consultas.servicio` (texto) contra
    `encamamiento.nombre_servicio` (catálogo) de forma case-insensitive.
    """
    from modules.encamamiento.models import EncamamientoModel

    rows = db.execute(text("""
        SELECT
            COALESCE(e.nombre, c.especialidad, 'Sin especialidad') AS especialidad,
            COUNT(*) FILTER (WHERE p.sexo = 'M') AS masculinos,
            COUNT(*) FILTER (WHERE p.sexo = 'F') AS femeninos,
            COUNT(*) AS total,
            COALESCE(AVG(CURRENT_DATE - c.fecha_consulta), 0) AS dias_promedio,
            c.servicio
        FROM consultas c
        JOIN pacientes p ON p.id = c.paciente_id
        LEFT JOIN especialidades e ON e.id = c.especialidad_id
        WHERE c.tipo_consulta = 2
          AND c.activo = true
          AND c.fecha_consulta BETWEEN :desde AND :hasta
        GROUP BY COALESCE(e.nombre, c.especialidad, 'Sin especialidad'), c.servicio
        ORDER BY COUNT(*) DESC
    """), {"desde": desde, "hasta": hasta}).mappings().all()

    servicios = db.query(EncamamientoModel).filter(
        EncamamientoModel.activo == True
    ).all()
    norm: dict[str, str] = {}
    for svc in servicios:
        clave = svc.nombre_servicio.upper().strip()
        norm.setdefault(clave, svc.nombre_servicio)

    def _match_servicio(servicio_texto: Optional[str]) -> Optional[str]:
        if not servicio_texto:
            return None
        clave = servicio_texto.upper().strip()
        if clave in norm:
            return norm[clave]
        for k, nombre in norm.items():
            if clave in k or k in clave:
                return nombre
        return None

    agrupado: dict[str, dict] = {}
    for r in rows:
        esp = str(r["especialidad"])
        entry = agrupado.setdefault(esp, {
            "especialidad": esp,
            "masculinos": 0,
            "femeninos": 0,
            "total": 0,
            "dias_promedio_estancia": 0.0,
            "servicio_encamamiento": None,
        })
        entry["masculinos"] += int(r["masculinos"] or 0)
        entry["femeninos"] += int(r["femeninos"] or 0)
        entry["total"] += int(r["total"] or 0)
        dias = float(r["dias_promedio"] or 0)
        entry["dias_promedio_estancia"] = dias
        if entry["servicio_encamamiento"] is None:
            entry["servicio_encamamiento"] = _match_servicio(r["servicio"])

    especialidades = [dict(a) for a in agrupado.values()]
    total_hospitalizados = sum(int(e["total"]) for e in especialidades)

    return {
        "desde": desde,
        "hasta": hasta,
        "total_hospitalizados": total_hospitalizados,
        "especialidades": especialidades,
    }


def copiar_dia_anterior(origen: date, destino: date, servicio_id: Optional[int], db: Session) -> dict:
    """Copia registros de censo de una fecha origen a una fecha destino.

    - Si el par (destino, servicio) ya existe, se actualiza con los valores del origen.
    - Si no existe, se crea.
    - `servicio_id` opcional: si se omite, se copian todos los servicios del día origen.
    """
    query = db.query(CensoCamasModel).filter(CensoCamasModel.fecha == origen)
    if servicio_id:
        query = query.filter(CensoCamasModel.servicio_id == servicio_id)
    origen_rows = query.all()

    copiados = 0
    actualizados = 0

    for src in origen_rows:
        existe = db.query(CensoCamasModel).filter(
            CensoCamasModel.fecha == destino,
            CensoCamasModel.servicio_id == src.servicio_id,
        ).first()

        by_sex = {
            sexo: {field: getattr(src, f"{field}_{sexo}") for field in _RAW_FIELDS}
            for sexo in _SEXES
        }
        datos = {
            f"{field}_{sexo}": value
            for sexo, values in by_sex.items()
            for field, value in values.items()
        }
        datos.update(_aggregate_values(by_sex["masculino"], by_sex["femenino"]))

        if existe:
            for key, value in datos.items():
                setattr(existe, key, value)
            actualizados += 1
        else:
            nuevo = CensoCamasModel(
                fecha=destino,
                servicio_id=src.servicio_id,
                **datos,
            )
            db.add(nuevo)
            copiados += 1

    if copiados or actualizados:
        db.commit()

    return {
        "origen": origen,
        "destino": destino,
        "copiados": copiados,
        "actualizados": actualizados,
        "sin_datos": 0 if (copiados or actualizados) else len(origen_rows),
    }


# ── CSV transversal: dos filas de encabezado y una fila por variable ──────
#
# La hoja viene en formato matriz, no en el formato largo de `importar_csv`:
#
#   fila 1: Masculino Femenino Masculino Femenino ...   (sexo por columna)
#   fila 2: FECHA  VARIABLE  MADRE CANGURO MADRE CANGURO UCIA UCIA ...
#   fila 3+: 1/01/2026  Cama Ocupada  0  0  1  5 ...
#
# El nombre del servicio se propaga hacia adelante (celdas repetidas), así que
# Ginecología y Maternidad ocupan una sola columna (Femenino) mientras el resto
# ocupa una por sexo.

_CSV_CAMPOS = {
    "ocupados": "ocupados",
    "egresos": "egresos",
    "fallecidos": "fallecidos",
    "referido": "referido",
    "traslado": "traslado",
    "contraindicados": "contraindicados",
    "otro ingresos": "otro_ingresos",
    "ingresos": "ingresos",
    "huespedes": "huespedes",
    "emergencia": "emergencia",
}

# La hoja trae "Cama Ocupada" y "Egresos Totales" como filas propias, pero la
# tabla los deriva de los movimientos; se descartan para no duplicar la fuente.
_CSV_CAMPOS_DERIVADOS = {
    "cama ocupada", "camas ocupadas", "egresos totales", "egreso total",
}

_CSV_SEXOS = {
    "m": "masculino", "masculino": "masculino", "hombres": "masculino", "varones": "masculino",
    "f": "femenino", "femenino": "femenino", "mujeres": "femenino", "femeninas": "femenino",
}

# El CSV nombra los servicios con su nombre completo y el catálogo de
# encamamiento usa códigos cortos. Sin este mapa, solo coincidiría UCIA.
_CSV_SERVICIOS = {
    "madre canguro": "CANGURO",
    "canguro": "CANGURO",
    "canguro madre": "CANGURO",
    "ucia": "UCIA",
    "medicina": "MEDI",
    "medicina general": "MEDI",
    "cirugia": "CIRU",
    "cirugia general": "CIRU",
    "pediatria cirugia": "CIRU PEDIA",
    "cirugia pediatrica": "CIRU PEDIA",
    "traumatologia": "TRAUMA",
    "traumatologia general": "TRAUMA",
    "pediatria trauma": "TRAUMA PEDIA",
    "traumatologia pediatrica": "TRAUMA PEDIA",
    "ginecologia": "GINE",
    "ginecologia obstetricia": "GINE",
    "obstetricia": "GINE",
    "maternidad": "MATER",
    "pediatria": "PEDIA",
    "neonatos": "NEO",
    "neonatologia": "NEO",
    "neonatos canguro": "NEO",
    "ucin": "UCIN",
    "crn": "CRN",
    "cuidados intermedio": "CRN",
    "cuidados intensivos": "CRN",
}

_CSV_ETIQUETAS_IGNORADAS = {"", "total", "totales", "total general", "suma"}

# Un servicio reportado en una sola columna no permite deducir el sexo por
# posición. Ginecología y Maternidad no tienen camas masculinas, así que el valor
# por defecto es Femenino; el importador lo reporta en `advertencias`.
_CSV_SEXO_UNICOLUMNA = "femenino"


def _normalizar_texto(valor: str) -> str:
    """Minúsculas, sin acentos y con espacios colapsados, para comparar nombres."""
    valor = unicodedata.normalize("NFD", (valor or "").strip().lower())
    valor = "".join(c for c in valor if unicodedata.category(c) != "Mn")
    return " ".join(valor.split())


def _parse_fecha_censo(valor: str) -> Optional[date]:
    """Acepta el formato dd/mm/aaaa de la hoja (1/01/2026) además de ISO."""
    valor = (valor or "").strip()
    if not valor:
        return None
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(valor, fmt).date()
        except ValueError:
            continue
    return None


def _parse_entero_censo(valor: str) -> Optional[int]:
    """Devuelve 0 para celdas vacías y None para contenido no numérico."""
    valor = (valor or "").strip()
    if not valor:
        return 0
    try:
        return int(float(valor))
    except ValueError:
        return None


def _resolver_servicios_transversal(
    nombres: list[str], db: Session
) -> tuple[dict[str, int], list[str]]:
    """Traduce los nombres largos del CSV a los códigos de `encamamiento`."""
    from modules.encamamiento.models import EncamamientoModel

    catalogo = {
        _normalizar_texto(s.nombre_servicio): s.id
        for s in db.query(EncamamientoModel).filter(EncamamientoModel.activo == True).all()
    }
    resoltos: dict[str, int] = {}
    faltantes: list[str] = []
    for nombre in nombres:
        clave = _normalizar_texto(nombre)
        if clave in resoltos or clave in faltantes:
            continue
        servicio_id = catalogo.get(clave) or catalogo.get(_normalizar_texto(_CSV_SERVICIOS.get(clave, "")))
        if servicio_id:
            resoltos[clave] = servicio_id
        else:
            faltantes.append(nombre)
    return resoltos, faltantes


def _columnas_transversal(filas: list[list[str]]) -> tuple[list[tuple[str, str, int]], list[str]]:
    """Devuelve (servicio_csv, sexo, índice en la fila de datos) por columna.

    El sexo se toma de la posición dentro del bloque del servicio: cada servicio
    ocupa dos columnas (Masculino y Femenino) salvo los que la hoja reporta en una
    sola. La fila de sexo solo interviene para esos bloques de una columna, y
    únicamente si tiene el mismo ancho que la fila de servicio; si viene recortada
    o desalineada se descarta y el bloque usa el valor por defecto.
    """
    nombres = filas[1][2:]
    alineado = len(filas[0]) == len(filas[1])
    etiquetas = filas[0][2:] if alineado else []

    indices: list[tuple[str, int]] = []
    servicio_actual = ""
    for i in range(len(nombres)):
        nombre = (nombres[i] or "").strip()
        if nombre:
            servicio_actual = nombre
        if not servicio_actual:
            continue
        indices.append((servicio_actual, i))

    sexos: dict[int, str] = {}
    unicolumna: list[str] = []
    inicio = 0
    for fin in range(1, len(indices) + 1):
        if fin < len(indices) and indices[fin][0] == indices[inicio][0]:
            continue
        bloque = list(range(inicio, fin))
        for posicion, idx in enumerate(bloque):
            if len(bloque) > 1:
                sexos[idx] = "masculino" if posicion == 0 else "femenino"
            elif etiquetas and idx < len(etiquetas):
                sexos[idx] = _CSV_SEXOS.get(_normalizar_texto(etiquetas[idx]), _CSV_SEXO_UNICOLUMNA)
            else:
                sexos[idx] = _CSV_SEXO_UNICOLUMNA
                servicio = indices[idx][0]
                if servicio not in unicolumna:
                    unicolumna.append(servicio)
        inicio = fin

    columnas = [(servicio, sexos[idx], idx) for servicio, idx in indices]
    return columnas, unicolumna


def importar_csv_transversal(contenido_csv: str, db: Session) -> dict:
    """Importa la hoja de censo en formato matriz (dos encabezados + una fila por variable).

    A diferencia de `importar_csv`, el servicio y el sexo son columnas y la
    variable es la fila. `camas_ocupadas` y `egresos_totales` se recalculan con
    las fórmulas de la tabla: las filas homónimas del CSV se descartan.
    """
    if not contenido_csv.strip():
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    try:
        sep = csv.Sniffer().sniff(contenido_csv[:8192], delimiters="\t;,").delimiter
    except csv.Error:
        # Con una sola columna por fila el detector no tiene nada que decidir, así
        # que se gana el separador que más se repite en las primeras líneas.
        lineas = [l for l in contenido_csv.splitlines() if l.strip()][:20]
        conteo = {d: max((l.count(d) for l in lineas), default=0) for d in "\t;,"}
        sep = max(conteo, key=lambda d: conteo[d]) if max(conteo.values()) else "\t"

    filas = [r for r in csv.reader(io.StringIO(contenido_csv), delimiter=sep) if r]
    if len(filas) < 3:
        raise HTTPException(
            status_code=400,
            detail="Se esperaban dos filas de encabezado y al menos una de datos",
        )
    if _normalizar_texto(filas[1][0]) != "fecha" or _normalizar_texto(filas[1][1]) != "variable":
        raise HTTPException(
            status_code=400,
            detail="La segunda fila debe comenzar con FECHA y VARIABLE",
        )

    columnas, unicolumna = _columnas_transversal(filas)
    if not columnas:
        raise HTTPException(status_code=400, detail="No se detectaron columnas de servicio")

    servicios, faltantes = _resolver_servicios_transversal(
        [s for s, _, _ in columnas], db
    )

    agrupados: dict[tuple[date, int], dict] = {}
    errores: list[dict] = []
    advertencias: list[str] = []
    variables_ignoradas: set[str] = set()
    celdas_invalidas = 0

    for num_fila, fila in enumerate(filas[2:], start=3):
        original = (fila[1] if len(fila) > 1 else "").strip()
        etiqueta = _normalizar_texto(original)
        if etiqueta in _CSV_ETIQUETAS_IGNORADAS:
            continue
        campo = _CSV_CAMPOS.get(etiqueta)
        if campo is None:
            if etiqueta not in _CSV_CAMPOS_DERIVADOS and etiqueta not in variables_ignoradas:
                variables_ignoradas.add(etiqueta)
                advertencias.append(f"VARIABLE '{original}' no reconocida; se ignora")
            continue

        fecha = _parse_fecha_censo(fila[0] if fila else "")
        if fecha is None:
            errores.append({"fila": num_fila, "error": f"Fecha inválida: '{(fila[0] or '').strip()}'"})
            continue

        for nombre, sexo, idx in columnas:
            servicio_id = servicios.get(_normalizar_texto(nombre))
            if not servicio_id:
                continue
            valor = _parse_entero_censo(fila[idx + 2] if idx + 2 < len(fila) else "")
            if valor is None:
                celdas_invalidas += 1
                continue
            clave = (fecha, servicio_id)
            grupo = agrupados.get(clave)
            if grupo is None:
                grupo = agrupados[clave] = {
                    "fecha": fecha,
                    "servicio_id": servicio_id,
                    "masculino": {field: 0 for field in _RAW_FIELDS},
                    "femenino": {field: 0 for field in _RAW_FIELDS},
                }
            grupo[sexo][campo] = valor

    if faltantes:
        advertencias.append(
            "Servicios del CSV sin coincidencia en el catálogo de encamamiento, se omiten: "
            + ", ".join(dict.fromkeys(faltantes))
        )
    if unicolumna:
        advertencias.append(
            f"Servicios con una sola columna, asignados a {_CSV_SEXO_UNICOLUMNA.upper()}: "
            + ", ".join(dict.fromkeys(unicolumna))
        )
    if celdas_invalidas:
        advertencias.append(f"{celdas_invalidas} celdas no numéricas se trataron como 0")
    if not agrupados:
        raise HTTPException(
            status_code=400,
            detail="No se encontraron filas de datos válidas. Revise las advertencias del archivo",
        )

    creados, actualizados = _persistir_por_fecha_servicio(agrupados, db)
    return {
        "creados": creados,
        "actualizados": actualizados,
        "fechas": len({fecha for fecha, _ in agrupados}),
        "servicios": len(servicios),
        "errores": errores,
        "advertencias": advertencias,
    }
