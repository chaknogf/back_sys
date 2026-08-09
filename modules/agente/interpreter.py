"""Intérprete determinístico lenguaje natural → SQL (solo SELECT).

Orquesta: normalización → detección de entidad → métrica → agrupación →
filtros (fechas, sexo, estado, tipo_consulta) → generación SQL con
parámetros ligados.

Toda decisión sale de ENTIDADES (catálogo) y de sinónimos aprendidos
(pasados como reglas_adicionales). El texto del usuario jamás se concatena
en el SQL; solo se usan valores como parámetros ligados.
"""
import re
from datetime import date, datetime, timedelta

from modules.agente.entidades import (
    ENTIDADES,
    TIPO_CONSULTA_MAPA,
    TIPO_CONSULTA_POR_NOMBRE,
)

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

_ALIAS_AGRUPACION = {
    "genero": "sexo", "generos": "sexo", "masculino": "sexo",
    "femenino": "sexo", "especialidades": "especialidad",
    "tipos de consulta": "tipo_consulta", "tipo de consulta": "tipo_consulta",
    "tipo documento": "tipo_documento", "tipo de documento": "tipo_documento",
    "tipos de documento": "tipo_documento", "documentos": "tipo_documento",
    "diagnostico": "diagnostico", "diagnosticos": "diagnostico",
    "diagnósticos": "diagnostico", "dx": "diagnostico",
    "meses": "mes", "anios": "anio", "anos": "anio", "dias": "dia",
}

_SINONIMOS_MEDIDA = {
    "promedio": "avg", "promedio de": "avg", "media": "avg",
    "edad promedio": "avg_edad", "edad media": "avg_edad",
}
_VALOR_MEDIDA = {
    "promedio de edad": "avg_edad",
    "promedio edad": "avg_edad",
    "edad promedio": "avg_edad",
    "edad media": "avg_edad",
}

_SINONIMOS_ENTIDAD_ADICIONAL = {
    "cantidad de consultas": "consultas",
    "numero de consultas": "consultas",
    "total de consultas": "consultas",
    "cuantas consultas": "consultas",
    "registro de consultas": "consultas",
"diagnosticos mas frecuentes": "sigsa3",
    "diagnosticos frecuentes": "sigsa3",
    "diagnosticos sigsa": "sigsa3",
    "consultas sigsa3": "sigsa3",
}


def _normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, espacios colapsados, sin puntuación rara."""
    t = texto.lower()
    t = t.replace("¿", "").replace("?", "").replace("¡", "").replace("!", "")
    t = re.sub(r"[^\w\s]", " ", t)
    t = t.replace("á", "a").replace("é", "e").replace("í", "i")
    t = t.replace("ó", "o").replace("ú", "u").replace("ü", "u").replace("ñ", "n")
    return re.sub(r"\s+", " ", t).strip()


def _detectar_entidad(texto: str, reglas_extra: dict) -> str | None:
    wordles = _normalizar(texto)
    # Sinónimos aprendidos tienen prioridad
    for sinonimo, entidad in sorted(reglas_extra.items(), key=lambda kv: -len(kv[0])):
        if _normalizar(sinonimo) in wordles:
            if entidad in ENTIDADES:
                return entidad
    # "pacientes fallecidos" debe priorizar pacientes (estado F) sobre defunciones
    if " paciente" in wordles or wordles.startswith("paciente "):
        return "pacientes"
    # Sinónimos explícitos compuestos primero
    for sinonimo, entidad in sorted(_SINONIMOS_ENTIDAD_ADICIONAL.items(),
                                    key=lambda kv: -len(kv[0])):
        if _normalizar(sinonimo) in wordles and entidad in ENTIDADES:
            return entidad
    # Sinónimos de cada entidad
    mejores = []
    for nombre_ent, meta in ENTIDADES.items():
        for sinonimo in meta["sinonimos"]:
            s = _normalizar(sinonimo)
            if s in wordles:
                # tokens de varios caracteres para evitar falsos positivos
                if len(s) >= 4:
                    mejores.append((len(s), nombre_ent, s))
    if not mejores:
        return None
    mejores.sort(key=lambda x: -x[0])
    return mejores[0][1]


def _detectar_medida(texto: str) -> str:
    """count | avg | avg_edad | sum_cantidad | list | top | sin_medida."""
    n = _normalizar(texto)
    for frase, medida in _VALOR_MEDIDA.items():
        if _normalizar(frase) in n:
            return medida
    if "suma" in n or "sumados" in n or "sumatorio" in n:
        return "sum_cantidad"
    if "cuantos" in n or "cuantas" in n or "numero de" in n or "cantidad de" in n:
        return "count"
    if "top" in n or "mas frecuentes" in n or "mas realizados" in n:
        return "top"
    if "listado" in n or "listame" in n or "listar" in n or "muestrame" in n \
            or "mostrar" in n or "lista de" in n or "cuales son" in n \
            or "cual es" in n or "cuales" in n or "cual" in n:
        return "list"
    for frase, medida in _SINONIMOS_MEDIDA.items():
        if _normalizar(frase) in n:
            return medida
    return "count"


def _detectar_agrupacion(texto: str) -> str | None:
    n = _normalizar(texto)
    for grilla in (
        r"por\s+([a-z ]+?)(?:$|\sfue|\sen\s|\sdurante)",
        r"agrup[ao]\s+por\s+([a-z ]+?)(?:$|\s)",
        r"segun\s+([a-z ]+?)(?:$|\s)",
    ):
        m = re.search(grilla, n)
        if m:
            token = re.sub(r"\s+", " ", m.group(1)).strip()
            # quitar restos temporales arrastrados: "sexo este mes", "sexo el año"
            token = re.sub(r"\s+(este|esta|el|la|los|las|del|en|durante)\s+\w[\w ]*$", "", token)
            token = re.sub(r"\s+(este|esta|el|la|los|las|del|en|durante)$", "", token)
            token = _ALIAS_AGRUPACION.get(token, token)
            if token in ("sexo", "genero"):
                return "sexo"
            return token
    return None


def _detectar_fechas(texto: str, hoy: date) -> tuple | None:
    """Devuelve (desde, hasta) — hasta exclusive — o None."""
    n = _normalizar(texto)
    if "hoy" in n:
        return hoy, hoy + timedelta(days=1)
    if "ayer" in n:
        return hoy - timedelta(days=1), hoy
    if "esta semana" in n:
        inicio = hoy - timedelta(days=hoy.weekday())
        return inicio, inicio + timedelta(days=7)
    if "este mes" in n or "en este mes" in n:
        inicio = hoy.replace(day=1)
        prox = (inicio.replace(day=28) + timedelta(days=4)).replace(day=1)
        return inicio, prox
    if "el mes pasado" in n or "mes pasado" in n:
        prox = hoy.replace(day=1)
        fin = (prox.replace(day=28) + timedelta(days=4)).replace(day=1)
        inicio = (prox - timedelta(days=1)).replace(day=1)
        return inicio, fin
    if "este anio" in n or "este ano" in n or "este año" in n:
        inicio = hoy.replace(month=1, day=1)
        return inicio, inicio.replace(year=hoy.year + 1, month=1, day=1)
    if "el anio pasado" in n or "anio pasado" in n:
        ano = hoy.year - 1
        return date(ano, 1, 1), date(ano + 1, 1, 1)
    m = re.search(r"ultimos?\s+(\d+)\s+(dia|dias|mes|meses|anio|anos|año|años)", n)
    if m:
        cant = int(m.group(1))
        unidad = m.group(2)
        if "dia" in unidad:
            return hoy - timedelta(days=cant - 1), hoy + timedelta(days=1)
        if "mes" in unidad:
            inicio = (hoy.replace(day=1) - timedelta(days=1)).replace(day=1)
            for _ in range(1, cant):
                inicio = (inicio.replace(day=1) - timedelta(days=1)).replace(day=1)
            return inicio, hoy + timedelta(days=1)
        if "anio" in unidad or "ano" in unidad:
            return date(hoy.year - cant + 1, 1, 1), hoy + timedelta(days=1)
    # Día+mes(+año): "el 1 de agosto 2026", "1 agosto 2026"
    m = re.search(r"(?:el\s+)?(\d{1,2})\s+(?:de\s+)?(enero|febrero|marzo|abril|"
                  r"mayo|junio|julio|agosto|septiembre|setiembre|octubre|"
                  r"noviembre|diciembre)(?:\s+de\s+)?(20\d{2})?\b", n)
    if m:
        dia = int(m.group(1))
        mes_nombre = m.group(2)
        ano = int(m.group(3)) if m.group(3) else hoy.year
        try:
            inicio = date(ano, MESES[mes_nombre], dia)
        except ValueError:
            inicio = None
        if inicio:
            return inicio, inicio + timedelta(days=1)
    m = re.search(r"(20\d{2})", n)
    if m:
        ano = int(m.group(1))
        return date(ano, 1, 1), date(ano + 1, 1, 1)
    m = re.search(r"en\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
                  r"septiembre|setiembre|octubre|noviembre|diciembre)(?:\s+de\s+)?(20\d{2})?", n)
    if m:
        mes_nombre = m.group(1)
        ano = int(m.group(2)) if m.group(2) else hoy.year
        inicio = date(ano, MESES[mes_nombre], 1)
        prox = (inicio.replace(day=28) + timedelta(days=4)).replace(day=1)
        return inicio, prox
    return None


def _detectar_sexo(texto: str) -> str | None:
    n = _normalizar(texto)
    if any(w in n for w in (" masculino", " hombres", " varones", " hombre ")) or \
            re.search(r"\b(hombre|hombres|varones|masc)\b", n):
        return "M"
    if any(w in n for w in (" femenino", " mujeres", " mujer ")) or \
            re.search(r"\b(mujer|mujeres|femen|femenina)\b", n):
        return "F"
    return None


def _detectar_estado(texto: str) -> str | None:
    n = _normalizar(texto)
    if "fallecidos" in n or " fallecido" in n or "fallecido " in n:
        return "F"
    if "inactivos" in n or " inactivo" in n or "inactivo " in n:
        return "I"
    return None


def _detectar_tipo_consulta(texto: str) -> str | None:
    n = _normalizar(texto)
    for nombre, codigo in TIPO_CONSULTA_POR_NOMBRE.items():
        if _normalizar(nombre) in n:
            return str(codigo)
    return None


def _extraer_top(texto: str, defecto: int = 10) -> int:
    m = re.search(r"top\s+(\d+)", _normalizar(texto))
    if m:
        return min(int(m.group(1)), 100)
    m = re.search(r"los\s+(\d+)\s+mas", _normalizar(texto))
    if m:
        return min(int(m.group(1)), 100)
    return defecto


# ---------------------------------------------------------------------------
# Generador
# ---------------------------------------------------------------------------

class PlanInvalido(Exception):
    pass


def _joins_entidad(meta: dict, necesita_paciente: bool,
                   necesita_especialidad: bool,
                   necesita_procedimiento: bool,
                   necesita_servicio: bool) -> str:
    partes = []
    if necesita_paciente and meta.get("join_paciente"):
        partes.append(meta["join_paciente"])
    if necesita_especialidad and meta.get("join_especialidad"):
        partes.append(meta["join_especialidad"])
    if necesita_procedimiento and meta.get("join_procedimiento"):
        partes.append(meta["join_procedimiento"])
    if necesita_servicio and meta.get("join_servicio"):
        partes.append(meta["join_servicio"])
    return "\n".join(partes)


def _detectar_especialidad(texto: str, especialidades: list[str]) -> str | None:
    """Busca en el texto un nombre de especialidad del catálogo (normalizado)."""
    if not especialidades:
        return None
    n = _normalizar(texto)
    for nombre in sorted(especialidades, key=len, reverse=True):
        if _normalizar(nombre) in n and len(_normalizar(nombre)) >= 3:
            return nombre
    return None


def generar_consulta(texto: str, reglas_extra: dict | None = None,
                     hoy: date | None = None,
                     especialidades: list[str] | None = None) -> dict:
    """Devuelve dict con 'sql', 'params', columnas y metadatos de respuesta."""
    reglas_extra = reglas_extra or {}
    hoy = hoy or date.today()
    especialidades = list(especialidades or [])

    entidad = _detectar_entidad(texto, reglas_extra)
    if entidad is None:
        raise PlanInvalido(
            "No reconozco sobre qué datos preguntas. Prueba con: pacientes, "
            "consultas, citas, medicos, nacimientos, defunciones, censo de "
            "camas, prestamos, procedimientos o constancias."
        )
    meta = ENTIDADES[entidad]

    medida = _detectar_medida(texto)
    agrupacion = _detectar_agrupacion(texto)
    rango = _detectar_fechas(texto, hoy)
    sexo = _detectar_sexo(texto)
    estado = _detectar_estado(texto)
    tipo_consulta = _detectar_tipo_consulta(texto)
    especialidad = _detectar_especialidad(texto, especialidades)

    # Validar agrupación soportada por la entidad
    grupo_ok = None
    if agrupacion and agrupacion in meta["agrupaciones"]:
        grupo_ok = agrupacion
    elif agrupacion and agrupacion in _ALIAS_AGRUPACION:
        can = _ALIAS_AGRUPACION[agrupacion]
        if can in meta["agrupaciones"]:
            grupo_ok = can

    joins = set()
    clausula_especialidad = None
    if grupo_ok == "especialidad" or especialidad:
        joins.add("especialidad")
    if (sexo or grupo_ok == "sexo") and meta.get("join_paciente"):
        joins.add("paciente")
    if tipo_consulta and entidad == "consultas":
        joins.add("especialidad")  # por simetría no, solo si se agrupa
    if grupo_ok == "procedimiento":
        joins.add("procedimiento")
    if grupo_ok == "servicio":
        joins.add("servicio")

    sql_joins = _joins_entidad(meta, "paciente" in joins, "especialidad" in joins,
                               "procedimiento" in joins, "servicio" in joins)

    where = []
    params = {}
    fecha_col = meta.get("fecha_col")
    if rango and fecha_col:
        where.append(f"{fecha_col} >= :desde AND {fecha_col} < :hasta")
        params["desde"] = str(rango[0])
        params["hasta"] = str(rango[1])
    if sexo:
        col_sexo = meta["alias_sql"].get("sexo", None) if meta.get("alias_sql") else None
        if not col_sexo:
            if meta.get("join_paciente"):
                col_sexo = "p.sexo"
            else:
                col_sexo = (meta.get("agrupaciones", {}).get("sexo") or ("", ""))[0].split(" AS")[0]
        where.append(f"({col_sexo}) = :sexo")
        params["sexo"] = sexo
    if estado and entidad == "pacientes":
        where.append("COALESCE(p.estado,'V') = :estado")
        params["estado"] = estado
    elif estado and entidad == "defunciones":
        where.append("d.es_fetal = :es_fetal" if estado == "F" else "1=1")
    if tipo_consulta and entidad == "consultas":
        where.append("c.tipo_consulta::int = :tipo_consulta")
        params["tipo_consulta"] = int(tipo_consulta)
    if especialidad and meta.get("join_especialidad"):
        where.append("e.nombre = :especialidad")
        params["especialidad"] = especialidad
    if meta.get("filtro_base"):
        where.append(meta["filtro_base"])

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    # Columnas de salida según métrica/agrupación
    if grupo_ok:
        expr, etiqueta = meta["agrupaciones"][grupo_ok]
        if medida == "top":
            select = f"{expr} AS {etiqueta}, COUNT(*) AS total"
            sql = (
                f"SELECT {select}\nFROM {meta['tabla']}\n{sql_joins}\n{where_sql}\n"
                f"GROUP BY {expr}\nORDER BY total DESC\nLIMIT :limite_top"
            )
            params["limite_top"] = _extraer_top(texto)
        elif medida == "avg" and grupo_ok == "sexo":
            edad_expr = meta["medidas"].get("edad")
            if not edad_expr:
                raise PlanInvalido("No puedo promediar esa dimensión.")
            sql = (
                f"SELECT {expr} AS {etiqueta}, ROUND(AVG({edad_expr})::numeric,1) AS promedio_edad\n"
                f"FROM {meta['tabla']}\n{sql_joins}\n{where_sql}\n"
                f"GROUP BY {expr}\nORDER BY {etiqueta}"
            )
        elif medida == "sum_cantidad" and meta.get("medidas", {}).get("cantidad"):
            sql = (
                f"SELECT {expr} AS {etiqueta}, SUM({meta['medidas']['cantidad']}) AS total\n"
                f"FROM {meta['tabla']}\n{sql_joins}\n{where_sql}\n"
                f"GROUP BY {expr}\nORDER BY total DESC"
            )
        else:
            sql = (
                f"SELECT {expr} AS {etiqueta}, COUNT(*) AS total\n"
                f"FROM {meta['tabla']}\n{sql_joins}\n{where_sql}\n"
                f"GROUP BY {expr}\nORDER BY {etiqueta}"
            )
        columnas = [etiqueta, "total"] if medida != "avg" else [etiqueta, "promedio_edad"]
        titulo = f"{_titulo_entidad(entidad)} agrupados por {etiqueta}"
    elif medida == "avg_edad":
        edad_expr = meta["medidas"].get("edad") if meta.get("medidas") else None
        if not edad_expr:
            raise PlanInvalido("No puedo calcular edad promedio en esta entidad.")
        sql = (f"SELECT ROUND(AVG({edad_expr})::numeric,1) AS promedio_edad\n"
               f"FROM {meta['tabla']}\n{sql_joins}\n{where_sql}")
        columnas = ["promedio_edad"]
        titulo = f"Promedio de edad en {_titulo_entidad(entidad)}"
    elif medida == "sum_cantidad" and meta.get("medidas", {}).get("cantidad"):
        sql = (f"SELECT SUM({meta['medidas']['cantidad']}) AS total\n"
               f"FROM {meta['tabla']}\n{sql_joins}\n{where_sql}")
        columnas = ["total"]
        titulo = f"Suma de cantidad en {_titulo_entidad(entidad)}"
    elif medida == "top":
        # Sin agrupación explícita: sigsa3 → diagnóstico; resto → primera dimensión
        if entidad == "sigsa3" and "diagnostico" in meta["agrupaciones"]:
            grupo = "diagnostico"
        else:
            grupo = next(iter(meta["agrupaciones"]))
        expr, etiqueta = meta["agrupaciones"][grupo]
        sql = (
            f"SELECT {expr} AS {etiqueta}, COUNT(*) AS total\n"
            f"FROM {meta['tabla']}\n{sql_joins}\n{where_sql}\n"
            f"GROUP BY {expr}\nORDER BY total DESC\nLIMIT :limite_top"
        )
        params["limite_top"] = _extraer_top(texto)
        columnas = [etiqueta, "total"]
        titulo = f"Top por {etiqueta} en {_titulo_entidad(entidad)}"
    elif medida == "list":
        sql = (f"SELECT *\nFROM {meta['tabla']}\n{sql_joins}\n{where_sql}\n"
               f"ORDER BY 1\nLIMIT :limite")
        params["limite"] = 20
        columnas = []
        titulo = f"Listado de {_titulo_entidad(entidad)}"
    else:  # count
        sql = (f"SELECT COUNT(*) AS total\nFROM {meta['tabla']}\n{sql_joins}\n{where_sql}")
        columnas = ["total"]
        titulo = f"Conteo de {_titulo_entidad(entidad)}"

    return {
        "sql": sql,
        "params": params,
        "columnas": columnas,
        "titulo": titulo,
        "entidad": entidad,
        "medida": medida,
        "agrupacion": grupo_ok,
        "filtros": {
            "rango": [str(rango[0]), str(rango[1])] if rango else None,
            "sexo": sexo,
            "estado": estado,
            "tipo_consulta": tipo_consulta,
            "especialidad": especialidad,
        },
    }


def _titulo_entidad(entidad: str) -> str:
    nombres = {
        "pacientes": "pacientes", "consultas": "consultas", "citas": "citas",
        "medicos": "médicos", "nacimientos": "nacimientos",
        "defunciones": "defunciones", "censo_camas": "censo de camas",
        "prestamos": "préstamos", "proce_medicos": "procedimientos",
        "sigsa3": "registros SIGSA-3",
        "constancia_nacimiento": "constancias de nacimiento",
    }
    return nombres.get(entidad, entidad.replace("_", " "))