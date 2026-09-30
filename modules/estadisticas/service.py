from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from core.config import APP_TIMEZONE

from modules.consultas.models import ConsultaModel
from modules.pacientes.models import PacienteModel
from modules.consultas.schemas import ConsultaListResponse


TIPO_CONSULTA_MAP = {1: "COEX", 2: "Hospitalización", 3: "Emergencia"}


def _parse_fechas(desde: str, hasta: str) -> tuple[date, date]:
    """Valida fechas ISO; los reportes aplican ambos extremos del rango de forma inclusiva."""
    try:
        return (
            datetime.strptime(desde, "%Y-%m-%d").date(),
            datetime.strptime(hasta, "%Y-%m-%d").date(),
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")


def pacientes_atendidos(db: Session, desde: str, hasta: str) -> dict:
    f_desde, f_hasta = _parse_fechas(desde, hasta)

    rows = db.execute(text("""
        SELECT
            c.tipo_consulta,
            c.especialidad,
            p.sexo,
            COUNT(*) AS total
        FROM consultas c
        JOIN pacientes p ON p.id = c.paciente_id
        WHERE c.fecha_consulta BETWEEN :desde AND :hasta
          AND p.sexo IN ('M', 'F')
        GROUP BY c.tipo_consulta, c.especialidad, p.sexo
        ORDER BY c.tipo_consulta, c.especialidad, p.sexo
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    datos = []
    total_general = 0
    for r in rows:
        m = r._mapping
        tc = int(m["tipo_consulta"])
        total = int(m["total"])
        total_general += total
        datos.append({
            "tipo_consulta": tc,
            "tipo_consulta_nombre": TIPO_CONSULTA_MAP.get(tc, f"Tipo {tc}"),
            "especialidad": str(m["especialidad"]),
            "sexo": str(m["sexo"]),
            "total": total,
        })

    return {
        "titulo": "Pacientes Atendidos por Tipo, Especialidad y Sexo",
        "desde": f_desde,
        "hasta": f_hasta,
        "datos": datos,
        "total_general": total_general,
        "generado_en": datetime.now(APP_TIMEZONE).isoformat(),
    }


def hospitalizacion_infantil(db: Session, desde: str, hasta: str) -> dict:
    f_desde, f_hasta = _parse_fechas(desde, hasta)

    rows = db.execute(text("""
        SELECT
            c.especialidad,
            p.sexo,
            COUNT(*) AS total
        FROM consultas c
        JOIN pacientes p ON p.id = c.paciente_id
        WHERE c.tipo_consulta = 2
          AND c.fecha_consulta BETWEEN :desde AND :hasta
          AND p.fecha_nacimiento IS NOT NULL
          AND p.sexo IN ('M', 'F')
          AND AGE(c.fecha_consulta, p.fecha_nacimiento) > INTERVAL '28 days'
          AND AGE(c.fecha_consulta, p.fecha_nacimiento) < INTERVAL '5 years'
        GROUP BY c.especialidad, p.sexo
        ORDER BY c.especialidad, p.sexo
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    datos = []
    total_general = 0
    for r in rows:
        m = r._mapping
        total = int(m["total"])
        total_general += total
        datos.append({
            "especialidad": str(m["especialidad"]),
            "sexo": str(m["sexo"]),
            "total": total,
        })

    return {
        "titulo": "Hospitalizaciones Infantiles (>28 días y <5 años)",
        "desde": f_desde,
        "hasta": f_hasta,
        "datos": datos,
        "total_general": total_general,
        "generado_en": datetime.now(APP_TIMEZONE).isoformat(),
    }


def promedio_diario(db: Session, desde: str, hasta: str) -> dict:
    f_desde, f_hasta = _parse_fechas(desde, hasta)

    esp_rows = db.execute(text("""
        SELECT
            especialidad,
            COUNT(*) AS total_consultas,
            COUNT(DISTINCT fecha_consulta) AS dias_con_registros
        FROM consultas
        WHERE fecha_consulta BETWEEN :desde AND :hasta
        GROUP BY especialidad
        ORDER BY especialidad
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    tipo_rows = db.execute(text("""
        SELECT
            especialidad,
            tipo_consulta,
            COUNT(*) AS total,
            COUNT(DISTINCT fecha_consulta) AS dias_con_registros
        FROM consultas
        WHERE fecha_consulta BETWEEN :desde AND :hasta
        GROUP BY especialidad, tipo_consulta
        ORDER BY especialidad, tipo_consulta
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    tipo_map: dict[str, list] = {}
    for r in tipo_rows:
        m = r._mapping
        esp = str(m["especialidad"])
        tc = int(m["tipo_consulta"])
        total = int(m["total"])
        dias = int(m["dias_con_registros"])
        tipo_map.setdefault(esp, []).append({
            "tipo_consulta": tc,
            "tipo_consulta_nombre": TIPO_CONSULTA_MAP.get(tc, f"Tipo {tc}"),
            "total": total,
            "dias_con_registros": dias,
            "promedio_diario": round(total / dias, 2) if dias > 0 else 0.0,
        })

    datos = []
    total_general = 0
    for r in esp_rows:
        m = r._mapping
        esp = str(m["especialidad"])
        total_consultas = int(m["total_consultas"])
        dias = int(m["dias_con_registros"])
        total_general += total_consultas
        datos.append({
            "especialidad": esp,
            "total_consultas": total_consultas,
            "dias_con_registros": dias,
            "promedio_diario": round(total_consultas / dias, 2) if dias > 0 else 0.0,
            "por_tipo": tipo_map.get(esp, []),
        })

    return {
        "titulo": "Promedio Diario de Consultas",
        "desde": f_desde,
        "hasta": f_hasta,
        "datos": datos,
        "total_general": total_general,
        "generado_en": datetime.now(APP_TIMEZONE).isoformat(),
    }


def _sigsa3_por_grupo(
    db: Session, desde: str, hasta: str,
    campo_filtro: str, valor_filtro: str,
    titulo: str,
    skip: int = 0, limit: int = 100,
) -> dict:
    """Genérico para consultas SIGSA-3 filtradas por campo de pacientes."""
    f_desde, f_hasta = _parse_fechas(desde, hasta)
    limit = min(limit, 500)

    where_extra = f"AND p.{campo_filtro} = :valor_filtro"

    rows = db.execute(text(f"""
        SELECT
            p.nombre,
            p.nombre_completo,
            p.expediente,
            r.tipo_consulta_id AS tipo_consulta,
            p.sexo,
            p.fecha_nacimiento,
            r.fecha_consulta,
            COALESCE(e.nombre, '—') AS especialidad,
            c.documento,
            r.paciente_id,
            CASE WHEN cie.codigo IS NOT NULL
                 THEN cie.codigo || COALESCE(' - ' || cie.descripcion, '')
            END AS diagnostico
        FROM sigsa3_registros r
        JOIN pacientes p ON p.id = r.paciente_id
        LEFT JOIN especialidades e ON e.id = r.especialidad_id
        LEFT JOIN cie10_catalogo cie ON cie.id = r.codigo_cie_10_id
        LEFT JOIN consultas c ON c.id = r.consulta_id
        WHERE r.fecha_consulta BETWEEN :desde AND :hasta
          {where_extra}
        ORDER BY r.fecha_consulta, r.id
        LIMIT :limit OFFSET :skip
    """), {"desde": f_desde, "hasta": f_hasta, "valor_filtro": valor_filtro, "limit": limit, "skip": skip}).fetchall()

    datos = []
    for r in rows:
        m = r._mapping
        tc = int(m["tipo_consulta"])
        edad = None
        if m["fecha_nacimiento"] and m["fecha_consulta"]:
            edad = (m["fecha_consulta"] - m["fecha_nacimiento"]).days // 365
        datos.append({
            "nombre": m["nombre"] if m["nombre"] else None,
            "nombre_completo": m["nombre_completo"],
            "expediente": str(m["expediente"]) if m["expediente"] else None,
            "tipo_consulta": tc,
            "tipo_consulta_nombre": TIPO_CONSULTA_MAP.get(tc, f"Tipo {tc}"),
            "sexo": str(m["sexo"]) if m["sexo"] else None,
            "edad": edad,
            "especialidad": str(m["especialidad"]),
            "documento": str(m["documento"]) if m["documento"] else None,
            "diagnostico": str(m["diagnostico"]) if m["diagnostico"] else None,
            "paciente_id": str(m["paciente_id"]),
            "fecha_consulta": str(m["fecha_consulta"]),
        })

    total = db.execute(text(f"""
        SELECT COUNT(*)
        FROM sigsa3_registros r
        JOIN pacientes p ON p.id = r.paciente_id
        WHERE r.fecha_consulta BETWEEN :desde AND :hasta
          {where_extra}
    """), {"desde": f_desde, "hasta": f_hasta, "valor_filtro": valor_filtro}).scalar()

    return {
        "titulo": titulo,
        "desde": f_desde,
        "hasta": f_hasta,
        "datos": datos,
        "total_general": int(total) if total else 0,
        "skip": skip,
        "limit": limit,
        "generado_en": datetime.now(APP_TIMEZONE).isoformat(),
    }


def personal_hospital(db: Session, desde: str, hasta: str, skip: int = 0, limit: int = 100) -> dict:
    return _sigsa3_por_grupo(db, desde, hasta, "es_personal_hospital", "S", "Consultas de Personal del Hospital", skip, limit)


def estudiante_publico(db: Session, desde: str, hasta: str) -> dict:
    return _sigsa3_por_grupo(db, desde, hasta, "es_estudiante_publico", "S", "Consultas de Estudiantes Públicos")


def reingresos(db: Session, desde: str, hasta: str) -> dict:
    f_desde, f_hasta = _parse_fechas(desde, hasta)

    rows = db.execute(text("""
        WITH unicos AS (
            SELECT DISTINCT ON (c.paciente_id, c.fecha_consulta)
                c.paciente_id,
                c.fecha_consulta,
                c.especialidad,
                c.egreso
            FROM consultas c
            WHERE c.tipo_consulta = 2 AND c.activo = true
            ORDER BY c.paciente_id, c.fecha_consulta, c.id
        ),
        numbered AS (
            SELECT
                u.*,
                ROW_NUMBER() OVER (
                    PARTITION BY u.paciente_id ORDER BY u.fecha_consulta
                ) AS rn,
                LAG(u.fecha_consulta) OVER (
                    PARTITION BY u.paciente_id ORDER BY u.fecha_consulta
                ) AS prev_fecha_consulta,
                LAG(u.especialidad) OVER (
                    PARTITION BY u.paciente_id ORDER BY u.fecha_consulta
                ) AS prev_especialidad,
                LAG(u.egreso) OVER (
                    PARTITION BY u.paciente_id ORDER BY u.fecha_consulta
                ) AS prev_egreso
            FROM unicos u
        )
        SELECT
            p.nombre,
            p.sexo,
            p.estado,
            p.fecha_nacimiento,
            c.fecha_consulta,
            c.especialidad,
            c.prev_fecha_consulta,
            c.prev_especialidad,
            c.egreso#>>'{registro}' AS egreso_actual_registro,
            c.prev_egreso#>>'{registro}' AS egreso_registro,
            c.prev_egreso#>>'{diagnosticos}' AS diagnostico
        FROM numbered c
        JOIN pacientes p ON p.id = c.paciente_id
        WHERE c.fecha_consulta BETWEEN :desde AND :hasta
          AND c.rn > 1
        ORDER BY c.fecha_consulta
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    datos = []
    for r in rows:
        m = r._mapping
        edad = None
        if m["fecha_nacimiento"] and m["fecha_consulta"]:
            edad = (m["fecha_consulta"] - m["fecha_nacimiento"]).days // 365

        egreso_registro = str(m["egreso_registro"]) if m["egreso_registro"] else None
        dias_entre_consultas = None
        if egreso_registro and m["fecha_consulta"]:
            try:
                egreso_dt = datetime.fromisoformat(egreso_registro)
                diff = (m["fecha_consulta"] - egreso_dt.date()).days
                if diff >= 0:
                    dias_entre_consultas = diff
            except (ValueError, TypeError):
                pass
        if dias_entre_consultas is None and m["prev_fecha_consulta"] and m["fecha_consulta"]:
            diff = (m["fecha_consulta"] - m["prev_fecha_consulta"]).days
            if diff >= 0:
                dias_entre_consultas = diff
        clasificacion = None
        if dias_entre_consultas is not None:
            if dias_entre_consultas < 8:
                clasificacion = "menores a 8 dias"
            elif dias_entre_consultas < 30:
                clasificacion = "por complicaciones"

        if clasificacion is None:
            continue

        datos.append({
            "nombre": m["nombre"] if m["nombre"] else None,
            "sexo": str(m["sexo"]) if m["sexo"] else None,
            "estado": str(m["estado"]) if m["estado"] else None,
            "edad": edad,
            "fecha_consulta": m["fecha_consulta"],
            "especialidad": str(m["especialidad"]),
            "prev_fecha_consulta": m["prev_fecha_consulta"],
            "prev_especialidad": str(m["prev_especialidad"]) if m["prev_especialidad"] else None,
            "egreso_actual_registro": str(m["egreso_actual_registro"]) if m["egreso_actual_registro"] else None,
            "egreso_registro": egreso_registro,
            "diagnostico": str(m["diagnostico"]) if m["diagnostico"] else None,
            "dias_entre_consultas": dias_entre_consultas,
            "clasificacion": clasificacion,
        })

    resumen = {"menores a 8 dias": 0, "por complicaciones": 0}
    por_esp: dict[str, dict] = {}
    for d in datos:
        c = d["clasificacion"]
        if c in resumen:
            resumen[c] += 1
        esp = d["especialidad"]
        if esp not in por_esp:
            por_esp[esp] = {"menores a 8 dias": 0, "por complicaciones": 0}
        if c in por_esp[esp]:
            por_esp[esp][c] += 1

    por_especialidad = sorted(
        [
            {
                "especialidad": esp,
                "menores_a_8_dias": v["menores a 8 dias"],
                "por_complicaciones": v["por complicaciones"],
                "total": v["menores a 8 dias"] + v["por complicaciones"],
            }
            for esp, v in por_esp.items()
        ],
        key=lambda x: x["especialidad"],
    )

    return {
        "titulo": "Reingresos Hospitalarios",
        "desde": f_desde,
        "hasta": f_hasta,
        "datos": datos,
        "resumen": resumen,
        "por_especialidad": por_especialidad,
        "total_general": len(datos),
        "generado_en": datetime.now(APP_TIMEZONE).isoformat(),
    }


def estadisticas_nacimientos(db: Session, desde: str, hasta: str) -> dict:
    f_desde, f_hasta = _parse_fechas(desde, hasta)

    total = db.execute(text("""
        SELECT COUNT(*) AS total
        FROM nacimientos n
        JOIN pacientes p ON p.id = n.paciente_id
        WHERE p.fecha_nacimiento BETWEEN :desde AND :hasta
    """), {"desde": f_desde, "hasta": f_hasta}).scalar()

    rows_mortinato = db.execute(text("""
        SELECT p.sexo, n.mortinato, COUNT(*) AS total
        FROM nacimientos n
        JOIN pacientes p ON p.id = n.paciente_id
        WHERE p.fecha_nacimiento BETWEEN :desde AND :hasta
          AND p.sexo IN ('M', 'F')
        GROUP BY p.sexo, n.mortinato
        ORDER BY p.sexo, n.mortinato
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    rows_fallecidos_posteriores = db.execute(text("""
        SELECT p.sexo, p.estado, COUNT(*) AS total
        FROM nacimientos n
        JOIN pacientes p ON p.id = n.paciente_id
        WHERE p.fecha_nacimiento BETWEEN :desde AND :hasta
          AND p.sexo IN ('M', 'F')
          AND p.estado = 'F'
          AND (n.mortinato = false OR n.mortinato IS NULL)
        GROUP BY p.sexo, p.estado
        ORDER BY p.sexo, p.estado
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    rows_clase_parto = db.execute(text("""
        SELECT
            p.datos_extra#>'{neonatales,clase_parto}' AS clase_parto,
            n.mortinato,
            p.estado,
            p.sexo,
            COUNT(*) AS total
        FROM nacimientos n
        JOIN pacientes p ON p.id = n.paciente_id
        WHERE p.fecha_nacimiento BETWEEN :desde AND :hasta
          AND p.sexo IN ('M', 'F')
        GROUP BY p.datos_extra#>'{neonatales,clase_parto}', n.mortinato, p.estado, p.sexo
        ORDER BY clase_parto, n.mortinato, p.estado, p.sexo
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    rows_clasificacion_parto = db.execute(text("""
        SELECT
            n.clasificacion_nacimiento AS clasificacion_parto,
            n.mortinato,
            p.estado,
            p.sexo,
            COUNT(*) AS total
        FROM nacimientos n
        JOIN pacientes p ON p.id = n.paciente_id
        WHERE p.fecha_nacimiento BETWEEN :desde AND :hasta
          AND p.sexo IN ('M', 'F')
        GROUP BY n.clasificacion_nacimiento, n.mortinato, p.estado, p.sexo
        ORDER BY clasificacion_parto, n.mortinato, p.estado, p.sexo
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    rows_trabajo_parto = db.execute(text("""
        SELECT
            n.trabajo_parto,
            n.mortinato,
            p.estado,
            p.sexo,
            COUNT(*) AS total
        FROM nacimientos n
        JOIN pacientes p ON p.id = n.paciente_id
        WHERE p.fecha_nacimiento BETWEEN :desde AND :hasta
          AND p.sexo IN ('M', 'F')
        GROUP BY n.trabajo_parto, n.mortinato, p.estado, p.sexo
        ORDER BY n.trabajo_parto, n.mortinato, p.estado, p.sexo
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    def _build_mortinato(items, key) -> list[dict]:
        result = []
        for r in items:
            m = r._mapping
            mort_val = m["mortinato"]
            es_mortinato = isinstance(mort_val, bool) and mort_val
            if not es_mortinato and not isinstance(mort_val, bool):
                es_mortinato = str(mort_val).lower() in ("true", "1", "yes")

            if es_mortinato:
                label = "Mortinato"
            elif str(m.get("estado", "")).upper() == "F":
                label = "Fallecido"
            else:
                label = "Vivo"

            item = {"estado": label, "sexo": str(m["sexo"]), "total": int(m["total"])}
            item[key] = str(m[key]) if m.get(key) is not None else None
            result.append(item)
        return result

    por_mortinato = []
    for r in rows_mortinato:
        m = r._mapping
        mort_val = m["mortinato"]
        if isinstance(mort_val, bool):
            label = "Mortinato" if mort_val else "Vivo"
        else:
            label = "Vivo" if str(mort_val).lower() in ("false", "0", "none") else "Mortinato"
        por_mortinato.append({
            "sexo": str(m["sexo"]),
            "estado": label,
            "total": int(m["total"]),
            "mortinato": mort_val,
        })

    return {
        "titulo": "Estadísticas de Nacimientos",
        "desde": f_desde,
        "hasta": f_hasta,
        "total": int(total),
        "por_mortinato": por_mortinato,
        "por_fallecidos_posteriores": [
            {"estado": str(r._mapping["estado"]), "sexo": str(r._mapping["sexo"]), "total": int(r._mapping["total"])}
            for r in rows_fallecidos_posteriores
        ],
        "por_clase_parto": _build_mortinato(rows_clase_parto, "clase_parto"),
        "por_clasificacion_parto": _build_mortinato(rows_clasificacion_parto, "clasificacion_parto"),
        "por_trabajo_parto": _build_mortinato(rows_trabajo_parto, "trabajo_parto"),
        "generado_en": datetime.now(APP_TIMEZONE).isoformat(),
    }


# =====================================================================
# SIGSA-3 ESTADÍSTICAS
# =====================================================================
def sigsa3_por_especialidad(db: Session, desde: str, hasta: str) -> dict:
    """Consultas SIGSA-3 (normalizadas) por especialidad, tipo y sexo.
    Fuente: sigsa3_registros (listado principal/final)."""
    f_desde, f_hasta = _parse_fechas(desde, hasta)

    rows = db.execute(text("""
        SELECT
            COALESCE(e.nombre, '—') AS especialidad,
            COALESCE(tc.nombre, '—') AS tipo_consulta,
            p.sexo AS sexo,
            COUNT(*) AS total
        FROM sigsa3_registros r
        LEFT JOIN especialidades e ON e.id = r.especialidad_id
        LEFT JOIN tipos_consulta_sigsa3 tc ON tc.id = r.tipo_consulta_id
        LEFT JOIN pacientes p ON p.id = r.paciente_id
        WHERE r.fecha_consulta BETWEEN :desde AND :hasta
          AND r.especialidad_id IS NOT NULL
          AND r.tipo_consulta_id IS NOT NULL
          AND p.sexo IS NOT NULL
        GROUP BY e.nombre, tc.nombre, p.sexo
        ORDER BY e.nombre, tc.nombre, p.sexo
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    datos = []
    total_general = 0
    for r in rows:
        m = r._mapping
        t = int(m["total"])
        total_general += t
        datos.append({
            "especialidad": m["especialidad"],
            "tipo_consulta": m["tipo_consulta"],
            "sexo": m["sexo"],
            "total": t,
        })

    return {
        "titulo": "Consultas SIGSA-3 por Especialidad, Tipo y Sexo",
        "desde": f_desde,
        "hasta": f_hasta,
        "datos": datos,
        "total_general": total_general,
        "generado_en": datetime.now(APP_TIMEZONE).isoformat(),
    }


def sigsa3_dx_frecuentes(db: Session, desde: str, hasta: str, top: int = 10, tipo_consulta: int = None, especialidad: str = None) -> dict:
    """Top diagnósticos (CIE-10) más frecuentes por especialidad, tipo y sexo.
    Fuente: sigsa3_registros (normalizado). El dx es el código CIE-10 del catálogo."""
    f_desde, f_hasta = _parse_fechas(desde, hasta)

    if top is None or top <= 0:
        top = 10

    rows = db.execute(text("""
        WITH base AS (
            SELECT
                COALESCE(e.nombre, '—') AS especialidad,
                COALESCE(tc.nombre, '—') AS tipo_consulta,
                p.sexo AS sexo,
                c.codigo AS dx,
                c.descripcion AS dx_desc,
                COUNT(*) AS total
            FROM sigsa3_registros r
            LEFT JOIN especialidades e ON e.id = r.especialidad_id
            LEFT JOIN tipos_consulta_sigsa3 tc ON tc.id = r.tipo_consulta_id
            LEFT JOIN pacientes p ON p.id = r.paciente_id
            LEFT JOIN cie10_catalogo c ON c.id = r.codigo_cie_10_id
            WHERE r.fecha_consulta BETWEEN :desde AND :hasta
              AND r.especialidad_id IS NOT NULL
              AND r.tipo_consulta_id IS NOT NULL
              AND p.sexo IS NOT NULL
              AND c.codigo IS NOT NULL
              AND c.codigo <> ''
              AND c.codigo NOT LIKE 'Z%'
              AND c.codigo NOT LIKE 'O82%'
              AND c.codigo NOT LIKE 'O80%'
              AND c.codigo NOT LIKE 'O62%'
              AND (:tc IS NULL OR r.tipo_consulta_id = :tc)
              AND (:esp IS NULL OR e.nombre = :esp)
            GROUP BY e.nombre, tc.nombre, p.sexo, c.codigo, c.descripcion
        ),
        combinado AS (
            SELECT
                especialidad,
                tipo_consulta,
                dx,
                SUM(total) AS total_combinado
            FROM base
            GROUP BY especialidad, tipo_consulta, dx
        ),
        ranked_dx AS (
            SELECT
                especialidad,
                tipo_consulta,
                dx,
                total_combinado,
                ROW_NUMBER() OVER (
                    PARTITION BY especialidad, tipo_consulta
                    ORDER BY total_combinado DESC, dx ASC
                ) AS rn
            FROM combinado
        )
        SELECT
            b.especialidad,
            b.tipo_consulta,
            b.sexo,
            b.dx,
            b.dx_desc,
            b.total,
            r.total_combinado,
            r.rn
        FROM base b
        JOIN ranked_dx r
          ON r.especialidad = b.especialidad
         AND r.tipo_consulta = b.tipo_consulta
         AND r.dx = b.dx
        ORDER BY b.especialidad, b.tipo_consulta, r.rn, b.sexo
    """), {"desde": f_desde, "hasta": f_hasta, "tc": tipo_consulta, "esp": especialidad}).fetchall()

    from collections import defaultdict

    grupos: dict[tuple, dict] = defaultdict(
        lambda: defaultdict(lambda: {"m": 0, "f": 0, "rn": None, "total_combinado": 0, "dx_desc": ""})
    )

    for r in rows:
        m = r._mapping
        key_grupo = (m["especialidad"], m["tipo_consulta"])
        dx = m["dx"]
        sexo = m["sexo"]
        total = int(m["total"])

        entry = grupos[key_grupo][dx]
        entry["dx_desc"] = m.get("dx_desc") or ""
        if sexo == "M":
            entry["m"] += total
        elif sexo == "F":
            entry["f"] += total
        else:
            entry["m"] += total

        entry["rn"] = int(m["rn"])
        entry["total_combinado"] = int(m["total_combinado"])

    datos = []
    totales_grupo = []
    total_general = 0

    for (esp, tc), dx_map in sorted(grupos.items()):
        dx_items = sorted(dx_map.items(), key=lambda kv: kv[1]["rn"])

        top_items = [(dx, v) for dx, v in dx_items if v["rn"] <= top]
        resto_items = [(dx, v) for dx, v in dx_items if v["rn"] > top]

        grupo_total = sum(v["total_combinado"] for _, v in dx_items)
        total_general += grupo_total

        for dx, v in top_items:
            datos.append({
                "especialidad": esp,
                "tipo_consulta": tc,
                "dx": (f"{dx} {v['dx_desc']}".strip() if v["dx_desc"] else dx),
                "total_m": v["m"],
                "total_f": v["f"],
                "total": v["m"] + v["f"],
            })

        resto_m = sum(v["m"] for _, v in resto_items)
        resto_f = sum(v["f"] for _, v in resto_items)
        resto_sum = resto_m + resto_f

        if resto_sum > 0:
            datos.append({
                "especialidad": esp,
                "tipo_consulta": tc,
                "dx": "Resto de causas",
                "total_m": resto_m,
                "total_f": resto_f,
                "total": resto_sum,
            })

        total_top = sum(v["m"] + v["f"] for _, v in top_items)
        totales_grupo.append({
            "especialidad": esp,
            "tipo_consulta": tc,
            "total_top": total_top,
            "total_resto": resto_sum,
            "total": grupo_total,
        })

    return {
        "titulo": "Diagnósticos Más Frecuentes por Especialidad",
        "desde": f_desde,
        "hasta": f_hasta,
        "top": top,
        "datos": datos,
        "totales_por_grupo": totales_grupo,
        "total_general": total_general,
        "generado_en": datetime.now(APP_TIMEZONE).isoformat(),
    }


# =====================================================================
# INDICADORES DE CONSULTA (jsonb consultas.indicadores)
# =====================================================================

# Etiquetas legibles del jsonb. El orden define cómo se presentsi un
# indicador aparece por primera vez en el rango; el resto se ordena al final.
INDICADORES_CONSULTA: dict[str, dict] = {
    "estudiante_publico": {"etiqueta": "Estudiante público", "tipo": "booleano"},
    "personal_hospital": {"etiqueta": "Personal del hospital", "tipo": "booleano"},
    "empleado_publico": {"etiqueta": "Empleado público", "tipo": "booleano"},
    "embarazo": {"etiqueta": "Embarazo", "tipo": "booleano"},
    "accidente_laboral": {"etiqueta": "Accidente laboral", "tipo": "booleano"},
    "accidente_transito": {"etiqueta": "Accidente de tránsito", "tipo": "booleano"},
    "discapacidad": {"etiqueta": "Discapacidad", "tipo": "booleano"},
    "ambulancia": {"etiqueta": "Llegada en ambulancia", "tipo": "booleano"},
    "arma_fuego": {"etiqueta": "Arma de fuego", "tipo": "booleano"},
    "arma_blanca": {"etiqueta": "Arma blanca", "tipo": "booleano"},
    "viene_referido": {"etiqueta": "Viene referido desde", "tipo": "texto"},
    "fue_referido": {"etiqueta": "Fue referido a", "tipo": "texto"},
}

# `personal_hospital` se persiste como S/N/null mientras el resto son booleanos,
# así que un mismo predicado cubre ambas convenciones.
INDICADOR_VALORES_VERDADEROS = ("true", "s", "1")
INDICADOR_VALORES_FALSOS = ("false", "n", "0")

_SQL_VERDADEROS = "('true', 's', '1')"
_SQL_FALSOS = "('false', 'n', '0')"
_JSONB_VACIO = "'{}'::jsonb"

# `consultas.indicadores` no siempre es un objeto: 202,479 filas lo guardan como
# el JSON literal `null`, que en PostgreSQL no es lo mismo que SQL NULL, por eso
# COALESCE no basta y `jsonb_each_text` aborta la transicion con
# "no se puede invocar jsonb_each_text en un no-objeto". `jsonb_typeof` es la
# unica guarda que distingue el JSON null del objeto vacio.
_JSONB_INDICADORES = (
    "CASE WHEN jsonb_typeof(c.indicadores) = 'object' "
    f"THEN c.indicadores ELSE {_JSONB_VACIO} END"
)


def _jsonb_es_objeto(columna: str = "c.indicadores") -> str:
    """Devuelve el predicado que confirma que la columna es un objeto JSON."""
    return f"jsonb_typeof({columna}) = 'object'"


def _clasificar_valor_indicador(valor) -> str:
    """Clasifica un valor de `jsonb_each_text` como verdadero, falso, sin_valor o texto."""
    if valor is None:
        return "sin_valor"
    texto = str(valor).strip()
    if texto == "":
        return "sin_valor"
    if texto.lower() in INDICADOR_VALORES_VERDADEROS:
        return "verdadero"
    if texto.lower() in INDICADOR_VALORES_FALSOS:
        return "falso"
    return "texto"


TIPO_CONSULTA_NOMBRE = {1: "COEX", 2: "Hospitalización", 3: "Emergencia"}


def referencias_consultas(
    db: Session,
    desde: str,
    hasta: str,
    tipo_consulta: int | None = None,
    especialidad: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> dict:
    """Lista paginada y resumen de referencias del rango indicado.

    El resumen agrupa por nombre normalizado para que "CAP de Pátzun",
    "cap de patzun" y "CAP DE PATZUN" cuenten como una sola institucion, y
    expone `variantes` con los textos crudos quecollapsed en ese grupo.
    """
    f_desde, f_hasta = _parse_fechas(desde, hasta)
    skip = max(0, skip)
    limit = max(1, min(limit, 1000))

    filtros = ["c.fecha_consulta BETWEEN :desde AND :hasta"]
    params: dict = {"desde": f_desde, "hasta": f_hasta}
    if tipo_consulta is not None:
        filtros.append("c.tipo_consulta = :tipo_consulta")
        params["tipo_consulta"] = tipo_consulta
    if especialidad:
        filtros.append("c.especialidad = :especialidad")
        params["especialidad"] = especialidad
    where_sql = " AND ".join(filtros)

    totales = db.execute(text(f"""
        SELECT
            COUNT(*) AS total,
            COUNT(DISTINCT c.paciente_id) AS pacientes,
            COUNT(DISTINCT c.fecha_consulta) AS dias,
            COUNT(*) FILTER (
                WHERE {_JSONB_INDICADORES} <> {_JSONB_VACIO}
            ) AS con_jsonb,
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(c.indicadores ->> 'viene_referido_de'), '') IS NOT NULL
                   OR NULLIF(BTRIM(c.indicadores ->> 'viene_referido'), '') IS NOT NULL
            ) AS con_origen,
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(c.indicadores ->> 'va_referido_a'), '') IS NOT NULL
                   OR NULLIF(BTRIM(c.indicadores ->> 'fue_referido'), '') IS NOT NULL
            ) AS con_destino,
            COUNT(*) FILTER (
                WHERE (
                    NULLIF(BTRIM(c.indicadores ->> 'viene_referido_de'), '') IS NOT NULL
                    OR NULLIF(BTRIM(c.indicadores ->> 'viene_referido'), '') IS NOT NULL
                  )
                  AND (
                    NULLIF(BTRIM(c.indicadores ->> 'va_referido_a'), '') IS NOT NULL
                    OR NULLIF(BTRIM(c.indicadores ->> 'fue_referido'), '') IS NOT NULL
                  )
            ) AS con_ambos,
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(c.indicadores ->> 'viene_referido_de'), '') IS NOT NULL
                   OR NULLIF(BTRIM(c.indicadores ->> 'viene_referido'), '') IS NOT NULL
                   OR NULLIF(BTRIM(c.indicadores ->> 'va_referido_a'), '') IS NOT NULL
                   OR NULLIF(BTRIM(c.indicadores ->> 'fue_referido'), '') IS NOT NULL
            ) AS con_alguna
        FROM consultas c
        WHERE {where_sql}
    """), params).mappings().one()

    # El resumen se calcula en SQL sobre todo el rango, sin el LIMIT de la lista.
    resumen_sql = f"""
        WITH base AS (
            SELECT
                c.id,
                c.paciente_id,
                COALESCE(
                    NULLIF(BTRIM(c.indicadores ->> 'viene_referido_de'), ''),
                    NULLIF(BTRIM(c.indicadores ->> 'viene_referido'), '')
                ) AS origen,
                COALESCE(
                    NULLIF(BTRIM(c.indicadores ->> 'va_referido_a'), ''),
                    NULLIF(BTRIM(c.indicadores ->> 'fue_referido'), '')
                ) AS destino
            FROM consultas c
            WHERE {where_sql}
        ),
        pares AS (
            SELECT 'viene' AS direccion, origen AS valor, id, paciente_id FROM base WHERE origen IS NOT NULL
            UNION ALL
            SELECT 'va' AS direccion, destino AS valor, id, paciente_id FROM base WHERE destino IS NOT NULL
        ),
        normalizado AS (
            SELECT direccion, valor, id, paciente_id,
                   UNACCENT(UPPER(BTRIM(valor))) AS clave
            FROM pares
        )
        SELECT
            direccion,
            clave,
            COUNT(*) AS total,
            COUNT(DISTINCT id) AS consultas,
            COUNT(DISTINCT paciente_id) AS pacientes,
            COUNT(DISTINCT valor) AS variantes
        FROM normalizado
        GROUP BY direccion, clave
        ORDER BY direccion, total DESC, clave ASC
    """

    filas_resumen = db.execute(text(resumen_sql), params).fetchall()

    # Variantes crudas por direccion + clave normalizada.
    variantes_sql = f"""
        WITH base AS (
            SELECT
                COALESCE(
                    NULLIF(BTRIM(c.indicadores ->> 'viene_referido_de'), ''),
                    NULLIF(BTRIM(c.indicadores ->> 'viene_referido'), '')
                ) AS origen,
                COALESCE(
                    NULLIF(BTRIM(c.indicadores ->> 'va_referido_a'), ''),
                    NULLIF(BTRIM(c.indicadores ->> 'fue_referido'), '')
                ) AS destino
            FROM consultas c
            WHERE {where_sql}
        ),
        pares AS (
            SELECT 'viene' AS direccion, origen AS valor FROM base WHERE origen IS NOT NULL
            UNION ALL
            SELECT 'va' AS direccion, destino AS valor FROM base WHERE destino IS NOT NULL
        )
        SELECT
            direccion,
            UNACCENT(UPPER(BTRIM(valor))) AS clave,
            BTRIM(valor) AS variante,
            COUNT(*) AS total
        FROM pares
        GROUP BY direccion, clave, variante
        ORDER BY direccion, clave, total DESC, variante ASC
    """

    filas_variantes = db.execute(text(variantes_sql), params).fetchall()

    variantes: dict[tuple[str, str], list[dict]] = {}
    for r in filas_variantes:
        m = r._mapping
        variantes.setdefault((str(m["direccion"]), str(m["clave"])), []).append({
            "valor": str(m["variante"]),
            "total": int(m["total"]),
        })

    resumen: list[dict] = []
    for r in filas_resumen:
        m = r._mapping
        direccion = str(m["direccion"])
        clave = str(m["clave"])
        resumen.append({
            "direccion": direccion,
            "direccion_nombre": "Viene referido de" if direccion == "viene" else "Va referido a",
            "referencia": clave,
            "referencia_normalizada": clave,
            "total_consultas": int(m["total"]),
            "consultas_distintas": int(m["consultas"]),
            "pacientes_distintos": int(m["pacientes"]),
            "variantes": variantes.get((direccion, clave), []),
        })

    # Lista paginada de las consultas con referencia.
    lista_sql = f"""
        SELECT
            c.id,
            c.paciente_id,
            c.expediente,
            c.tipo_consulta,
            c.especialidad,
            c.fecha_consulta,
            NULLIF(BTRIM(c.indicadores ->> 'viene_referido_de'), '') AS viene_referido_de,
            NULLIF(BTRIM(c.indicadores ->> 'va_referido_a'), '') AS va_referido_a,
            NULLIF(BTRIM(c.indicadores ->> 'viene_referido'), '') AS viene_referido,
            NULLIF(BTRIM(c.indicadores ->> 'fue_referido'), '') AS fue_referido
        FROM consultas c
        WHERE {where_sql}
          AND (
              NULLIF(BTRIM(c.indicadores ->> 'viene_referido_de'), '') IS NOT NULL
              OR NULLIF(BTRIM(c.indicadores ->> 'viene_referido'), '') IS NOT NULL
              OR NULLIF(BTRIM(c.indicadores ->> 'va_referido_a'), '') IS NOT NULL
              OR NULLIF(BTRIM(c.indicadores ->> 'fue_referido'), '') IS NOT NULL
          )
        ORDER BY c.fecha_consulta DESC, c.id DESC
        LIMIT :limit OFFSET :skip
    """

    filas_lista = db.execute(
        text(lista_sql), {**params, "limit": limit, "skip": skip}
    ).fetchall()

    lista = []
    for r in filas_lista:
        m = r._mapping
        lista.append({
            "id": int(m["id"]),
            "paciente_id": m["paciente_id"],
            "expediente": m["expediente"],
            "tipo_consulta": m["tipo_consulta"],
            "tipo_consulta_nombre": TIPO_CONSULTA_NOMBRE.get(m["tipo_consulta"]),
            "especialidad": m["especialidad"],
            "fecha_consulta": m["fecha_consulta"],
            "viene_referido_de": m["viene_referido_de"],
            "va_referido_a": m["va_referido_a"],
            "viene_referido": m["viene_referido"],
            "fue_referido": m["fue_referido"],
        })

    total_consultas = int(totales["total"] or 0)
    con_jsonb = int(totales["con_jsonb"] or 0)
    con_alguna = int(totales["con_alguna"] or 0)
    con_origen = int(totales["con_origen"] or 0)
    con_destino = int(totales["con_destino"] or 0)

    return {
        "titulo": "Referencias de Consultas (viene_referido_de / va_referido_a)",
        "desde": f_desde,
        "hasta": f_hasta,
        "total_consultas": total_consultas,
        "pacientes_distintos": int(totales["pacientes"] or 0),
        "dias_con_registros": int(totales["dias"] or 0),
        "cobertura": {
            "consultas_con_jsonb": con_jsonb,
            "consultas_sin_jsonb": total_consultas - con_jsonb,
            "consultas_con_referencia": con_alguna,
            "consultas_sin_referencia": total_consultas - con_alguna,
            "con_origen": con_origen,
            "con_destino": con_destino,
            "porcentaje_con_referencia": round(100.0 * con_alguna / total_consultas, 1) if total_consultas else 0.0,
            "ambos_sentidos": int(totales["con_ambos"] or 0),
        },
        "lista": lista,
        "resumen": resumen,
        "total_general": con_alguna,
        "skip": skip,
        "limit": limit,
        "generado_en": datetime.now(APP_TIMEZONE).isoformat(),
    }


def indicadores_consultas(
    db: Session,
    desde: str,
    hasta: str,
    tipo_consulta: int | None = None,
    especialidad: str | None = None,
    top_referencias: int = 10,
) -> dict:
    """Resume el jsonb `consultas.indicadores` por rango de fechas.

    Las banderas se cuentan como marcadas cuando valen true o S; el null y la
    cadena vacía se reportan aparte porque no equivalen a un negativo.
    """
    f_desde, f_hasta = _parse_fechas(desde, hasta)
    top_referencias = max(1, min(top_referencias, 100))

    filtros = ["c.fecha_consulta BETWEEN :desde AND :hasta"]
    params: dict = {"desde": f_desde, "hasta": f_hasta}
    if tipo_consulta is not None:
        filtros.append("c.tipo_consulta = :tipo_consulta")
        params["tipo_consulta"] = tipo_consulta
    if especialidad:
        filtros.append("c.especialidad = :especialidad")
        params["especialidad"] = especialidad
    where_sql = " AND ".join(filtros)

    totales = db.execute(text(f"""
        SELECT
            COUNT(*) AS total,
            COUNT(DISTINCT c.paciente_id) AS pacientes,
            COUNT(DISTINCT c.fecha_consulta) AS dias,
            COUNT(*) FILTER (WHERE c.indicadores IS NULL) AS sin_columna,
            COUNT(*) FILTER (WHERE {_jsonb_es_objeto()} AND c.indicadores = {_JSONB_VACIO}) AS sin_claves
        FROM consultas c
        WHERE {where_sql}
    """), params).mappings().one()

    total_consultas = int(totales["total"] or 0)
    pacientes_distintos = int(totales["pacientes"] or 0)

    # Distribución de valores por clave. Cada jsonb aporta una fila por clave,
    # así que la suma de `registros` por indicador son las consultas que lo traen.
    filas_valor = db.execute(text(f"""
        SELECT
            e.key AS indicador,
            e.value AS valor,
            COUNT(*) AS registros,
            COUNT(DISTINCT c.paciente_id) AS pacientes
        FROM consultas c
        CROSS JOIN LATERAL jsonb_each_text({_JSONB_INDICADORES}) AS e(key, value)
        WHERE {where_sql}
        GROUP BY 1, 2
    """), params).fetchall()

    por_indicador: dict[str, dict] = {}
    total_pares_clave = 0

    for r in filas_valor:
        m = r._mapping
        clave = str(m["indicador"])
        registros = int(m["registros"])
        clasificacion = _clasificar_valor_indicador(m["valor"])

        acc = por_indicador.setdefault(clave, {
            "con_clave": 0,
            "sin_valor": 0,
            "verdadero": 0,
            "falso": 0,
            "con_texto": 0,
            "valores": set(),
        })
        acc["con_clave"] += registros
        total_pares_clave += registros

        if clasificacion == "sin_valor":
            acc["sin_valor"] += registros
        elif clasificacion == "verdadero":
            acc["verdadero"] += registros
        elif clasificacion == "falso":
            acc["falso"] += registros
        else:
            acc["con_texto"] += registros
            acc["valores"].add(str(m["valor"]).strip())

    # Pacientes distintos por indicador: requiere el agregado aparte porque un
    # mismo paciente puede aparecer bajo varios valores de una clave.
    filas_pacientes = db.execute(text(f"""
        SELECT
            e.key AS indicador,
            COUNT(DISTINCT c.paciente_id) AS pacientes
        FROM consultas c
        CROSS JOIN LATERAL jsonb_each_text({_JSONB_INDICADORES}) AS e(key, value)
        WHERE {where_sql}
          AND e.value IS NOT NULL
          AND btrim(e.value) <> ''
          AND (
            lower(btrim(e.value)) IN {_SQL_VERDADEROS}
            OR e.key IN ('viene_referido', 'fue_referido')
          )
        GROUP BY 1
    """), params).fetchall()
    pacientes_por_clave = {
        str(r._mapping["indicador"]): int(r._mapping["pacientes"]) for r in filas_pacientes
    }

    filas_tipo = db.execute(text(f"""
        SELECT
            e.key AS indicador,
            c.tipo_consulta,
            COUNT(*) AS total
        FROM consultas c
        CROSS JOIN LATERAL jsonb_each_text({_JSONB_INDICADORES}) AS e(key, value)
        WHERE {where_sql}
          AND e.value IS NOT NULL
          AND lower(btrim(e.value)) IN {_SQL_VERDADEROS}
        GROUP BY 1, 2
    """), params).fetchall()

    por_tipo: dict[str, dict[int, int]] = {}
    for r in filas_tipo:
        m = r._mapping
        por_tipo.setdefault(str(m["indicador"]), {})[int(m["tipo_consulta"])] = int(m["total"])

    # Referencias: texto libre, se rankea por indicador para no mezcalos.
    filas_ref = db.execute(text(f"""
        SELECT indicador, valor, total
        FROM (
            SELECT
                e.key AS indicador,
                btrim(e.value) AS valor,
                COUNT(*) AS total,
                ROW_NUMBER() OVER (
                    PARTITION BY e.key ORDER BY COUNT(*) DESC, btrim(e.value) ASC
                ) AS rn
            FROM consultas c
            CROSS JOIN LATERAL jsonb_each_text({_JSONB_INDICADORES}) AS e(key, value)
            WHERE {where_sql}
              AND e.key IN ('viene_referido', 'fue_referido')
              AND e.value IS NOT NULL
              AND btrim(e.value) <> ''
            GROUP BY 1, 2
        ) t
        WHERE rn <= :top_referencias
        ORDER BY indicador, rn
    """), {**params, "top_referencias": top_referencias}).fetchall()

    referencias = [
        {
            "indicador": str(r._mapping["indicador"]),
            "valor": str(r._mapping["valor"]),
            "total": int(r._mapping["total"]),
        }
        for r in filas_ref
    ]

    def _porcentaje(numerador: int, denominador: int) -> float:
        return round(100.0 * numerador / denominador, 1) if denominador else 0.0

    def _tipo_dato(clave: str) -> str:
        return INDICADORES_CONSULTA.get(clave, {}).get("tipo", "texto")

    datos = []
    for clave, acc in por_indicador.items():
        tipo = _tipo_dato(clave)
        es_texto = tipo == "texto"

        if es_texto:
            magnitud = acc["con_texto"]
        else:
            magnitud = acc["verdadero"]

        datos.append({
            "indicador": clave,
            "etiqueta": INDICADORES_CONSULTA.get(clave, {}).get("etiqueta", clave),
            "tipo_dato": tipo,
            "clave_ausente": max(total_consultas - acc["con_clave"], 0),
            "sin_valor": acc["sin_valor"],
            "verdadero": acc["verdadero"],
            "falso": acc["falso"],
            "con_texto": acc["con_texto"] if es_texto else 0,
            "valores_distintos": len(acc["valores"]) if es_texto else 0,
            "pacientes": pacientes_por_clave.get(clave, 0),
            "porcentaje_consultas": _porcentaje(magnitud, total_consultas),
            "porcentaje_pacientes": _porcentaje(pacientes_por_clave.get(clave, 0), pacientes_distintos),
            "por_tipo_consulta": [
                {
                    "tipo_consulta": tc,
                    "tipo_consulta_nombre": TIPO_CONSULTA_MAP.get(tc, f"Tipo {tc}"),
                    "total": n,
                }
                for tc, n in sorted(por_tipo.get(clave, {}).items())
            ] if not es_texto else [],
        })

    # Ordena por magnitud descendente; los indicadores del catálogo conocido
    # conservan su posición declarada cuando empatan en cero.
    prioridad = {clave: i for i, clave in enumerate(INDICADORES_CONSULTA)}
    def _orden(d):
        magnitud = d["con_texto"] if d["tipo_dato"] == "texto" else d["verdadero"]
        return (-magnitud, prioridad.get(d["indicador"], len(prioridad)), d["indicador"])
    datos.sort(key=_orden)

    return {
        "titulo": "Resumen de Indicadores de Consultas",
        "desde": f_desde,
        "hasta": f_hasta,
        "total_consultas": total_consultas,
        "pacientes_distintos": pacientes_distintos,
        "dias_con_registros": int(totales["dias"] or 0),
        "cobertura": {
            "consultas_sin_columna": int(totales["sin_columna"] or 0),
            "consultas_sin_claves": int(totales["sin_claves"] or 0),
            "claves_distintas": len(por_indicador),
            "promedio_claves_por_consulta": (
                round(total_pares_clave / total_consultas, 2) if total_consultas else 0.0
            ),
        },
        "datos": datos,
        "referencias": referencias,
        "total_general": total_consultas,
        "generado_en": datetime.now(APP_TIMEZONE).isoformat(),
    }


# =====================================================================
# REINGRESOS Y CONSULTAS ACTIVAS (movidos desde consultas/service.py)
# =====================================================================

def reingresos_consulta_tipo3(
    db: Session,
    skip: int = 0,
    limit: int = 50,
):
    desde = date.today() - timedelta(days=20)
    hasta = date.today()

    filters = (
        ConsultaModel.tipo_consulta == 3,
        ConsultaModel.activo.is_(True),
        ConsultaModel.fecha_consulta.between(desde, hasta),
    )

    multi_pacientes = (
        db.query(ConsultaModel.paciente_id)
        .filter(*filters)
        .group_by(ConsultaModel.paciente_id)
        .having(func.count(ConsultaModel.id) >= 2)
        .subquery()
    )

    total_query = (
        db.query(func.count(ConsultaModel.id))
        .filter(
            ConsultaModel.paciente_id.in_(db.query(multi_pacientes.c.paciente_id)),
            *filters,
        )
    )
    total = total_query.scalar()

    resultados = (
        db.query(ConsultaModel)
        .options(joinedload(ConsultaModel.paciente))
        .filter(
            ConsultaModel.paciente_id.in_(db.query(multi_pacientes.c.paciente_id)),
            *filters,
        )
        .order_by(ConsultaModel.paciente_id, ConsultaModel.fecha_consulta.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return ConsultaListResponse(
        total=total or 0,
        consultas=resultados
    )


def consultas_activas_admision_mayores_7_dias(
    db: Session,
    skip: int = 0,
    limit: int = 50,
):
    corte = date.today() - timedelta(days=7)
    query = (
        db.query(ConsultaModel)
        .join(PacienteModel, ConsultaModel.paciente_id == PacienteModel.id)
        .options(joinedload(ConsultaModel.paciente))
        .filter(
            ConsultaModel.activo.is_(True),
            ConsultaModel.ultimo_estado == "admision",
            ConsultaModel.fecha_consulta < corte
        )
    )

    total = query.count()
    resultados = (
        query
        .order_by(ConsultaModel.fecha_consulta.asc())
        .limit(limit).offset(skip)
        .all()
    )

    hoy = date.today()
    for r in resultados:
        r.dias_acumulados = (hoy - r.fecha_consulta).days

    return ConsultaListResponse(
        total=total,
        consultas=resultados
    )
