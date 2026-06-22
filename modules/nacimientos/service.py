import json
import re
from datetime import date
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from typing import Optional

from modules.nacimientos.models import NacimientoModel
from modules.nacimientos.schemas import NacimientoCreate, NacimientoUpdate, LegacyReferenceOut


def _fetchone(db: Session, sql: str, params: dict | None = None) -> dict | None:
    r = db.execute(text(sql), params or {}).mappings().first()
    return dict(r) if r else None


def _fetchall(db: Session, sql: str, params: dict | None = None) -> list[dict]:
    return [dict(r) for r in db.execute(text(sql), params or {}).mappings().all()]


_NACIMIENTO_COLS = """
    n.id, n.paciente_id, n.madre_id, n.registrador_id,
    n.created_at, n.updated_at,
    n.peso_gramos, n.clasificacion_nacimiento, n.trabajo_parto
"""

_PACIENTE_JOIN = """
    LEFT JOIN pacientes p ON p.id = n.paciente_id
"""

_MADRE_JOIN = """
    LEFT JOIN pacientes m ON m.id = n.madre_id
"""

_NEONATALES_SELECT = """
    p.datos_extra->'neonatales'->>'peso_nacimiento' AS neonatales_peso_nacimiento,
    p.datos_extra->'neonatales'->>'edad_gestacional' AS neonatales_edad_gestacional,
    p.datos_extra->'neonatales'->>'tipo_parto' AS neonatales_tipo_parto,
    p.datos_extra->'neonatales'->>'clase_parto' AS neonatales_clase_parto,
    p.datos_extra->'neonatales'->>'gemelo' AS neonatales_gemelo,
    p.datos_extra->'neonatales'->>'hora_nacimiento' AS neonatales_hora_nacimiento,
    p.datos_extra->'neonatales'->>'extrahositalario' AS neonatales_extrahospitalario
"""

_PACIENTE_SELECT = """
    p.id AS paciente_id_ref,
    p.expediente AS paciente_expediente,
    p.cui AS paciente_cui,
    p.nombre_completo AS paciente_nombre_completo,
    p.nombre->>'primer_nombre' AS paciente_nombre_primer_nombre,
    p.nombre->>'segundo_nombre' AS paciente_nombre_segundo_nombre,
    p.nombre->>'otro_nombre' AS paciente_nombre_otro_nombre,
    p.nombre->>'primer_apellido' AS paciente_nombre_primer_apellido,
    p.nombre->>'segundo_apellido' AS paciente_nombre_segundo_apellido,
    p.nombre->>'apellido_casada' AS paciente_nombre_apellido_casada,
    p.sexo AS paciente_sexo,
    p.fecha_nacimiento AS paciente_fecha_nacimiento,
    p.estado AS paciente_estado
"""

_MADRE_SELECT = """
    m.nombre_completo AS nombre_madre
"""


def _row_to_out(row: dict) -> dict:
    neonatales = {}
    for k in ("peso_nacimiento", "edad_gestacional", "tipo_parto", "clase_parto", "gemelo"):
        v = row.get(f"neonatales_{k}")
        if v is not None:
            neonatales[k] = v
    hora = row.get("neonatales_hora_nacimiento")
    if hora is not None:
        neonatales["hora_nacimiento"] = hora
    extra = row.get("neonatales_extrahospitalario")
    if extra is not None:
        neonatales["extrahospitalario"] = str(extra).lower() in ("true", "1", "yes")

    paciente = None
    if row.get("paciente_id_ref"):
        nombre = {
            k: row.get(f"paciente_nombre_{k}")
            for k in ("primer_nombre", "segundo_nombre", "otro_nombre",
                      "primer_apellido", "segundo_apellido", "apellido_casada")
        }
        nombre = {k: v for k, v in nombre.items() if v is not None} or None
        paciente = {
            "id": row["paciente_id_ref"],
            "expediente": row.get("paciente_expediente"),
            "cui": row.get("paciente_cui"),
            "nombre_completo": row.get("paciente_nombre_completo"),
            "nombre": nombre,
            "sexo": row.get("paciente_sexo"),
            "fecha_nacimiento": row.get("paciente_fecha_nacimiento"),
            "estado": row.get("paciente_estado"),
        }

    return {
        "id": row["id"],
        "paciente_id": row.get("paciente_id"),
        "madre_id": row.get("madre_id"),
        "registrador_id": row.get("registrador_id"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "peso_gramos": float(row["peso_gramos"]) if row.get("peso_gramos") is not None else None,
        "clasificacion_nacimiento": row.get("clasificacion_nacimiento"),
        "trabajo_parto": row.get("trabajo_parto"),
        "neonatales": neonatales or None,
        "paciente": paciente,
        "nombre_madre": row.get("nombre_madre"),
    }


def peso_lb_onz_a_gramos(peso: str | None) -> Decimal | None:
    if not peso:
        return None
    peso_clean = peso.strip().upper()
    lb = Decimal(0)
    onz = Decimal(0)

    m = re.match(r'^(\d+)\s*(?:LIBRAS|LB)\s+(\d+)\s*(?:ONZAS|ONZ)\s*$', peso_clean)
    if m:
        lb = Decimal(m.group(1))
        onz = Decimal(m.group(2))
    else:
        m = re.match(r'^(\d+)\s*(?:LIBRAS|LB)\s*$', peso_clean)
        if m:
            lb = Decimal(m.group(1))
        else:
            m = re.match(r'^(\d{1,3})\.(\d{1,2})$', peso_clean)
            if m:
                lb = Decimal(m.group(1))
                onz = Decimal(m.group(2))
            else:
                return None
    return ((lb + onz / Decimal("16")) / Decimal("2.2") * Decimal("1000")).quantize(Decimal("1"))


def clasificacion_nacimiento(pg: Decimal | None) -> str | None:
    if pg is None:
        return None
    if pg < 1000:
        return "EBP"
    if pg < 1500:
        return "MBP"
    if pg < 2500:
        return "BP"
    return "PN"


def trabajo_parto(eg: str | None) -> str | None:
    if not eg:
        return None
    try:
        semanas = Decimal(str(eg).strip())
    except Exception:
        return "no especificado"
    if semanas > 41:
        return "Prolongado"
    if semanas < 37:
        return "Prematuro"
    return "a Termino"


def _computar(neonatales: dict) -> dict:
    pg = peso_lb_onz_a_gramos(neonatales.get("peso_nacimiento"))
    return {
        "peso_gramos": pg,
        "clasificacion_nacimiento": clasificacion_nacimiento(pg),
        "trabajo_parto": trabajo_parto(neonatales.get("edad_gestacional")),
    }


def _recomputar_desde_origen(db: Session, nacimiento: NacimientoModel) -> bool:
    if not nacimiento.paciente_id:
        return False
    row = _fetchone(db, """
        SELECT datos_extra FROM pacientes WHERE id = :id
    """, {"id": nacimiento.paciente_id})
    if not row:
        return False
    de = row.get("datos_extra") or {}
    if isinstance(de, str):
        de = json.loads(de)
    neonatales = de.get("neonatales") or {}
    if not neonatales:
        return False
    computado = _computar(neonatales)
    cambios = False
    if computado["peso_gramos"] != nacimiento.peso_gramos:
        nacimiento.peso_gramos = computado["peso_gramos"]
        cambios = True
    if computado["clasificacion_nacimiento"] != nacimiento.clasificacion_nacimiento:
        nacimiento.clasificacion_nacimiento = computado["clasificacion_nacimiento"]
        cambios = True
    if computado["trabajo_parto"] != nacimiento.trabajo_parto:
        nacimiento.trabajo_parto = computado["trabajo_parto"]
        cambios = True
    if cambios:
        db.commit()
        db.refresh(nacimiento)
    return cambios


def _insert_nacimiento(db: Session, paciente_id: int, madre_id: int | None,
                       registrador_id: int | None, computado: dict) -> NacimientoModel:
    nacimiento = NacimientoModel(
        paciente_id=paciente_id,
        madre_id=madre_id,
        registrador_id=registrador_id,
        peso_gramos=computado["peso_gramos"],
        clasificacion_nacimiento=computado["clasificacion_nacimiento"],
        trabajo_parto=computado["trabajo_parto"],
    )
    db.add(nacimiento)
    db.commit()
    db.refresh(nacimiento)
    return nacimiento


def crear_nacimiento_desde_paciente(
    paciente_id: int,
    registrador_id: int | None,
    db: Session
) -> dict:
    row = _fetchone(db, """
        SELECT id, expediente, nombre_completo, sexo, fecha_nacimiento, datos_extra
        FROM pacientes WHERE id = :id
    """, {"id": paciente_id})
    if not row:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    de = row.get("datos_extra") or {}
    if isinstance(de, str):
        de = json.loads(de)
    neonatales = de.get("neonatales") or {}
    origen = de.get("origen") or {}

    if not neonatales:
        raise HTTPException(status_code=400, detail="El paciente no tiene datos neonatales")
    if origen.get("tipo") != "MADRE" or not origen.get("paciente_id"):
        raise HTTPException(status_code=400, detail="El paciente no fue registrado como hijo de una madre")

    madre_id = origen["paciente_id"]

    existente = _fetchone(db, "SELECT id FROM nacimientos WHERE paciente_id = :pid", {"pid": paciente_id})
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un registro de nacimiento para este paciente")

    computado = _computar(neonatales)
    nacimiento = _insert_nacimiento(db, paciente_id, madre_id, registrador_id, computado)

    return _row_to_out(_fetchone(db, f"""
        SELECT {_NACIMIENTO_COLS}, {_PACIENTE_SELECT}, {_NEONATALES_SELECT}, {_MADRE_SELECT}
        FROM nacimientos n
        {_PACIENTE_JOIN}
        {_MADRE_JOIN}
        WHERE n.id = :id
    """, {"id": nacimiento.id}))


def crear_nacimiento(data: NacimientoCreate, db: Session) -> dict:
    if not data.paciente_id:
        raise HTTPException(status_code=400, detail="paciente_id es requerido")

    existente = db.query(NacimientoModel).filter(
        NacimientoModel.paciente_id == data.paciente_id
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un registro de nacimiento para este paciente"
        )

    row = _fetchone(db, """
        SELECT id, datos_extra FROM pacientes WHERE id = :id
    """, {"id": data.paciente_id})
    if not row:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    de = row.get("datos_extra") or {}
    if isinstance(de, str):
        de = json.loads(de)
    neonatales = de.get("neonatales") or {}
    origen = de.get("origen") or {}
    madre_id = data.madre_id or origen.get("paciente_id")

    computado = _computar(neonatales)
    nacimiento = NacimientoModel(
        paciente_id=data.paciente_id,
        madre_id=madre_id,
        registrador_id=None,
        peso_gramos=computado["peso_gramos"],
        clasificacion_nacimiento=computado["clasificacion_nacimiento"],
        trabajo_parto=computado["trabajo_parto"],
    )
    db.add(nacimiento)
    db.commit()
    db.refresh(nacimiento)

    return _row_to_out(_fetchone(db, f"""
        SELECT {_NACIMIENTO_COLS}, {_PACIENTE_SELECT}, {_NEONATALES_SELECT}, {_MADRE_SELECT}
        FROM nacimientos n
        {_PACIENTE_JOIN}
        {_MADRE_JOIN}
        WHERE n.id = :id
    """, {"id": nacimiento.id}))


def listar_nacimientos(
    db: Session,
    q: Optional[str] = None,
    expediente: Optional[str] = None,
    sexo: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[dict], int]:
    where_clauses = []
    params: dict = {}

    if q:
        where_clauses.append("p.nombre_completo ILIKE :q")
        params["q"] = f"%{q}%"
    if expediente:
        where_clauses.append("p.expediente = :expediente")
        params["expediente"] = expediente
    if sexo:
        where_clauses.append("p.sexo = :sexo")
        params["sexo"] = sexo.upper()
    if fecha_desde:
        where_clauses.append("p.fecha_nacimiento >= :fecha_desde")
        params["fecha_desde"] = fecha_desde
    if fecha_hasta:
        where_clauses.append("p.fecha_nacimiento <= :fecha_hasta")
        params["fecha_hasta"] = fecha_hasta

    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

    count_sql = f"""
        SELECT COUNT(*) FROM nacimientos n
        {_PACIENTE_JOIN}
        {_MADRE_JOIN}
        WHERE {where_sql}
    """
    total = db.execute(text(count_sql), params).scalar()

    data_sql = f"""
        SELECT {_NACIMIENTO_COLS}, {_PACIENTE_SELECT}, {_NEONATALES_SELECT}, {_MADRE_SELECT}
        FROM nacimientos n
        {_PACIENTE_JOIN}
        {_MADRE_JOIN}
        WHERE {where_sql}
        ORDER BY n.id DESC
        LIMIT :limit OFFSET :skip
    """
    params["limit"] = limit
    params["skip"] = skip
    rows = db.execute(text(data_sql), params).mappings().all()

    return [_row_to_out(dict(r)) for r in rows], total


def obtener_nacimiento(nacimiento_id: int, db: Session) -> dict:
    nacimiento = db.query(NacimientoModel).filter(NacimientoModel.id == nacimiento_id).first()
    if not nacimiento:
        raise HTTPException(status_code=404, detail="Registro de nacimiento no encontrado")
    _recomputar_desde_origen(db, nacimiento)
    row = _fetchone(db, f"""
        SELECT {_NACIMIENTO_COLS}, {_PACIENTE_SELECT}, {_NEONATALES_SELECT}, {_MADRE_SELECT}
        FROM nacimientos n
        {_PACIENTE_JOIN}
        {_MADRE_JOIN}
        WHERE n.id = :id
    """, {"id": nacimiento_id})
    return _row_to_out(row)


def actualizar_nacimiento(
    nacimiento_id: int,
    data: NacimientoUpdate,
    db: Session
) -> dict:
    nacimiento = db.query(NacimientoModel).filter(NacimientoModel.id == nacimiento_id).first()
    if not nacimiento:
        raise HTTPException(status_code=404, detail="Registro de nacimiento no encontrado")

    if data.madre_id is not None:
        nacimiento.madre_id = data.madre_id

    _recomputar_desde_origen(db, nacimiento)

    return obtener_nacimiento(nacimiento_id, db)


def eliminar_nacimiento(nacimiento_id: int, db: Session) -> None:
    nacimiento = db.query(NacimientoModel).filter(NacimientoModel.id == nacimiento_id).first()
    if not nacimiento:
        raise HTTPException(status_code=404, detail="Registro de nacimiento no encontrado")
    try:
        db.delete(nacimiento)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar, está relacionado con otros registros"
        )
    return None


def sincronizar_nacimientos(
    db: Session,
    registrador_id: int | None = None
) -> dict:
    pacientes = _fetchall(db, """
        SELECT id FROM pacientes
        WHERE datos_extra->'neonatales' IS NOT NULL
          AND datos_extra->'origen'->>'tipo' = 'MADRE'
          AND id NOT IN (
            SELECT paciente_id FROM nacimientos WHERE paciente_id IS NOT NULL
          )
        ORDER BY id
    """)

    creados = 0
    errores = []
    for p in pacientes:
        try:
            crear_nacimiento_desde_paciente(p["id"], registrador_id, db)
            creados += 1
        except HTTPException as e:
            errores.append({"paciente_id": p["id"], "error": e.detail})

    importados = importar_desde_legacy(db, solo_con_madre=True, limit=5000, offset=0)

    return {
        "madre_hijo_creados": creados,
        "madre_hijo_errores": errores,
        "legacy_creados": importados["creados"],
        "legacy_saltados": importados["saltados"],
        "legacy_errores": importados["errores"],
    }


_TIPO_PARTO_MAP = {1: "EUTOCICO", 2: "DISTOCICO", 3: "CESAREA", 4: "OTRO"}
_CLASE_PARTO_MAP = {1: "UNICO", 2: "GEMELAR", 3: "TRIPLE", 4: "MULTIPLE"}


def _peso_legacy_a_str(lb: int | None, onz: int | None) -> str | None:
    if lb is None and onz is None:
        return None
    partes = []
    if lb:
        partes.append(f"{lb} lb")
    if onz:
        partes.append(f"{onz} onz")
    return " ".join(partes) if partes else None


def referenciar_legacy(
    db: Session,
    limit: int = 500,
    offset: int = 0,
    solo_sin_match: bool = False,
) -> dict:
    count_sql = "SELECT COUNT(*) FROM nacimientos_legacy"
    if solo_sin_match:
        count_sql += " WHERE expediente IS NOT NULL AND CAST(expediente AS VARCHAR) NOT IN (SELECT expediente FROM pacientes WHERE expediente IS NOT NULL AND expediente <> '')"
    total = db.execute(text(count_sql)).scalar()

    data_sql = "SELECT * FROM nacimientos_legacy ORDER BY id"
    if solo_sin_match:
        data_sql += " WHERE expediente IS NOT NULL AND CAST(expediente AS VARCHAR) NOT IN (SELECT expediente FROM pacientes WHERE expediente IS NOT NULL AND expediente <> '')"
    data_sql += f" LIMIT {limit} OFFSET {offset}"
    rows = db.execute(text(data_sql)).mappings().all()

    referencias: list[LegacyReferenceOut] = []
    coincidencias = 0
    con_nacimiento = 0
    sin_nacimiento = 0
    madres_sin_hijo = 0

    def buscar_hijo(madre_id: int, leg: dict) -> dict | None:
        hijos = _fetchall(db,
            """SELECT id, expediente, cui, nombre_completo, sexo, fecha_nacimiento, datos_extra
               FROM pacientes
               WHERE datos_extra @> :origen
               ORDER BY id""",
            {"origen": f'{{"origen": {{"paciente_id": {madre_id}, "tipo": "MADRE"}}}}'}
        )
        if not hijos:
            return None
        leg_fecha = leg.get("fecha_parto")
        leg_sexo = leg.get("sexo_rn")
        for h in hijos:
            if leg_sexo and leg_fecha:
                if h.get("sexo") == leg_sexo and str(h.get("fecha_nacimiento")) == str(leg_fecha):
                    return h
        return hijos[0] if hijos else None

    for leg in rows:
        madre = None
        match_tipo = "sin_match"
        leg_exp = leg.get("expediente")
        leg_dpi = leg.get("dpi")

        if leg_exp:
            madre = _fetchone(db,
                "SELECT id, expediente, nombre_completo FROM pacientes WHERE expediente = :exp",
                {"exp": str(leg_exp)}
            )

        if not madre and leg_dpi:
            madre = _fetchone(db,
                "SELECT id, expediente, nombre_completo FROM pacientes WHERE cui = :cui",
                {"cui": leg_dpi}
            )

        hijo = None
        if madre:
            hijo = buscar_hijo(madre["id"], leg)

        if not hijo:
            leg_madre = leg.get("madre")
            leg_fecha = leg.get("fecha_parto")
            leg_sexo = leg.get("sexo_rn")
            if leg_madre and leg_fecha and leg_sexo:
                candidatos = _fetchall(db,
                    """SELECT id, expediente, cui, nombre_completo, sexo, fecha_nacimiento, datos_extra
                       FROM pacientes
                       WHERE sexo = :sexo AND fecha_nacimiento = :fecha
                       ORDER BY id""",
                    {"sexo": leg_sexo, "fecha": str(leg_fecha)}
                )
                for c in candidatos:
                    de = c.get("datos_extra")
                    if de and isinstance(de, dict):
                        origen = de.get("origen", {})
                        if origen.get("tipo") == "MADRE" and origen.get("paciente_id"):
                            m = _fetchone(db,
                                "SELECT id, expediente, nombre_completo FROM pacientes WHERE id = :id",
                                {"id": origen["paciente_id"]}
                            )
                            if m and leg_madre.lower() in (m.get("nombre_completo", "") or "").lower():
                                hijo = c
                                madre = m
                                match_tipo = "por_madre_fecha_sexo"
                                break

        nacimiento_id = None
        if hijo:
            if not match_tipo or match_tipo == "sin_match":
                if madre and leg_exp and str(leg_exp) == madre.get("expediente"):
                    match_tipo = "por_expediente"
                elif madre and leg_dpi:
                    match_tipo = "por_dpi"
                else:
                    match_tipo = "por_madre_fecha_sexo"

            coincidencias += 1
            n = _fetchone(db,
                "SELECT id FROM nacimientos WHERE paciente_id = :pid",
                {"pid": hijo["id"]}
            )
            if n:
                nacimiento_id = n["id"]
                con_nacimiento += 1
            else:
                sin_nacimiento += 1

        if madre and not hijo:
            n_legacy = _fetchone(db,
                "SELECT id FROM nacimientos WHERE datos_extra->>'legacy_id' = :lid",
                {"lid": str(leg["id"])}
            )
            if n_legacy:
                con_nacimiento += 1
                nacimiento_id = n_legacy["id"]
            else:
                sin_nacimiento += 1

        if madre and not hijo:
            madres_sin_hijo += 1

        referencias.append(LegacyReferenceOut(
            legacy_id=leg["id"],
            legacy_doc=leg.get("doc"),
            legacy_madre=leg.get("madre"),
            legacy_fecha_parto=leg.get("fecha_parto"),
            legacy_sexo_rn=leg.get("sexo_rn"),
            legacy_expediente=leg.get("expediente"),
            legacy_lb=leg.get("lb"),
            legacy_onz=leg.get("onz"),
            legacy_hora=leg.get("hora"),
            legacy_tipo_parto=leg.get("tipo_parto"),
            legacy_clase_parto=leg.get("clase_parto"),
            legacy_medico=leg.get("medico"),
            match_tipo=match_tipo,
            madre_id=madre["id"] if madre else None,
            madre_expediente=madre.get("expediente") if madre else None,
            madre_nombre=madre.get("nombre_completo") if madre else None,
            paciente_id=hijo["id"] if hijo else None,
            paciente_expediente=hijo.get("expediente") if hijo else None,
            paciente_nombre=hijo.get("nombre_completo") if hijo else None,
            paciente_sexo=hijo.get("sexo") if hijo else None,
            paciente_fecha_nac=hijo.get("fecha_nacimiento") if hijo else None,
            nacimiento_id=nacimiento_id,
        ))

    sin_coincidencia = total - coincidencias

    return {
        "total_legacy": total,
        "coincidencias": coincidencias,
        "sin_coincidencia": sin_coincidencia,
        "madres_sin_hijo": madres_sin_hijo,
        "con_nacimiento": con_nacimiento,
        "sin_nacimiento": sin_nacimiento,
        "referencias": referencias,
    }


_TIPO_PARTO_MAP_STR = {1: "EUTOCICO", 2: "DISTOCICO", 3: "CESAREA", 4: "OTRO"}
_CLASE_PARTO_MAP_STR = {1: "UNICO", 2: "GEMELAR", 3: "TRIPLE", 4: "MULTIPLE"}


def _set_neonatales_en_paciente(db: Session, paciente_id: int, neonatales: dict):
    row = _fetchone(db, "SELECT datos_extra FROM pacientes WHERE id = :id FOR UPDATE", {"id": paciente_id})
    if not row:
        return
    de = row["datos_extra"]
    if isinstance(de, str):
        de = json.loads(de)
    if not isinstance(de, dict):
        de = {}
    de["neonatales"] = {**(de.get("neonatales") or {}), **neonatales}
    db.execute(
        text("UPDATE pacientes SET datos_extra = CAST(:de AS jsonb) WHERE id = :id"),
        {"de": json.dumps(de), "id": paciente_id}
    )


def importar_desde_legacy(
    db: Session,
    solo_con_madre: bool = True,
    limit: int = 500,
    offset: int = 0,
) -> dict:
    where = ""
    if solo_con_madre:
        where = " WHERE expediente IS NOT NULL AND CAST(expediente AS VARCHAR) IN (SELECT expediente FROM pacientes WHERE expediente IS NOT NULL AND expediente <> '')"

    count_sql = f"SELECT COUNT(*) FROM nacimientos_legacy{where}"
    total = db.execute(text(count_sql)).scalar()

    data_sql = f"SELECT * FROM nacimientos_legacy{where} ORDER BY id LIMIT {limit} OFFSET {offset}"
    rows = db.execute(text(data_sql)).mappings().all()

    creados = 0
    saltados = 0
    errores = []

    for leg in rows:
        try:
            leg_id = leg["id"]
            leg_exp = leg.get("expediente")
            leg_dpi = leg.get("dpi")

            ya_existe = _fetchone(db,
                "SELECT id FROM nacimientos WHERE datos_extra->>'legacy_id' = :lid",
                {"lid": str(leg_id)}
            )
            if ya_existe:
                saltados += 1
                continue

            madre = None
            if leg_exp:
                madre = _fetchone(db,
                    "SELECT id FROM pacientes WHERE expediente = :exp",
                    {"exp": str(leg_exp)}
                )
            if not madre and leg_dpi:
                madre = _fetchone(db,
                    "SELECT id FROM pacientes WHERE cui = :cui",
                    {"cui": leg_dpi}
                )

            madre_id = madre["id"] if madre else None
            leg_fecha = leg.get("fecha_parto")
            leg_sexo = leg.get("sexo_rn")

            hijo = None
            if madre_id and leg_fecha and leg_sexo:
                hijos = _fetchall(db,
                    """SELECT id, sexo, fecha_nacimiento, datos_extra
                       FROM pacientes
                       WHERE datos_extra @> :origen""",
                    {"origen": f'{{"origen": {{"paciente_id": {madre_id}, "tipo": "MADRE"}}}}'}
                )
                for h in hijos:
                    if h["sexo"] == leg_sexo and str(h["fecha_nacimiento"]) == str(leg_fecha):
                        hijo = h
                        break

            tipo_parto_str = _TIPO_PARTO_MAP_STR.get(leg.get("tipo_parto"))
            clase_parto_str = _CLASE_PARTO_MAP_STR.get(leg.get("clase_parto"))
            peso_str = _peso_legacy_a_str(leg.get("lb"), leg.get("onz"))

            neonatales = {}
            if peso_str:
                neonatales["peso_nacimiento"] = peso_str
            if tipo_parto_str:
                neonatales["tipo_parto"] = tipo_parto_str
            if clase_parto_str:
                neonatales["clase_parto"] = clase_parto_str
            hora = leg.get("hora")
            if hora:
                neonatales["hora_nacimiento"] = str(hora)

            extra = {"legacy_id": leg_id, "legacy_doc": leg.get("doc"), "legacy_madre": leg.get("madre")}

            computado = _computar(neonatales)

            if hijo:
                _set_neonatales_en_paciente(db, hijo["id"], neonatales)
                db.commit()

            db.execute(text("""
                INSERT INTO nacimientos
                    (paciente_id, madre_id, registrador_id, peso_gramos, clasificacion_nacimiento, trabajo_parto)
                VALUES
                    (:pid, :mid, NULL, :pg, :clasif, :tp)
            """), {
                "pid": hijo["id"] if hijo else None,
                "mid": madre_id,
                "pg": computado["peso_gramos"],
                "clasif": computado["clasificacion_nacimiento"],
                "tp": computado["trabajo_parto"],
            })
            db.commit()
            creados += 1

        except Exception as e:
            db.rollback()
            errores.append({"legacy_id": leg.get("id"), "error": str(e)})

    return {
        "total_legacy": total,
        "creados": creados,
        "saltados": saltados,
        "errores": errores,
    }
