from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from datetime import date
import csv
import io

from modules.censo_camas.models import CensoCamasModel
from modules.censo_camas.schemas import CensoCamasCreate, CensoCamasUpdate


def _calc_egresos_totales(egresos: int, fallecidos: int, referido: int, traslado: int, contraindicados: int) -> int:
    return egresos + fallecidos + referido + traslado + contraindicados


def _calc_camas_ocupadas(ocupados: int, otro_ingresos: int, ingresos: int, huespedes: int, emergencia: int, egresos_totales: int) -> int:
    return (emergencia + huespedes + ingresos + otro_ingresos + ocupados) - egresos_totales


def _to_out(r: CensoCamasModel) -> dict:
    egresos_totales = _calc_egresos_totales(r.egresos, r.fallecidos, r.referido, r.traslado, r.contraindicados)
    camas_ocupadas = _calc_camas_ocupadas(r.ocupados, r.otro_ingresos, r.ingresos, r.huespedes, r.emergencia, egresos_totales)
    return {
        "id": r.id,
        "fecha": r.fecha,
        "servicio_id": r.servicio_id,
        "sexo": r.sexo,
        "ocupados": r.ocupados,
        "camas_ocupadas": camas_ocupadas,
        "egresos_totales": egresos_totales,
        "egresos": r.egresos,
        "fallecidos": r.fallecidos,
        "referido": r.referido,
        "traslado": r.traslado,
        "contraindicados": r.contraindicados,
        "otro_ingresos": r.otro_ingresos,
        "ingresos": r.ingresos,
        "huespedes": r.huespedes,
        "emergencia": r.emergencia,
        "created_at": r.created_at,
        "updated_at": r.updated_at,
    }


def _build_model(data: CensoCamasCreate) -> dict:
    d = data.model_dump()
    egresos_totales = _calc_egresos_totales(
        d["egresos"], d["fallecidos"], d["referido"], d["traslado"], d["contraindicados"]
    )
    d["egresos_totales"] = egresos_totales
    d["camas_ocupadas"] = _calc_camas_ocupadas(
        d["ocupados"], d["otro_ingresos"], d["ingresos"], d["huespedes"], d["emergencia"], egresos_totales
    )
    return d


def crear_registro(data: CensoCamasCreate, db: Session) -> dict:
    existe = db.query(CensoCamasModel).filter(
        CensoCamasModel.fecha == data.fecha,
        CensoCamasModel.servicio_id == data.servicio_id,
        CensoCamasModel.sexo == data.sexo,
    ).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un registro para esa fecha, servicio y sexo"
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
        CensoCamasModel.sexo == data.sexo,
    ).first()
    if existe:
        d = data.model_dump(exclude_unset=True)
        campos_actualizables = {k: v for k, v in d.items() if k not in ("fecha", "servicio_id", "sexo")}
        for key, value in campos_actualizables.items():
            setattr(existe, key, value)
        existe.egresos_totales = _calc_egresos_totales(
            existe.egresos, existe.fallecidos, existe.referido, existe.traslado, existe.contraindicados
        )
        existe.camas_ocupadas = _calc_camas_ocupadas(
            existe.ocupados, existe.otro_ingresos, existe.ingresos, existe.huespedes, existe.emergencia, existe.egresos_totales
        )
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
    sexo: Optional[int] = None,
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
    if sexo is not None:
        query = query.filter(CensoCamasModel.sexo == sexo)
        count_query = count_query.filter(CensoCamasModel.sexo == sexo)

    total = count_query.scalar()
    limit = min(limit, 500)
    registros = query.order_by(
        CensoCamasModel.fecha.desc(),
        CensoCamasModel.servicio_id,
        CensoCamasModel.sexo,
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
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(registro, key, value)
    registro.egresos_totales = _calc_egresos_totales(
        registro.egresos, registro.fallecidos, registro.referido, registro.traslado, registro.contraindicados
    )
    registro.camas_ocupadas = _calc_camas_ocupadas(
        registro.ocupados, registro.otro_ingresos, registro.ingresos, registro.huespedes, registro.emergencia, registro.egresos_totales
    )
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


def resumen_diario(fecha: date, db: Session) -> dict:
    from modules.encamamiento.models import EncamamientoModel

    servicios = db.query(EncamamientoModel).filter(
        EncamamientoModel.activo == True
    ).order_by(EncamamientoModel.nombre_servicio).all()

    registros = db.query(CensoCamasModel).filter(
        CensoCamasModel.fecha == fecha
    ).all()

    reg_map: dict[tuple[int, int], CensoCamasModel] = {}
    for r in registros:
        reg_map[(r.servicio_id, r.sexo)] = r

    total_ocupados = 0
    servicios_resumen = []

    for svc in servicios:
        masc = reg_map.get((svc.id, 0))
        fem = reg_map.get((svc.id, 1))
        ocupados_m = masc.ocupados if masc else 0
        ocupados_f = fem.ocupados if fem else 0
        total_ocupados += ocupados_m + ocupados_f

        servicios_resumen.append({
            "servicio_id": svc.id,
            "servicio_nombre": svc.nombre_servicio,
            "camas_censables": svc.camas_censables,
            "masculino": _to_out(masc) if masc else None,
            "femenino": _to_out(fem) if fem else None,
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

    for data in registros:
        try:
            existe = db.query(CensoCamasModel).filter(
                CensoCamasModel.fecha == data.fecha,
                CensoCamasModel.servicio_id == data.servicio_id,
                CensoCamasModel.sexo == data.sexo,
            ).first()
            if existe:
                d = data.model_dump(exclude_unset=True)
                campos = {k: v for k, v in d.items() if k not in ("fecha", "servicio_id", "sexo")}
                for key, value in campos.items():
                    setattr(existe, key, value)
                existe.egresos_totales = _calc_egresos_totales(
                    existe.egresos, existe.fallecidos, existe.referido, existe.traslado, existe.contraindicados
                )
                existe.camas_ocupadas = _calc_camas_ocupadas(
                    existe.ocupados, existe.otro_ingresos, existe.ingresos, existe.huespedes, existe.emergencia, existe.egresos_totales
                )
                actualizados += 1
            else:
                registro = CensoCamasModel(**_build_model(data))
                db.add(registro)
                creados += 1
        except Exception as e:
            db.rollback()
            errores.append({
                "fecha": str(data.fecha),
                "servicio_id": data.servicio_id,
                "sexo": data.sexo,
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

    creados = 0
    actualizados = 0
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

            data = CensoCamasCreate(
                fecha=fecha,
                servicio_id=servicio_id,
                sexo=sexo,
                ocupados=int(row["ocupados"]),
                egresos=int(row["egresos"]),
                fallecidos=int(row["fallecidos"]),
                referido=int(row["referido"]),
                traslado=int(row["traslado"]),
                contraindicados=int(row["contraindicados"]),
                otro_ingresos=int(row["otro_ingresos"]),
                ingresos=int(row["ingresos"]),
                huespedes=int(row["huespedes"]),
                emergencia=int(row["emergencia"]),
            )

            existe = db.query(CensoCamasModel).filter(
                CensoCamasModel.fecha == data.fecha,
                CensoCamasModel.servicio_id == data.servicio_id,
                CensoCamasModel.sexo == data.sexo,
            ).first()

            if existe:
                existe.ocupados = data.ocupados
                existe.egresos = data.egresos
                existe.fallecidos = data.fallecidos
                existe.referido = data.referido
                existe.traslado = data.traslado
                existe.contraindicados = data.contraindicados
                existe.otro_ingresos = data.otro_ingresos
                existe.ingresos = data.ingresos
                existe.huespedes = data.huespedes
                existe.emergencia = data.emergencia
                existe.egresos_totales = _calc_egresos_totales(
                    data.egresos, data.fallecidos, data.referido, data.traslado, data.contraindicados
                )
                existe.camas_ocupadas = _calc_camas_ocupadas(
                    data.ocupados, data.otro_ingresos, data.ingresos, data.huespedes, data.emergencia, existe.egresos_totales
                )
                actualizados += 1
            else:
                registro = CensoCamasModel(**_build_model(data))
                db.add(registro)
                creados += 1

        except HTTPException:
            raise
        except Exception as e:
            errores.append({"fila": i, "error": str(e)})

    if creados or actualizados:
        db.commit()

    return {
        "creados": creados,
        "actualizados": actualizados,
        "errores": errores,
    }
