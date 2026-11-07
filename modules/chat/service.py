"""Adapta el chat HTTP al intérprete determinístico de consultas estadísticas."""

from typing import List, Optional

from sqlalchemy.orm import Session

TABLAS_CONOCIDAS = {
    "pacientes": "Pacientes del hospital. Datos demográficos, estado, CUI, expediente. JSONB: nombre (nombre1,nombre2,nombre3), apellido1...5, datos_extra (socioeconomicos, neonatales, etc.)",
    "consultas": "Registro de consultas médicas. tipo_consulta (1=COEX, 2=Hosp, 3=Emerg), especialidad, paciente_id, fecha_consulta, activo",
    "personal_atencion": "Catálogo de médicos. nombre, colegiado, especialidad, activo",
    "users": "Usuarios del sistema. username, email, rol, activo",
    "citas": "Citas programadas. paciente_id, fecha_cita, especialidad, razon, estado",
    "ciclos_consulta": "Ciclos clínicos por consulta. consulta_id, descripcion, activo",
    "eventos_consulta": "Eventos clínicos (ingreso/evolución/egreso). consulta_id, tipo_evento, descripcion, creado_en",
    "catalogo_procedimientos": "Catálogo maestro de procedimientos. nombre, abreviatura, especialidad_ref, activo",
    "area_cuerpo_intervenida": "Catálogo de áreas del cuerpo intervenidas. codigo, nombre, region",
    "proce_medicos": "Procedimientos realizados. id_catalogo_procedimiento, especialidad_id, fecha, cantidad, desglose nino_m/nino_f/adulto_m/adulto_f",
    "constancia_nacimiento": "Constancias de nacimiento. paciente_id, madre_id, peso, sexo, estado_informe",
    "nacimientos": "Registro de nacimientos (sin datos redundantes). paciente_id, madre_id, peso_gramos, clasificacion_nacimiento, trabajo_parto",
    "nacimientos_legacy": "Datos históricos de nacimientos migrados de sistema anterior",
    "prestamos": "Préstamos de expedientes. paciente_id, tipo_documento, fecha_prestamo, fecha_devolucion, activo",
    "encamamiento": "Catálogo de servicios de encamamiento. nombre, activo",
    "censo_camas": "Censo diario por servicio con conteos de movimientos separados por sexo",
    "defunciones": "Registro de defunciones. paciente_id, es_fetal, fecha_defuncion, causa, estado",
    "sigsa3": "Registro SIGSA-3 de consultas externas. personal_salud, fecha_consulta, tipo_consulta, especialidad, cie10, sexo, area",
    "cie10_catalogo": "Catálogo CIE-10 de diagnósticos. codigo, descripcion, nivel, codigo_padre",
    "municipios": "Municipios de Guatemala. codigo, municipio, departamento",
    "paises_iso": "Países ISO. codigo, nombre, nacionalidad",
    "audit_log": "Registro de auditoría de accesos. tabla, accion, usuario_id, fecha",
    "personal_salud": "Catálogo de trabajadores de salud para SIGSA-3",
    "expediente_control": "Control de correlativos de expedientes. tipo, año, ultimo_numero",
}


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
