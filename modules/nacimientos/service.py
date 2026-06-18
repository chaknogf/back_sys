import json
from datetime import date
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


def crear_nacimiento_desde_paciente(
    paciente_id: int,
    registrador_id: int | None,
    db: Session
) -> dict:
    paciente = _fetchone(db, "SELECT id, expediente, nombre_completo, sexo, fecha_nacimiento, datos_extra FROM pacientes WHERE id = :id", {"id": paciente_id})
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    de = paciente.get("datos_extra") or {}
    if isinstance(de, str):
        de = json.loads(de)
    neonatales = de.get("neonatales") or {}
    origen = de.get("origen") or {}

    if not neonatales:
        raise HTTPException(status_code=400, detail="El paciente no tiene datos neonatales")
    if origen.get("tipo") != "MADRE" or not origen.get("paciente_id"):
        raise HTTPException(status_code=400, detail="El paciente no fue registrado como hijo de una madre")

    madre_id = origen["paciente_id"]
    madre = _fetchone(db, "SELECT nombre_completo FROM pacientes WHERE id = :id", {"id": madre_id})
    madre_nombre = madre["nombre_completo"] if madre else "DESCONOCIDO"

    existente = _fetchone(db, "SELECT id FROM nacimientos WHERE paciente_id = :pid", {"pid": paciente_id})
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un registro de nacimiento para este paciente")

    extra = {"origen": origen}
    if paciente.get("datos_extra") and isinstance(paciente["datos_extra"], dict):
        extra["idpersona_madre"] = paciente["datos_extra"].get("idpersona_madre")

    db.execute(text("""
        INSERT INTO nacimientos
            (paciente_id, madre_id, expediente, nombre_completo, sexo, fecha_nacimiento,
             peso_nacimiento, edad_gestacional, tipo_parto, clase_parto, gemelo,
             hora_nacimiento, extrahospitalario, registrador_id, datos_extra)
        VALUES
            (:pid, :mid, :exp, :nom, :sexo, :fecha,
             :peso, :eg, :tp, :cl, :gem,
             :hora, :extrahop, :rid, CAST(:extra AS jsonb))
    """), {
        "pid": paciente_id,
        "mid": madre_id,
        "exp": paciente.get("expediente") or None,
        "nom": paciente.get("nombre_completo") or f"Hijo/a de {madre_nombre}",
        "sexo": paciente.get("sexo"),
        "fecha": str(paciente.get("fecha_nacimiento")) if paciente.get("fecha_nacimiento") else None,
        "peso": neonatales.get("peso_nacimiento"),
        "eg": neonatales.get("edad_gestacional"),
        "tp": neonatales.get("tipo_parto"),
        "cl": neonatales.get("clase_parto"),
        "gem": neonatales.get("gemelo"),
        "hora": str(neonatales.get("hora_nacimiento")) if neonatales.get("hora_nacimiento") else None,
        "extrahop": neonatales.get("extrahositalario", False),
        "rid": registrador_id,
        "extra": json.dumps(extra),
    })
    db.commit()
    nacimiento = _fetchone(db, "SELECT * FROM nacimientos WHERE paciente_id = :pid", {"pid": paciente_id})
    return nacimiento


def crear_nacimiento(data: NacimientoCreate, db: Session) -> NacimientoModel:
    existente = db.query(NacimientoModel).filter(
        NacimientoModel.paciente_id == data.paciente_id
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un registro de nacimiento para este paciente"
        )
    nacimiento = NacimientoModel(**data.model_dump())
    db.add(nacimiento)
    db.commit()
    db.refresh(nacimiento)
    return nacimiento


def listar_nacimientos(
    db: Session,
    q: Optional[str] = None,
    expediente: Optional[str] = None,
    sexo: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[NacimientoModel], int]:
    query = db.query(NacimientoModel)

    if q:
        query = query.filter(
            NacimientoModel.nombre_completo.ilike(f"%{q}%")
        )
    if expediente:
        query = query.filter(NacimientoModel.expediente == expediente)
    if sexo:
        query = query.filter(NacimientoModel.sexo == sexo.upper())
    if fecha_desde:
        query = query.filter(NacimientoModel.fecha_nacimiento >= fecha_desde)
    if fecha_hasta:
        query = query.filter(NacimientoModel.fecha_nacimiento <= fecha_hasta)

    total = query.count()
    nacimientos = query.order_by(desc(NacimientoModel.id)).offset(skip).limit(limit).all()
    return nacimientos, total


def obtener_nacimiento(nacimiento_id: int, db: Session) -> NacimientoModel:
    nacimiento = db.query(NacimientoModel).filter(NacimientoModel.id == nacimiento_id).first()
    if not nacimiento:
        raise HTTPException(status_code=404, detail="Registro de nacimiento no encontrado")
    return nacimiento


def actualizar_nacimiento(
    nacimiento_id: int,
    data: NacimientoUpdate,
    db: Session
) -> NacimientoModel:
    nacimiento = db.query(NacimientoModel).filter(NacimientoModel.id == nacimiento_id).first()
    if not nacimiento:
        raise HTTPException(status_code=404, detail="Registro de nacimiento no encontrado")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(nacimiento, key, value)
    db.commit()
    db.refresh(nacimiento)
    return nacimiento


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

        # 1) Find mother by expediente
        if leg_exp:
            madre = _fetchone(db,
                "SELECT id, expediente, nombre_completo FROM pacientes WHERE expediente = :exp",
                {"exp": str(leg_exp)}
            )

        # 2) Find mother by DPI
        if not madre and leg_dpi:
            madre = _fetchone(db,
                "SELECT id, expediente, nombre_completo FROM pacientes WHERE cui = :cui",
                {"cui": leg_dpi}
            )

        # 3) Find child directly (fallback: madre not found, search by sex+fecha+origen)
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

            extra = {"legacy_id": leg_id, "legacy_doc": leg.get("doc"), "legacy_madre": leg.get("madre")}

            db.execute(
                text("""
                    INSERT INTO nacimientos
                        (paciente_id, madre_id, expediente, nombre_completo, sexo, fecha_nacimiento,
                         peso_nacimiento, tipo_parto, clase_parto, hora_nacimiento, extrahospitalario,
                         registrador_id, datos_extra)
                    VALUES
                        (:pid, :mid, :exp, :nom, :sexo, :fecha,
                         :peso, :tipo, :clase, :hora, false,
                         NULL, CAST(:extra AS jsonb))
                """),
                {
                    "pid": hijo["id"] if hijo else None,
                    "mid": madre_id,
                    "exp": hijo.get("expediente") if hijo else None,
                    "nom": hijo.get("nombre_completo") if hijo else (f"Hijo/a de {leg.get('madre')}" if leg.get("madre") else "N.N."),
                    "sexo": leg_sexo,
                    "fecha": str(leg_fecha) if leg_fecha else None,
                    "peso": peso_str,
                    "tipo": tipo_parto_str,
                    "clase": clase_parto_str,
                    "hora": str(leg.get("hora")) if leg.get("hora") else None,
                    "extra": json.dumps(extra),
                }
            )
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
