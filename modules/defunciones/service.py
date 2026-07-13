from datetime import datetime, date
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from modules.defunciones.models import DefuncionModel
from modules.defunciones.schemas import DefuncionCreate, DefuncionUpdate


def _fetchone(db: Session, sql: str, params: dict | None = None) -> dict | None:
    r = db.execute(text(sql), params or {}).mappings().first()
    return dict(r) if r else None


def _fetchall(db: Session, sql: str, params: dict | None = None) -> list[dict]:
    return [dict(r) for r in db.execute(text(sql), params or {}).mappings().all()]


_DEF_COLS = """
    d.id, d.medico_id, d.fecha_defuncion,
    d.paciente_id, d.fallecido_edad_horas, d.fallecido_edad_dias,
    d.fallecido_edad_meses, d.fallecido_edad_anios, d.mujer_edad_fertil,
    d.muerte_gestacion,
    d.causa_a, d.causa_b, d.causa_c, d.causa_d, d.causa_intervalo, d.causa_otros,
    d.fue_presunto, d.lugar_lesion, d.ocurrio_trabajo, d.accidente_transito, d.arma,
    d.madre_id, d.madre_edad, d.madre_sabe_leer_escribir,
    d.es_fetal, d.embarazos_previvos_vivos, d.embarazos_previvos_muertos,
    d.fetal_sexo, d.fetal_murio_antes_parto, d.fetal_parto_tipo, d.fetal_clase_parto,
    d.fetal_via_parto, d.fetal_semanas_gestacion, d.fetal_causas_fetales, d.fetal_causas_maternas,
    d.registrador_id, d.observaciones, d.created_at, d.updated_at
"""


def _edad_en_momento(fecha_nac: date | datetime | None, fecha_def: datetime | None) -> dict:
    if not fecha_nac or not fecha_def:
        return {"horas": None, "dias": None, "meses": None, "anios": None}

    nac = fecha_nac if isinstance(fecha_nac, datetime) else datetime.combine(fecha_nac, datetime.min.time())
    if getattr(fecha_def, 'tzinfo', None) is not None:
        fecha_def = fecha_def.replace(tzinfo=None)
    if getattr(nac, 'tzinfo', None) is not None:
        nac = nac.replace(tzinfo=None)
    delta = fecha_def - nac
    total_horas = delta.total_seconds() / 3600

    if total_horas < 24:
        return {"horas": int(total_horas), "dias": None, "meses": None, "anios": None}

    def_date = fecha_def.date()
    nac_date = nac.date()
    delta_days = (def_date - nac_date).days

    if delta_days < 30:
        return {"horas": None, "dias": delta_days, "meses": None, "anios": None}

    meses = (def_date.year - nac_date.year) * 12 + (def_date.month - nac_date.month)
    if def_date.day < nac_date.day:
        meses -= 1

    if meses < 12:
        return {"horas": None, "dias": None, "meses": max(1, meses), "anios": None}

    anios = meses // 12
    return {"horas": None, "dias": None, "meses": None, "anios": anios}


_PACIENTE_SELECT = """
    p.id AS p_id, p.expediente AS p_expediente, p.cui AS p_cui,
    p.nombre_completo AS p_nombre_completo, p.nombre AS p_nombre,
    p.sexo AS p_sexo, p.fecha_nacimiento AS p_fecha_nacimiento, p.estado AS p_estado,
    p.datos_extra
"""

_MEDICO_SELECT = """
    doc.id AS m_id, doc.nombre AS m_nombre, doc.colegiado AS m_colegiado, doc.especialidad AS m_especialidad
"""


def _build_paciente(row: dict, prefix: str = "p") -> dict | None:
    if not row.get(f"{prefix}_id"):
        return None
    nombre = row.get(f"{prefix}_nombre")
    if nombre and isinstance(nombre, str):
        try:
            import json
            nombre = json.loads(nombre)
        except Exception:
            pass
    cui = row.get(f"{prefix}_cui")
    cui_str = str(cui) if cui is not None else None

    de = row.get(f"{prefix}_datos_extra")
    if de and isinstance(de, str):
        try:
            import json
            de = json.loads(de)
        except Exception:
            de = None

    defuncion = None
    if de and isinstance(de, dict):
        defuncion = de.get("defuncion")

    return {
        "id": row[f"{prefix}_id"],
        "expediente": row.get(f"{prefix}_expediente"),
        "cui": cui_str,
        "nombre_completo": row.get(f"{prefix}_nombre_completo"),
        "nombre": nombre if isinstance(nombre, dict) else None,
        "sexo": row.get(f"{prefix}_sexo"),
        "fecha_nacimiento": row.get(f"{prefix}_fecha_nacimiento"),
        "estado": row.get(f"{prefix}_estado"),
        "cui_formateado": cui_str,
        "defuncion": defuncion,
    }


def _build_medico(row: dict) -> dict | None:
    if not row.get("m_id"):
        return None
    return {
        "id": row["m_id"],
        "nombre": row.get("m_nombre"),
        "colegiado": row.get("m_colegiado"),
        "especialidad": row.get("m_especialidad"),
    }


def _build_out(row: dict) -> dict:
    out = {k: row.get(k) for k in [
        "id", "medico_id", "fecha_defuncion", "paciente_id",
        "fallecido_edad_horas", "fallecido_edad_dias", "fallecido_edad_meses",
        "fallecido_edad_anios", "mujer_edad_fertil", "muerte_gestacion",
        "causa_a", "causa_b", "causa_c", "causa_d", "causa_intervalo", "causa_otros",
        "fue_presunto", "lugar_lesion", "ocurrio_trabajo", "accidente_transito", "arma",
        "madre_id", "madre_edad", "madre_sabe_leer_escribir",
        "es_fetal", "embarazos_previvos_vivos", "embarazos_previvos_muertos",
        "fetal_sexo", "fetal_murio_antes_parto", "fetal_parto_tipo", "fetal_clase_parto",
        "fetal_via_parto", "fetal_semanas_gestacion", "fetal_causas_fetales",
        "fetal_causas_maternas", "registrador_id", "observaciones",
        "created_at", "updated_at",
    ]}

    out["mujer_edad_fertil"] = bool(out.get("mujer_edad_fertil") or False)
    out["es_fetal"] = bool(out.get("es_fetal") or False)

    out["paciente"] = _build_paciente(row, "p")
    out["madre"] = _build_paciente(row, "madre")

    # For madre, override prefix: madre_id is stored as mad_id in query
    madre_prefix = "madre"
    if row.get(f"{madre_prefix}_id"):
        out["madre"] = _build_paciente(row, madre_prefix)

    out["medico"] = _build_medico(row)

    return out


def _recalcular_edad(db: Session, defuncion_id: int):
    """Recalcula edad del fallecido y madre desde pacientes."""
    row = _fetchone(db, f"""
        SELECT {_DEF_COLS}, p.fecha_nacimiento AS p_fecha_nac, p.sexo AS p_sexo,
               m.fecha_nacimiento AS madre_fecha_nac, m.datos_extra AS madre_datos_extra
        FROM defunciones d
        LEFT JOIN pacientes p ON p.id = d.paciente_id
        LEFT JOIN pacientes m ON m.id = d.madre_id
        WHERE d.id = :id
    """, {"id": defuncion_id})
    if not row:
        return

    cambios = {}

    # Edad del fallecido
    if row.get("paciente_id") and row.get("p_fecha_nac") and row.get("fecha_defuncion"):
        edad = _edad_en_momento(row["p_fecha_nac"], row["fecha_defuncion"])
        for k, v in [("fallecido_edad_horas", edad["horas"]),
                     ("fallecido_edad_dias", edad["dias"]),
                     ("fallecido_edad_meses", edad["meses"]),
                     ("fallecido_edad_anios", edad["anios"])]:
            if v is not None:
                cambios[k] = v

    # mujer_edad_fertil
    if row.get("p_sexo") == "2" and row.get("p_fecha_nac") and row.get("fecha_defuncion"):
        edad_anios = _edad_en_momento(row["p_fecha_nac"], row["fecha_defuncion"])["anios"]
        if edad_anios is not None:
            cambios["mujer_edad_fertil"] = 10 <= edad_anios <= 54

    # Edad de la madre
    if row.get("madre_id") and row.get("madre_fecha_nac") and row.get("fecha_defuncion"):
        edad_madre = _edad_en_momento(row["madre_fecha_nac"], row["fecha_defuncion"])["anios"]
        if edad_madre is not None:
            cambios["madre_edad"] = edad_madre

    # madre_sabe_leer_escribir from datos_extra.socioeconomico.educacion
    if row.get("madre_datos_extra"):
        de = row["madre_datos_extra"]
        if isinstance(de, str):
            import json
            try:
                de = json.loads(de)
            except Exception:
                de = None
        if de and isinstance(de, dict):
            socio = de.get("socioeconomico") or de.get("socioeconomicos") or {}
            educacion = socio.get("educacion")
            if educacion:
                if str(educacion) in ("0", "NINGUNA", "NINGUNO"):
                    cambios["madre_sabe_leer_escribir"] = "NO"
                else:
                    cambios["madre_sabe_leer_escribir"] = "SI"

    if cambios:
        set_clause = ", ".join(f"{k} = :{k}" for k in cambios)
        cambios["id"] = defuncion_id
        db.execute(text(f"UPDATE defunciones SET {set_clause} WHERE id = :id"), cambios)
        db.commit()


def crear_defuncion(data: DefuncionCreate, registrador_id: int | None, db: Session) -> dict:
    defuncion = DefuncionModel(
        registrador_id=registrador_id,
        **data.model_dump(exclude_unset=True),
    )
    db.add(defuncion)
    db.commit()
    db.refresh(defuncion)

    _recalcular_edad(db, defuncion.id)

    return obtener_defuncion(defuncion.id, db)


def listar_defunciones(
    db: Session,
    q: Optional[str] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    es_fetal: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[dict], int]:
    where_clauses = []
    params: dict = {}

    if q:
        where_clauses.append("(p.nombre_completo ILIKE :q OR m.nombre_completo ILIKE :q OR doc.nombre ILIKE :q)")
        params["q"] = f"%{q}%"
    if fecha_desde:
        where_clauses.append("d.fecha_defuncion >= :fecha_desde")
        params["fecha_desde"] = fecha_desde
    if fecha_hasta:
        where_clauses.append("d.fecha_defuncion <= :fecha_hasta")
        params["fecha_hasta"] = fecha_hasta
    if es_fetal is not None:
        where_clauses.append("d.es_fetal = :es_fetal")
        params["es_fetal"] = es_fetal

    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

    joins = """
        LEFT JOIN pacientes p ON p.id = d.paciente_id
        LEFT JOIN pacientes m ON m.id = d.madre_id
        LEFT JOIN medicos doc ON doc.id = d.medico_id
    """

    count_sql = f"SELECT COUNT(*) FROM defunciones d {joins} WHERE {where_sql}"
    total = db.execute(text(count_sql), params).scalar()

    data_sql = f"""
        SELECT {_DEF_COLS}, {_PACIENTE_SELECT}, {_MEDICO_SELECT},
               m.id AS madre_id, m.nombre_completo AS madre_nombre_completo,
               m.nombre AS madre_nombre, m.sexo AS madre_sexo,
               m.fecha_nacimiento AS madre_fecha_nacimiento,
               m.estado AS madre_estado, m.cui AS madre_cui,
               m.expediente AS madre_expediente, m.datos_extra AS madre_datos_extra
        FROM defunciones d
        {joins}
        WHERE {where_sql}
        ORDER BY d.fecha_defuncion DESC NULLS LAST, d.id DESC
        LIMIT :limit OFFSET :skip
    """
    params["limit"] = limit
    params["skip"] = skip
    rows = db.execute(text(data_sql), params).mappings().all()

    return [_build_out(dict(r)) for r in rows], total


def obtener_defuncion(defuncion_id: int, db: Session) -> dict:
    defuncion = db.query(DefuncionModel).filter(DefuncionModel.id == defuncion_id).first()
    if not defuncion:
        raise HTTPException(status_code=404, detail="Registro de defunción no encontrado")

    _recalcular_edad(db, defuncion_id)

    row = _fetchone(db, f"""
        SELECT {_DEF_COLS}, {_PACIENTE_SELECT}, {_MEDICO_SELECT},
               m.id AS madre_id, m.nombre_completo AS madre_nombre_completo,
               m.nombre AS madre_nombre, m.sexo AS madre_sexo,
               m.fecha_nacimiento AS madre_fecha_nacimiento,
               m.estado AS madre_estado, m.cui AS madre_cui,
               m.expediente AS madre_expediente, m.datos_extra AS madre_datos_extra
        FROM defunciones d
        LEFT JOIN pacientes p ON p.id = d.paciente_id
        LEFT JOIN pacientes m ON m.id = d.madre_id
        LEFT JOIN medicos doc ON doc.id = d.medico_id
        WHERE d.id = :id
    """, {"id": defuncion_id})
    return _build_out(row)


def actualizar_defuncion(defuncion_id: int, data: DefuncionUpdate, db: Session) -> dict:
    defuncion = db.query(DefuncionModel).filter(DefuncionModel.id == defuncion_id).first()
    if not defuncion:
        raise HTTPException(status_code=404, detail="Registro de defunción no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(defuncion, key, value)

    db.commit()
    db.refresh(defuncion)

    _recalcular_edad(db, defuncion_id)

    return obtener_defuncion(defuncion_id, db)


def buscar_pacientes_fallecidos(
    db: Session,
    q: Optional[str] = None,
    expediente: Optional[str] = None,
    cui: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[dict], int]:
    where_clauses = ["p.estado = 'F'"]
    params: dict = {}

    if q:
        where_clauses.append("p.nombre_completo ILIKE :q")
        params["q"] = f"%{q}%"
    if expediente:
        where_clauses.append("p.expediente ILIKE :expediente")
        params["expediente"] = f"%{expediente}%"
    if cui:
        where_clauses.append("CAST(p.cui AS TEXT) ILIKE :cui")
        params["cui"] = f"%{cui}%"

    where_sql = " AND ".join(where_clauses)

    count_sql = f"SELECT COUNT(*) FROM pacientes p WHERE {where_sql}"
    total = db.execute(text(count_sql), params).scalar()

    data_sql = f"""
        SELECT p.id, p.expediente, p.cui, p.nombre_completo, p.nombre,
               p.sexo, p.fecha_nacimiento, p.estado, p.datos_extra,
               d.id AS defuncion_id, d.fecha_defuncion, d.medico_id,
               d.causa_a, d.causa_b, d.causa_c, d.causa_d,
               d.fallecido_edad_anios, d.muerte_gestacion,
               d.es_fetal, d.mujer_edad_fertil,
               d.lugar_lesion, d.fue_presunto
        FROM pacientes p
        LEFT JOIN defunciones d ON d.paciente_id = p.id
        WHERE {where_sql}
        ORDER BY p.nombre_completo
        LIMIT :limit OFFSET :skip
    """
    params["limit"] = limit
    params["skip"] = skip
    rows = db.execute(text(data_sql), params).mappings().all()

    result = []
    for r in rows:
        r = dict(r)
        nombre = r.get("nombre")
        if nombre and isinstance(nombre, str):
            try:
                import json
                nombre = json.loads(nombre)
            except Exception:
                pass

        de = r.get("datos_extra")
        if de and isinstance(de, str):
            try:
                import json
                de = json.loads(de)
            except Exception:
                de = None

        result.append({
            "id": r["id"],
            "expediente": r.get("expediente"),
            "cui": str(r["cui"]) if r.get("cui") else None,
            "nombre_completo": r.get("nombre_completo"),
            "nombre": nombre if isinstance(nombre, dict) else None,
            "sexo": r.get("sexo"),
            "fecha_nacimiento": r.get("fecha_nacimiento"),
            "estado": r.get("estado"),
            "defuncion": {
                "id": r.get("defuncion_id"),
                "fecha_defuncion": r.get("fecha_defuncion"),
                "medico_id": r.get("medico_id"),
                "causa_a": r.get("causa_a"),
                "causa_b": r.get("causa_b"),
                "causa_c": r.get("causa_c"),
                "causa_d": r.get("causa_d"),
                "edad_anios": r.get("fallecido_edad_anios"),
                "muerte_gestacion": r.get("muerte_gestacion"),
                "es_fetal": r.get("es_fetal"),
                "mujer_edad_fertil": r.get("mujer_edad_fertil"),
                "lugar_lesion": r.get("lugar_lesion"),
                "fue_presunto": r.get("fue_presunto"),
            } if r.get("defuncion_id") else None,
        })

    return result, total


def eliminar_defuncion(defuncion_id: int, db: Session) -> None:
    defuncion = db.query(DefuncionModel).filter(DefuncionModel.id == defuncion_id).first()
    if not defuncion:
        raise HTTPException(status_code=404, detail="Registro de defunción no encontrado")
    try:
        db.delete(defuncion)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar, está relacionado con otros registros"
        )
