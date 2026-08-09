import re
import time
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

SQL_BLOCKED_KEYWORDS = re.compile(
    r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|'
    r'GRANT|REVOKE|EXECUTE|CALL|MERGE|COPY|LOAD|IMPORT|'
    r'FETCH|SET\s+(SESSION|ROLE|TRANSACTION)|RESET\s+(SESSION|ROLE)|'
    r'DEALLOCATE|PREPARE|EXPLAIN\s+(ANALYZE|VERBOSE)|VACUUM|ANALYZE)\b',
    re.IGNORECASE,
)

TABLAS_CONOCIDAS = {
    "pacientes": "Pacientes del hospital. Datos demográficos, estado, CUI, expediente. JSONB: nombre (nombre1,nombre2,nombre3), apellido1...5, datos_extra (socioeconomicos, neonatales, etc.)",
    "consultas": "Registro de consultas médicas. tipo_consulta (1=COEX, 2=Hosp, 3=Emerg), especialidad, paciente_id, fecha_consulta, medico_id, activo",
    "medicos": "Catálogo de médicos. nombre, colegiado, especialidad, activo",
    "users": "Usuarios del sistema. username, email, rol, activo",
    "citas": "Citas programadas. paciente_id, fecha_cita, especialidad, razon, estado",
    "ciclos_consulta": "Ciclos clínicos por consulta. consulta_id, descripcion, activo",
    "eventos_consulta": "Eventos clínicos (ingreso/evolución/egreso). consulta_id, tipo_evento, descripcion, creado_en",
    "procedimientos": "Catálogo de procedimientos. nombre, abreviatura, costo",
    "proce_medicos": "Procedimientos realizados. consulta_id, procedimiento_id, medico_id, fecha",
    "constancia_nacimiento": "Constancias de nacimiento. paciente_id, madre_id, peso, sexo, estado_informe",
    "nacimientos": "Registro de nacimientos (sin datos redundantes). paciente_id, madre_id, peso_gramos, clasificacion_nacimiento, trabajo_parto",
    "nacimientos_legacy": "Datos históricos de nacimientos migrados de sistema anterior",
    "prestamos": "Préstamos de expedientes. paciente_id, tipo_documento, fecha_prestamo, fecha_devolucion, activo",
    "encamamiento": "Catálogo de servicios de encamamiento. nombre, activo",
    "censo_camas": "Censo diario de camas. fecha, servicio, disponibles, ocupadas, sexo",
    "defunciones": "Registro de defunciones. paciente_id, es_fetal, fecha_defuncion, causa, estado",
    "sigsa3": "Registro SIGSA-3 de consultas externas. personal_salud, fecha_consulta, tipo_consulta, especialidad, cie10, sexo, area",
    "cie10_catalogo": "Catálogo CIE-10 de diagnósticos. codigo, descripcion, nivel, codigo_padre",
    "municipios": "Municipios de Guatemala. codigo, municipio, departamento",
    "paises_iso": "Países ISO. codigo, nombre, nacionalidad",
    "audit_log": "Registro de auditoría de accesos. tabla, accion, usuario_id, fecha",
    "personal_salud": "Catálogo de trabajadores de salud para SIGSA-3",
    "expediente_control": "Control de correlativos de expedientes. tipo, año, ultimo_numero",
}


def _validar_sql(sql: str) -> bool:
    sql_sin_comentarios = re.sub(r'--.*', '', sql)
    sql_sin_comentarios = re.sub(r'/\*.*?\*/', '', sql_sin_comentarios, flags=re.DOTALL)
    sql_sin_strings = re.sub(r"'[^']*'", '', sql_sin_comentarios)
    sql_sin_strings = re.sub(r'"\s*[^"]*"', '', sql_sin_strings)

    if SQL_BLOCKED_KEYWORDS.search(sql_sin_strings):
        return False

    stripped = sql_sin_strings.strip().upper()
    return stripped.startswith('SELECT') or stripped.startswith('WITH')


def _extraer_sql(texto: str) -> str:
    patrones = [
        r'```sql\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
        r'SELECT.*?;',
    ]
    for patron in patrones:
        match = re.search(patron, texto, re.DOTALL | re.IGNORECASE)
        if match:
            sql = match.group(1) if match.lastindex else match.group(0)
            if not sql.upper().startswith('SELECT') and not sql.upper().startswith('WITH'):
                continue
            return sql.strip()
    if texto.upper().startswith('SELECT') or texto.upper().startswith('WITH'):
        return texto.strip()
    return ""


def _obtener_tablas_relevantes(mensajes: List[dict], tablas_filtro: Optional[List[str]]) -> List[str]:
    texto = " ".join(m["content"] for m in mensajes).lower()
    if tablas_filtro:
        return [t for t in tablas_filtro if t in TABLAS_CONOCIDAS]
    return sorted(TABLAS_CONOCIDAS.keys())


def _construir_schema_context(tablas: List[str]) -> str:
    lineas: List[str] = []
    for nombre in tablas:
        desc = TABLAS_CONOCIDAS.get(nombre, "")
        lineas.append(f"- {nombre}: {desc}")
    return "\n".join(lineas)


def _ejecutar_sql(sql: str, db: Session, max_filas: int) -> tuple:
    inicio = time.time()
    result = db.execute(text(sql))
    filas = [dict(r._mapping) for r in result.fetchmany(max_filas)]
    # Convertir tipos no serializables
    for fila in filas:
        for k, v in fila.items():
            if hasattr(v, 'isoformat'):
                fila[k] = v.isoformat()
            elif isinstance(v, (bytes, bytearray)):
                fila[k] = str(v)
    columnas = list(filas[0].keys()) if filas else []
    ejecucion_ms = int((time.time() - inicio) * 1000)
    return filas, columnas, ejecucion_ms


def consultar(
    mensajes: List[dict],
    db: Session,
    max_filas: int = 100,
    tablas_filtro: Optional[List[str]] = None,
) -> dict:
    from modules.agente.service import ejecutar_consulta

    ultimo_usuario = next(
        (m["content"] for m in reversed(mensajes) if m["role"] == "user"),
        "",
    )
    if not ultimo_usuario:
        return {
            "respuesta": "Hazme una pregunta sobre los datos del hospital, "
                         "por ejemplo: ¿cuántos pacientes hay?",
            "datos": [],
            "columnas": [],
            "total_filas": 0,
            "ejecucion_ms": 0,
            "modelo": "agente-rule",
            "error": None,
        }

    resultado_agente = ejecutar_consulta(
        texto=ultimo_usuario, db=db, username=None, max_filas=max_filas
    )

    if resultado_agente.get("sql_generado"):
        return {
            "respuesta": resultado_agente["respuesta"],
            "datos": resultado_agente["datos"],
            "columnas": resultado_agente["columnas"],
            "total_filas": resultado_agente["total_filas"],
            "ejecucion_ms": resultado_agente["ejecucion_ms"],
            "modelo": "agente-rule",
            "error": None,
        }
    if resultado_agente.get("error"):
        return {
            "respuesta": f"{resultado_agente['respuesta']}",
            "datos": [],
            "columnas": [],
            "total_filas": 0,
            "ejecucion_ms": resultado_agente["ejecucion_ms"],
            "modelo": "agente-rule",
            "error": resultado_agente["error"],
        }

    return {
        "respuesta": resultado_agente["respuesta"],
        "datos": [],
        "columnas": [],
        "total_filas": 0,
        "ejecucion_ms": resultado_agente["ejecucion_ms"],
        "modelo": "agente-rule",
        "error": None,
    }