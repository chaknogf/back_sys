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
