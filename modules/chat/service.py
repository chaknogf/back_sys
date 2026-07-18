import re
import time
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from core.config import (
    CHAT_LLM_API_KEY,
    CHAT_LLM_MODEL,
    CHAT_LLM_PROVIDER,
    CHAT_LLM_BASE_URL,
    OLLAMA_HOST,
    OPENCODE_SERVER_URL,
    OPENCODE_SERVER_PASSWORD,
)

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


SISTEMA_PROMPT_TEMPLATE = """Eres un asistente SQL que convierte preguntas en lenguaje natural a consultas SQL para PostgreSQL.

Reglas estrictas:
- GENERA ÚNICAMENTE sentencias SELECT. NUNCA INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT u otras.
- Usa SQL válido para PostgreSQL.
- Usa ILIKE para búsquedas de texto parcial. Ej: nombre ILIKE '%texto%'
- Usa unaccent() para ignorar acentos: unaccent(nombre) ILIKE unaccent('%texto%')
- Accede a campos JSONB con operador ->>. Ej: pacientes.datos_extra->'socioeconomicos'->>'personal_hospital'
- El JSONB nombre tiene campos: nombre1, nombre2, nombre3, apellido1..5
- Para fechas usa formato 'YYYY-MM-DD' y compara con >= y <.
- LIMITA los resultados a {max_filas} filas. Usa LIMIT {max_filas}.
- Siempre incluye ORDER BY apropiado.
- Si necesitas calcular edad: EXTRACT(YEAR FROM age(fecha_nac)) (si fecha_nac existe)
- Devuelve SOLO el SQL, sin markdown ni explicaciones.
- Si la pregunta NO se puede responder con SQL, responde exactamente: NO_SQL: [explicación breve]

Tablas disponibles en la base de datos hospital:
{tablas_contexto}"""


def _llm_ollama(messages: List[dict]) -> str:
    import httpx
    model = CHAT_LLM_MODEL
    url = f"{OLLAMA_HOST}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.1},
    }
    with httpx.Client(timeout=120) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "").strip()


def _llm_openai(messages: List[dict]) -> str:
    import httpx
    model = CHAT_LLM_MODEL
    api_url = f"{CHAT_LLM_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {CHAT_LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 1500,
    }
    with httpx.Client(verify=True, timeout=60) as client:
        resp = client.post(api_url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


def _llm_opencode(messages: List[dict]) -> str:
    import httpx
    import uuid

    url_base = OPENCODE_SERVER_URL.rstrip("/")
    auth_headers = {}
    if OPENCODE_SERVER_PASSWORD:
        import base64
        token = base64.b64encode(f"opencode:{OPENCODE_SERVER_PASSWORD}".encode()).decode()
        auth_headers["Authorization"] = f"Basic {token}"

    session_id = None
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                f"{url_base}/session",
                json={"title": f"chat-sql-{uuid.uuid4().hex[:8]}"},
                headers=auth_headers,
            )
            resp.raise_for_status()
            session_id = resp.json()["id"]

        # Extraer system prompt aparte si existe
        system_text = None
        user_msgs = []
        for m in messages:
            if m["role"] == "system":
                system_text = m["content"]
            else:
                user_msgs.append(m)

        prompt_text = "\n".join(
            f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
            for m in user_msgs
        )
        if system_text:
            prompt_text = f"[INSTRUCCIONES DEL SISTEMA]\n{system_text}\n\n[CONVERSACION]\n{prompt_text}"

        with httpx.Client(timeout=120) as client:
            resp = client.post(
                f"{url_base}/session/{session_id}/message",
                json={
                    "parts": [{"type": "text", "text": prompt_text}],
                },
                headers=auth_headers,
            )
            resp.raise_for_status()
            data = resp.json()
            textos = []
            for part in data.get("parts", []):
                if part.get("type") == "text":
                    textos.append(part.get("text", ""))
            return "\n".join(textos).strip()

    finally:
        if session_id:
            try:
                with httpx.Client(timeout=5) as client:
                    client.delete(
                        f"{url_base}/session/{session_id}",
                        headers=auth_headers,
                    )
            except Exception:
                pass


PROVIDERS = {
    "ollama": _llm_ollama,
    "openai": _llm_openai,
    "opencode": _llm_opencode,
}


def _llm_chat(messages: List[dict]) -> str:
    provider = CHAT_LLM_PROVIDER.lower()
    if provider == "ollama":
        try:
            return _llm_ollama(messages)
        except Exception as e:
            if CHAT_LLM_API_KEY:
                return _llm_openai(messages)
            raise ValueError(
                f"Ollama no disponible: {e}. "
                "Instálalo con: brew install ollama && ollama pull phi3:mini"
            )
    if provider == "opencode":
        if not OPENCODE_SERVER_URL:
            raise ValueError(
                "OPENCODE_SERVER_URL no configurado. "
                "Ejecuta 'opencode serve' y configura la URL en .env"
            )
        return _llm_opencode(messages)
    llm_fn = PROVIDERS.get(provider)
    if not llm_fn:
        raise ValueError(
            f"Proveedor desconocido: {provider} "
            f"(usa 'ollama', 'openai' u 'opencode')"
        )
    return llm_fn(messages)


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
    tablas = _obtener_tablas_relevantes(mensajes, tablas_filtro)
    schema_context = _construir_schema_context(tablas)
    system_prompt = SISTEMA_PROMPT_TEMPLATE.format(
        max_filas=max_filas,
        tablas_contexto=schema_context,
    )
    system_msg = {"role": "system", "content": system_prompt}
    messages_with_system = [system_msg] + mensajes

    # 1. LLM genera SQL
    inicio = time.time()
    try:
        respuesta_llm = _llm_chat(messages_with_system)
    except Exception as e:
        return {
            "respuesta": f"No pude conectar con el modelo de lenguaje: {e}",
            "datos": [],
            "columnas": [],
            "sql_generado": None,
            "total_filas": 0,
            "ejecucion_ms": int((time.time() - inicio) * 1000),
            "modelo": f"{CHAT_LLM_PROVIDER}:{CHAT_LLM_MODEL}",
            "error": str(e),
        }

    # 2. Verificar si el LLM dijo NO_SQL
    if respuesta_llm.upper().startswith("NO_SQL:"):
        return {
            "respuesta": respuesta_llm[7:].strip(),
            "datos": [],
            "columnas": [],
            "sql_generado": None,
            "total_filas": 0,
            "ejecucion_ms": int((time.time() - inicio) * 1000),
            "modelo": f"{CHAT_LLM_PROVIDER}:{CHAT_LLM_MODEL}",
            "error": None,
        }

    # 3. Extraer SQL
    sql = _extraer_sql(respuesta_llm)
    if not sql:
        return {
            "respuesta": "No pude generar una consulta SQL para tu pregunta. Sé más específico.",
            "datos": [],
            "columnas": [],
            "sql_generado": respuesta_llm[:500],
            "total_filas": 0,
            "ejecucion_ms": int((time.time() - inicio) * 1000),
            "modelo": f"{CHAT_LLM_PROVIDER}:{CHAT_LLM_MODEL}",
            "error": "No se pudo extraer SQL válido",
        }

    # 4. Validar SQL (solo SELECT)
    if not _validar_sql(sql):
        return {
            "respuesta": "La consulta generada no es válida (solo se permiten SELECT).",
            "datos": [],
            "columnas": [],
            "sql_generado": sql,
            "total_filas": 0,
            "ejecucion_ms": int((time.time() - inicio) * 1000),
            "modelo": f"{CHAT_LLM_PROVIDER}:{CHAT_LLM_MODEL}",
            "error": "SQL bloqueado por seguridad",
        }

    # 5. Ejecutar SQL
    try:
        filas, columnas, ejecucion_ms = _ejecutar_sql(sql, db, max_filas)
    except Exception as e:
        return {
            "respuesta": f"Error al ejecutar la consulta: {e}",
            "datos": [],
            "columnas": [],
            "sql_generado": sql,
            "total_filas": 0,
            "ejecucion_ms": int((time.time() - inicio) * 1000),
            "modelo": f"{CHAT_LLM_PROVIDER}:{CHAT_LLM_MODEL}",
            "error": str(e),
        }

    # 6. Generar respuesta natural con LLM sobre los resultados
    if filas:
        resumen = f"La consulta devolvió {len(filas)} filas. Los datos están disponibles en el campo 'datos'."
    else:
        resumen = "La consulta no devolvió resultados."

    return {
        "respuesta": resumen,
        "datos": filas,
        "columnas": columnas,
        "sql_generado": sql,
        "total_filas": len(filas),
        "ejecucion_ms": ejecucion_ms,
        "modelo": f"{CHAT_LLM_PROVIDER}:{CHAT_LLM_MODEL}",
        "error": None,
    }
