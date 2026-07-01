from datetime import date, datetime
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


TIPO_CONSULTA_MAP = {1: "COEX", 2: "Hospitalización", 3: "Emergencia"}


def _parse_fechas(desde: str, hasta: str) -> tuple[date, date]:
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
        "generado_en": datetime.now().isoformat(),
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
        "generado_en": datetime.now().isoformat(),
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
        "generado_en": datetime.now().isoformat(),
    }


def personal_hospital(db: Session, desde: str, hasta: str) -> dict:
    f_desde, f_hasta = _parse_fechas(desde, hasta)

    rows = db.execute(text("""
        SELECT
            p.nombre,
            p.nombre_completo,
            p.expediente,
            c.tipo_consulta,
            p.sexo,
            p.fecha_nacimiento,
            c.fecha_consulta,
            c.especialidad,
            c.documento,
            c.paciente_id,
            c.egreso#>>'{diagnosticos}' AS diagnostico
        FROM consultas c
        JOIN pacientes p ON p.id = c.paciente_id
        WHERE c.fecha_consulta BETWEEN :desde AND :hasta
          AND c.activo = true
          AND (
              p.datos_extra#>>'{socioeconomicos,personal_hospital}' = 'S'
          )
        ORDER BY c.fecha_consulta, c.hora_consulta
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

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
            "fecha_consulta": str(m["fecha_consulta"])
        })

    return {
        "titulo": "Consultas de Personal del Hospital",
        "desde": f_desde,
        "hasta": f_hasta,
        "datos": datos,
        "total_general": len(datos),
        "generado_en": datetime.now().isoformat(),
    }


def estudiante_publico(db: Session, desde: str, hasta: str) -> dict:
    f_desde, f_hasta = _parse_fechas(desde, hasta)

    rows = db.execute(text("""
        SELECT
            p.nombre,
            p.nombre_completo,
            p.expediente,
            c.tipo_consulta,
            p.sexo,
            p.fecha_nacimiento,
            c.fecha_consulta,
            c.especialidad,
            c.documento,
            c.fecha_consulta,
            c.paciente_id,
            c.egreso#>>'{diagnosticos}' AS diagnostico
        FROM consultas c
        JOIN pacientes p ON p.id = c.paciente_id
        WHERE c.fecha_consulta BETWEEN :desde AND :hasta
          AND c.activo = true
          AND (
              p.datos_extra#>>'{socioeconomicos,estudiante_publico}' = 'S'
          )
        ORDER BY c.fecha_consulta, c.hora_consulta
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

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
            "fecha_consulta": str(m["fecha_consulta"]),
            "paciente_id": str(m["paciente_id"])
        })

    return {
        "titulo": "Consultas de Estudiantes Públicos",
        "desde": f_desde,
        "hasta": f_hasta,
        "datos": datos,
        "total_general": len(datos),
        "generado_en": datetime.now().isoformat(),
    }


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
        "generado_en": datetime.now().isoformat(),
    }


def _rows_to_list(rows) -> list[dict]:
    return [dict(r._mapping) for r in rows]


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
          AND p.estado IN ('V', 'F')
          AND (n.mortinato = false OR n.mortinato IS NULL)
        GROUP BY p.sexo, p.estado
        ORDER BY p.sexo, p.estado
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    rows_clase_parto = db.execute(text("""
        SELECT
            p.datos_extra#>'{neonatales,clase_parto}' AS clase_parto,
            n.mortinato,
            p.sexo,
            COUNT(*) AS total
        FROM nacimientos n
        JOIN pacientes p ON p.id = n.paciente_id
        WHERE p.fecha_nacimiento BETWEEN :desde AND :hasta
          AND p.sexo IN ('M', 'F')
        GROUP BY p.datos_extra#>'{neonatales,clase_parto}', n.mortinato, p.sexo
        ORDER BY clase_parto, n.mortinato, p.sexo
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    rows_clasificacion_parto = db.execute(text("""
        SELECT
            n.clasificacion_nacimiento AS clasificacion_parto,
            n.mortinato,
            p.sexo,
            COUNT(*) AS total
        FROM nacimientos n
        JOIN pacientes p ON p.id = n.paciente_id
        WHERE p.fecha_nacimiento BETWEEN :desde AND :hasta
          AND p.sexo IN ('M', 'F')
        GROUP BY n.clasificacion_nacimiento, n.mortinato, p.sexo
        ORDER BY clasificacion_parto, n.mortinato, p.sexo
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    rows_trabajo_parto = db.execute(text("""
        SELECT
            n.trabajo_parto,
            n.mortinato,
            p.sexo,
            COUNT(*) AS total
        FROM nacimientos n
        JOIN pacientes p ON p.id = n.paciente_id
        WHERE p.fecha_nacimiento BETWEEN :desde AND :hasta
          AND p.sexo IN ('M', 'F')
        GROUP BY n.trabajo_parto, n.mortinato, p.sexo
        ORDER BY n.trabajo_parto, n.mortinato, p.sexo
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    def _build_mortinato(items, key) -> list[dict]:
        result = []
        for r in items:
            m = r._mapping
            mort_val = m["mortinato"]
            if isinstance(mort_val, bool):
                label = "Mortinato" if mort_val else "Vivo"
            else:
                label = "Vivo" if str(mort_val).lower() in ("false", "0", "none") else "Mortinato"
            item = {"estado": label, "sexo": str(m["sexo"]), "total": int(m["total"])}
            item[key] = str(m[key]) if m.get(key) is not None else None
            result.append(item)
        return result

    def _build_estado(items, key) -> list[dict]:
        result = []
        for r in items:
            m = r._mapping
            item = {"estado": str(m["estado"]), "sexo": str(m["sexo"]), "total": int(m["total"])}
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
        "por_fallecidos_posteriores": _build_estado(rows_fallecidos_posteriores, "sexo"),
        "por_clase_parto": _build_mortinato(rows_clase_parto, "clase_parto"),
        "por_clasificacion_parto": _build_mortinato(rows_clasificacion_parto, "clasificacion_parto"),
        "por_trabajo_parto": _build_mortinato(rows_trabajo_parto, "trabajo_parto"),
        "generado_en": datetime.now().isoformat(),
    }
