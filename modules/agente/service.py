"""Servicio del agente estadístico: aprende de sinónimos/feedback, interpreta
la consulta, ejecuta el SQL generado y construye una respuesta en lenguaje
natural. No depende de ningún LLM ni API key."""
import time
from typing import List, Optional

from sqlalchemy import text, func, select
from sqlalchemy.orm import Session

from modules.agente.interpreter import PlanInvalido, generar_consulta
from modules.agente.entidades import ENTIDADES, TIPO_CONSULTA_MAPA
from modules.agente.models import ReglaAgente, FeedbackAgente

try:
    from modules.especialidades.models import EspecialidadModel
except Exception:  # pragma: no cover
    EspecialidadModel = None


def _cargar_reglas(db: Session) -> dict:
    """Agrupa reglas aprendidas por tipo para inyectarlas al intérprete."""
    reglas = db.execute(
        select(ReglaAgente).order_by(ReglaAgente.veces_exito.desc())
    ).scalars().all()
    sinonimos_entidad = {}
    sinonimos_agrupacion = {}
    sinonimos_medida = {}
    for r in reglas:
        if r.tipo == "sinonimo_entidad":
            sinonimos_entidad[r.clave] = r.valor
        elif r.tipo == "sinonimo_agrupacion":
            sinonimos_agrupacion[r.clave] = r.valor
        elif r.tipo == "sinonimo_medida":
            sinonimos_medida[r.clave] = r.valor
    return {
        "entidad": sinonimos_entidad,
        "agrupacion": sinonimos_agrupacion,
        "medida": sinonimos_medida,
    }


def _cargar_especialidades(db: Session) -> list:
    try:
        return [r[0] for r in db.execute(
            select(EspecialidadModel.nombre).distinct().order_by(EspecialidadModel.nombre)
        ).all()]
    except Exception:
        return []


def _marcar_uso(db: Session, regla_tipo: str = None):
    """Contador de uso (placeholder simple; la litis log de uso se hace por
    query en el router de feedback)."""


def ejecutar_consulta(texto: str, db: Session, username: str = None,
                      max_filas: int = 100) -> dict:
    """Flujo principal del agente: interpreta → ejecuta → responde."""
    inicio = time.time()
    resultado = {
        "respuesta": "", "datos": [], "columnas": [], "sql_generado": None,
        "total_filas": 0, "ejecucion_ms": 0, "modelo": "agente-rule",
        "error": None,
    }

    try:
        reglas = _cargar_reglas(db)
        plan = generar_consulta(
            texto,
            reglas_extra=reglas["entidad"],
            hoy=None,
            especialidades=_cargar_especialidades(db) if EspecialidadModel else [],
        )
    except PlanInvalido as e:
        resultado["respuesta"] = str(e)
        resultado["ejecucion_ms"] = int((time.time() - inicio) * 1000)
        return resultado
    except Exception as e:
        resultado["respuesta"] = f"No pude procesar tu consulta: {e}"
        resultado["error"] = str(e)
        resultado["ejecucion_ms"] = int((time.time() - inicio) * 1000)
        return resultado

    resultado["sql_generado"] = plan["sql"]
    try:
        filas, columnas, ejecucion_ms = _ejecutar(plan, db, max_filas)
    except Exception as e:
        resultado["respuesta"] = f"Error al ejecutar la consulta: {e}"
        resultado["error"] = str(e)
        resultado["ejecucion_ms"] = int((time.time() - inicio) * 1000)
        return resultado

    resultado["datos"] = filas
    resultado["columnas"] = columnas
    resultado["total_filas"] = len(filas)
    resultado["ejecucion_ms"] = ejecucion_ms + int((time.time() - inicio) * 1000)
    resultado["respuesta"] = _redactar(texto, plan, filas, columnas)
    return resultado


def _ejecutar(plan: dict, db: Session, max_filas: int) -> tuple:
    inicio = time.time()
    result = db.execute(text(plan["sql"]), plan["params"])
    filas_raw = result.fetchmany(max_filas)
    filas = []
    for fila in filas_raw:
        fila_dict = {}
        for k, v in fila._mapping.items():
            if hasattr(v, "isoformat"):
                fila_dict[k] = v.isoformat()
            elif isinstance(v, (bytes, bytearray)):
                fila_dict[k] = str(v)
            else:
                fila_dict[k] = v
        filas.append(fila_dict)
    columnas = list(filas[0].keys()) if filas else plan["columnas"]
    ms = int((time.time() - inicio) * 1000)
    return filas, columnas, ms


def _redactar(texto: str, plan: dict, filas: list, columnas: list) -> str:
    entidad = _titulo_entidad(plan["entidad"])
    f = plan["filtros"]

    prefijo = ""
    if f.get("rango"):
        prefijo = f" del {f['rango'][0]} al {f['rango'][1]}"
    if f.get("especialidad"):
        prefijo += f" de {f['especialidad']}"
    if f.get("sexo"):
        prefijo += " " + ("hombres" if f["sexo"] == "M" else "mujeres")
    if f.get("estado"):
        prefijo += f" {f['estado']}"
    if f.get("tipo_consulta"):
        prefijo += f" tipo {TIPO_CONSULTA_MAPA.get(int(f['tipo_consulta']), f['tipo_consulta'])}"

    if not filas:
        return f"No se encontraron registros de {entidad}{prefijo}."

    medida = plan["medida"]
    if plan["agrupacion"]:
        if medida == "avg":
            return f"Promedio por {plan['agrupacion']} de {entidad}{prefijo}: " \
                   f"{filas[0].get('promedio_edad', '?')} años (ver datos)."
        if len(filas) == 1:
            return f"En {entidad}{prefijo} hay {filas[0].get('total', 0)} registros."
        return (f"Distribución de {entidad}{prefijo} por {plan['agrupacion']} "
                f"({len(filas)} grupos; ver datos).")
    if medida == "avg_edad":
        return f"El promedio de edad de {entidad}{prefijo} es " \
               f"{filas[0].get('promedio_edad', '?')} años."
    if medida == "sum_cantidad":
        return f"La suma de cantidad en {entidad}{prefijo} es " \
               f"{filas[0].get('total', 0)}."
    if medida == "top":
        return f"Top resultados de {entidad}{prefijo}: {len(filas)} grupos (ver datos)."
    if medida == "list":
        return f"Se muestran {len(filas)} registros de {entidad}{prefijo} (ver datos)."
    total = filas[0].get("total", 0) if filas else 0
    return f"Hay {total} {entidad}{prefijo}."


def _titulo_entidad(entidad: str) -> str:
    nombres = {
        "pacientes": "pacientes", "consultas": "consultas", "citas": "citas",
        "medicos": "médicos", "nacimientos": "nacimientos",
        "defunciones": "defunciones", "censo_camas": "reportes de camas",
        "prestamos": "préstamos", "proce_medicos": "procedimientos",
        "sigsa3": "registros SIGSA-3",
        "constancia_nacimiento": "constancias de nacimiento",
    }
    return nombres.get(entidad, entidad.replace("_", " "))