import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


def _calcular_edad(fecha_nac: date) -> int:
    if fecha_nac is None:
        return 0
    hoy = date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))


def resumen_dashboard(db: Session, fecha: Optional[str] = None) -> dict:
    fecha_ref = datetime.strptime(fecha, "%Y-%m-%d").date() if fecha else date.today()
    ayer = fecha_ref - timedelta(days=1)

    rows = db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM pacientes) AS total_pacientes,
            (SELECT COUNT(*) FROM pacientes WHERE estado = 'A') AS pacientes_activos,
            (SELECT COUNT(*) FROM consultas) AS total_consultas,
            (SELECT COUNT(*) FROM consultas WHERE fecha_consulta = :hoy) AS consultas_hoy,
            (SELECT COUNT(*) FROM consultas WHERE fecha_consulta = :ayer) AS consultas_ayer,
            (SELECT COUNT(*) FROM consultas WHERE tipo_consulta = 2 AND fecha_consulta = :hoy) AS hospitalizados_hoy,
            (SELECT COUNT(*) FROM consultas WHERE tipo_consulta = 2 AND activo = true) AS hospitalizados_activos,
            (SELECT COUNT(*) FROM consultas WHERE tipo_consulta = 3 AND fecha_consulta = :hoy) AS emergencias_hoy,
            (SELECT COUNT(*) FROM procedimientos) AS total_procedimientos,
            (SELECT COUNT(*) FROM prestamos WHERE activo = true) AS prestamos_activos,
            (SELECT COUNT(*) FROM users WHERE estado = 'A') AS usuarios_activos,
            (SELECT COUNT(*) FROM citas WHERE fecha_cita = :hoy) AS citas_hoy
    """), {"hoy": fecha_ref, "ayer": ayer}).first()

    total = rows._mapping

    def calc_variacion(actual: int, anterior: int) -> Optional[float]:
        if anterior == 0:
            return None
        return round((actual - anterior) / anterior * 100, 1)

    var_consultas = calc_variacion(total["consultas_hoy"], total["consultas_ayer"])
    tendencia_consultas = "up" if (var_consultas or 0) > 0 else "down" if (var_consultas or 0) < 0 else "stable"

    indicadores = [
        {"etiqueta": "Pacientes Totales", "valor": total["total_pacientes"]},
        {"etiqueta": "Pacientes Activos", "valor": total["pacientes_activos"]},
        {"etiqueta": "Consultas Hoy", "valor": total["consultas_hoy"], "variacion": var_consultas, "tendencia": tendencia_consultas},
        {"etiqueta": "Hospitalizados", "valor": total["hospitalizados_hoy"]},
        {"etiqueta": "Hospitalizados Activos", "valor": total["hospitalizados_activos"]},
        {"etiqueta": "Emergencias Hoy", "valor": total["emergencias_hoy"]},
        {"etiqueta": "Procedimientos (Catálogo)", "valor": total["total_procedimientos"]},
        {"etiqueta": "Préstamos Activos", "valor": total["prestamos_activos"]},
        {"etiqueta": "Usuarios Activos", "valor": total["usuarios_activos"]},
        {"etiqueta": "Citas Programadas Hoy", "valor": total["citas_hoy"]},
    ]

    periodo = "Hoy" if fecha is None or fecha == str(date.today()) else fecha_ref.strftime("%d/%m/%Y")

    return {
        "indicadores": indicadores,
        "periodo": periodo,
        "generado_en": datetime.now().isoformat(),
    }


def consultas_por_dia(db: Session, desde: str, hasta: str) -> dict:
    try:
        f_desde = datetime.strptime(desde, "%Y-%m-%d").date()
        f_hasta = datetime.strptime(hasta, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    rows = db.execute(text("""
        SELECT fecha_consulta, tipo_consulta, COUNT(*) AS total
        FROM consultas
        WHERE fecha_consulta BETWEEN :desde AND :hasta
        GROUP BY fecha_consulta, tipo_consulta
        ORDER BY fecha_consulta, tipo_consulta
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    if not rows:
        return {"titulo": "Consultas por Día", "datos": [], "total": 0, "generado_en": datetime.now().isoformat()}

    df = pd.DataFrame([dict(r._mapping) for r in rows])
    tipos = {1: "COEX", 2: "Hospitalización", 3: "Emergencia"}

    pivote = df.pivot_table(
        index="fecha_consulta",
        columns="tipo_consulta",
        values="total",
        aggfunc="sum",
        fill_value=0
    )
    pivote.columns = [tipos.get(c, f"Tipo {c}") for c in pivote.columns]
    pivote["Total"] = pivote.sum(axis=1)
    pivote = pivote.reset_index()

    datos = []
    for _, row in pivote.iterrows():
        punto = {"label": str(row["fecha_consulta"]), "valor": int(row["Total"])}
        for col in pivote.columns:
            if col not in ("fecha_consulta", "Total"):
                punto[col] = int(row[col])
        datos.append(punto)

    return {
        "titulo": "Consultas por Día",
        "datos": datos,
        "total": int(df["total"].sum()),
        "generado_en": datetime.now().isoformat(),
    }


def consultas_por_especialidad(db: Session, desde: Optional[str] = None, hasta: Optional[str] = None) -> dict:
    filtro = ""
    params = {}
    if desde and hasta:
        filtro = "WHERE c.fecha_consulta BETWEEN :desde AND :hasta"
        params = {"desde": desde, "hasta": hasta}

    rows = db.execute(text(f"""
        SELECT c.especialidad, COUNT(*) AS total
        FROM consultas c
        {filtro}
        GROUP BY c.especialidad
        ORDER BY total DESC
    """), params).fetchall()

    if not rows:
        return {"titulo": "Consultas por Especialidad", "datos": [], "total": 0, "generado_en": datetime.now().isoformat()}

    df = pd.DataFrame([dict(r._mapping) for r in rows])
    total_general = int(df["total"].sum())
    df["porcentaje"] = (df["total"] / total_general * 100).round(1)

    datos = [
        {"label": r["especialidad"], "valor": int(r["total"]), "porcentaje": float(r["porcentaje"])}
        for _, r in df.iterrows()
    ]

    return {
        "titulo": "Consultas por Especialidad",
        "datos": datos,
        "total": total_general,
        "generado_en": datetime.now().isoformat(),
    }


def piramide_poblacional(db: Session) -> dict:
    rows = db.execute(text("""
        SELECT fecha_nacimiento, sexo
        FROM pacientes
        WHERE fecha_nacimiento IS NOT NULL AND sexo IN ('M', 'F')
    """)).fetchall()

    if not rows:
        return {
            "titulo": "Pirámide Poblacional",
            "rangos": [], "total_hombres": 0, "total_mujeres": 0,
            "total_pacientes": 0, "generado_en": datetime.now().isoformat(),
        }

    df = pd.DataFrame([dict(r._mapping) for r in rows])
    hoy = date.today()
    df["edad"] = df["fecha_nacimiento"].apply(
        lambda fn: hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))
    )

    bins = list(range(0, 101, 5))
    labels = [f"{i}-{i+4}" for i in range(0, 100, 5)]
    labels[-1] = "95+"
    df["rango"] = pd.cut(df["edad"], bins=bins, labels=labels, right=False, include_lowest=True)

    agrupado = df.groupby(["rango", "sexo"]).size().unstack(fill_value=0)

    rangos = []
    total_h = total_m = 0
    for rango_label in labels:
        if rango_label in agrupado.index:
            h = int(agrupado.loc[rango_label, "M"]) if "M" in agrupado.columns else 0
            m = int(agrupado.loc[rango_label, "F"]) if "F" in agrupado.columns else 0
        else:
            h = m = 0
        total_h += h
        total_m += m
        rangos.append({"rango": rango_label, "hombres": h, "mujeres": m, "total": h + m})

    return {
        "titulo": "Pirámide Poblacional",
        "rangos": rangos,
        "total_hombres": total_h,
        "total_mujeres": total_m,
        "total_pacientes": total_h + total_m,
        "generado_en": datetime.now().isoformat(),
    }


def procedimientos_mas_frecuentes(db: Session, desde: Optional[str] = None, hasta: Optional[str] = None, limite: int = 10) -> dict:
    filtro = ""
    params = {"limite": limite}
    if desde and hasta:
        filtro = "AND pm.fecha BETWEEN :desde AND :hasta"
        params["desde"] = desde
        params["hasta"] = hasta

    rows = db.execute(text(f"""
        SELECT p.nombre, COUNT(*) AS total
        FROM proce_medicos pm
        JOIN procedimientos p ON p.id = pm.id_procedimiento
        WHERE pm.id_procedimiento IS NOT NULL {filtro}
        GROUP BY p.id, p.nombre
        ORDER BY total DESC
        LIMIT :limite
    """), params).fetchall()

    total_general = db.execute(text("""
        SELECT COUNT(*) FROM proce_medicos WHERE id_procedimiento IS NOT NULL
    """)).scalar() or 0

    if not rows:
        return {
            "titulo": "Procedimientos Más Frecuentes",
            "procedimientos": [], "total_general": total_general,
            "periodo": "histórico", "generado_en": datetime.now().isoformat(),
        }

    df = pd.DataFrame([dict(r._mapping) for r in rows])
    df["porcentaje"] = (df["total"] / total_general * 100).round(1)

    procedimientos = [
        {"nombre": r["nombre"], "total": int(r["total"]), "porcentaje": float(r["porcentaje"])}
        for _, r in df.iterrows()
    ]

    periodo = "histórico"
    if desde and hasta:
        periodo = f"{desde} al {hasta}"

    return {
        "titulo": "Procedimientos Más Frecuentes",
        "procedimientos": procedimientos,
        "total_general": total_general,
        "periodo": periodo,
        "generado_en": datetime.now().isoformat(),
    }


def ocupacion_hospitalaria(db: Session) -> dict:
    rows = db.execute(text("""
        SELECT
            servicio,
            COUNT(*) AS total_camas,
            SUM(CASE WHEN activo = true THEN 1 ELSE 0 END) AS camas_ocupadas
        FROM consultas
        WHERE tipo_consulta = 2
          AND fecha_consulta >= CURRENT_DATE - INTERVAL '1 day'
        GROUP BY servicio
        ORDER BY servicio
    """)).fetchall()

    if not rows:
        return {
            "titulo": "Ocupación Hospitalaria",
            "servicios": [], "total_camas": 0, "total_ocupadas": 0,
            "porcentaje_global": 0.0, "generado_en": datetime.now().isoformat(),
        }

    servicios = []
    total_camas = total_ocupadas = 0
    for r in rows:
        m = r._mapping
        disp = int(m["total_camas"])
        ocup = int(m["camas_ocupadas"])
        pct = round(ocup / disp * 100, 1) if disp > 0 else 0.0
        total_camas += disp
        total_ocupadas += ocup
        servicios.append({
            "servicio": m["servicio"],
            "camas_disponibles": disp,
            "camas_ocupadas": ocup,
            "porcentaje_ocupacion": pct,
        })

    pct_global = round(total_ocupadas / total_camas * 100, 1) if total_camas > 0 else 0.0

    return {
        "titulo": "Ocupación Hospitalaria",
        "servicios": servicios,
        "total_camas": total_camas,
        "total_ocupadas": total_ocupadas,
        "porcentaje_global": pct_global,
        "generado_en": datetime.now().isoformat(),
    }


def reporte_personalizado(db: Session, tabla: str, columnas: List[str], filtros: Optional[dict] = None,
                           desde: Optional[str] = None, hasta: Optional[str] = None,
                           col_fecha: Optional[str] = None, limite: int = 500) -> dict:
    if not columnas:
        raise HTTPException(status_code=400, detail="Debe especificar al menos una columna")

    tablas_permitidas = {
        "pacientes", "consultas", "citas", "eventos_consulta",
        "procedimientos", "proce_medicos", "prestamos", "medicos",
        "ciclos_consulta", "laboratorios", "rayos_x",
    }
    if tabla not in tablas_permitidas:
        raise HTTPException(status_code=400, detail=f"Tabla no permitida. Use: {', '.join(sorted(tablas_permitidas))}")

    cols_sql = ", ".join(columnas)
    where_clauses = []
    params = {"limite": limite}

    if filtros:
        for k, v in filtros.items():
            col = k.replace("'", "''")
            where_clauses.append(f"{col} = :f_{col}")
            params[f"f_{col}"] = v

    if desde and hasta and col_fecha:
        where_clauses.append(f"{col_fecha} BETWEEN :desde AND :hasta")
        params["desde"] = desde
        params["hasta"] = hasta

    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

    query = text(f"SELECT {cols_sql} FROM {tabla} WHERE {where_sql} LIMIT :limite")
    rows = db.execute(query, params).fetchall()

    if not rows:
        return {"desde": desde, "hasta": hasta, "generado_en": datetime.now().isoformat(),
                "data": [], "columnas": columnas, "total_filas": 0} if desde else \
               {"generado_en": datetime.now().isoformat(), "data": [], "columnas": columnas, "total_filas": 0}

    df = pd.DataFrame([dict(r._mapping) for r in rows])

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: str(x) if not pd.isna(x) else None)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
        elif isinstance(df[col].dtype, np.integer):
            df[col] = df[col].apply(lambda x: int(x) if not pd.isna(x) else None)
        elif isinstance(df[col].dtype, np.floating):
            df[col] = df[col].apply(lambda x: float(x) if not pd.isna(x) else None)

    data = df.replace({np.nan: None}).to_dict(orient="records")

    result = {"generado_en": datetime.now().isoformat(), "data": data, "columnas": columnas, "total_filas": len(data)}
    if desde and hasta:
        result["desde"] = desde
        result["hasta"] = hasta
    return result


TIPO_CONSULTA_MAP = {1: "COEX", 2: "Hospitalización", 3: "Emergencia"}


def personal_salud_reporte(
    db: Session,
    desde: str,
    hasta: str,
    filtro: str = "personal_hospital",
) -> dict:
    try:
        f_desde = datetime.strptime(desde, "%Y-%m-%d").date()
        f_hasta = datetime.strptime(hasta, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    cond_indicador = "(c.indicadores->>'personal_hospital' = 'S' OR c.indicadores->>'personal_hospital' = 'true')"
    filtro_label = "personal_hospital"

    rows = db.execute(text(f"""
        SELECT
            p.sexo,
            c.especialidad,
            c.tipo_consulta,
            c.egreso->>'diagnosticos' AS diagnostico,
            COUNT(*) AS total
        FROM consultas c
        JOIN pacientes p ON p.id = c.paciente_id
        WHERE c.fecha_consulta BETWEEN :desde AND :hasta
          AND {cond_indicador}
          AND p.sexo IN ('M', 'F')
        GROUP BY p.sexo, c.especialidad, c.tipo_consulta, c.egreso->>'diagnosticos'
        ORDER BY total DESC
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    detalle_rows = db.execute(text(f"""
        SELECT
            c.expediente,
            p.nombre,
            p.sexo,
            p.fecha_nacimiento,
            c.egreso->>'diagnosticos' AS diagnostico,
            c.fecha_consulta,
            c.especialidad,
            c.tipo_consulta
        FROM consultas c
        JOIN pacientes p ON p.id = c.paciente_id
        WHERE c.fecha_consulta BETWEEN :desde AND :hasta
          AND {cond_indicador}
          AND p.sexo IN ('M', 'F')
        ORDER BY c.fecha_consulta DESC, p.nombre->>'primer_apellido'
    """), {"desde": f_desde, "hasta": f_hasta}).fetchall()

    def _build_nombre(nombre_json) -> str:
        if not nombre_json:
            return "S/N"
        parts = []
        for key in ("primer_nombre", "segundo_nombre", "primer_apellido", "segundo_apellido"):
            val = nombre_json.get(key)
            if val:
                parts.append(val)
        return " ".join(parts) if parts else "S/N"

    detalle = [
        {
            "expediente": r.expediente,
            "nombre": _build_nombre(r.nombre),
            "sexo": r.sexo,
            "fecha_nacimiento": r.fecha_nacimiento,
            "diagnostico": r.diagnostico,
            "fecha_consulta": r.fecha_consulta,
            "especialidad": r.especialidad,
            "tipo_consulta": r.tipo_consulta,
        }
        for r in detalle_rows
    ]

    if not rows:
        return {
            "titulo": "Consulta de Personal de Salud",
            "desde": f_desde, "hasta": f_hasta,
            "filtro_aplicado": filtro_label,
            "resumen": [], "detalle": [],
            "total_consultas": 0,
            "total_sexo_m": 0, "total_sexo_f": 0,
            "generado_en": datetime.now().isoformat(),
        }

    df = pd.DataFrame([dict(r._mapping) for r in rows])
    df["tipo_consulta_nombre"] = df["tipo_consulta"].map(TIPO_CONSULTA_MAP).fillna("Desconocido")

    filas = []
    for _, r in df.iterrows():
        filas.append({
            "sexo": str(r["sexo"]),
            "diagnostico": r["diagnostico"] if pd.notna(r["diagnostico"]) else None,
            "especialidad": str(r["especialidad"]),
            "tipo_consulta": int(r["tipo_consulta"]),
            "tipo_consulta_nombre": str(r["tipo_consulta_nombre"]),
            "total": int(r["total"]),
        })

    total_consultas = int(df["total"].sum())
    total_m = int(df[df["sexo"] == "M"]["total"].sum()) if "M" in df["sexo"].values else 0
    total_f = int(df[df["sexo"] == "F"]["total"].sum()) if "F" in df["sexo"].values else 0

    return {
        "titulo": "Consulta de Personal de Salud",
        "desde": f_desde,
        "hasta": f_hasta,
        "filtro_aplicado": filtro_label,
        "resumen": filas,
        "detalle": detalle,
        "total_consultas": total_consultas,
        "total_sexo_m": total_m,
        "total_sexo_f": total_f,
        "generado_en": datetime.now().isoformat(),
    }
