import csv
import io
import re
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import text, or_
from sqlalchemy.orm import Session
from typing import List, Optional as Opt
from datetime import date, datetime

from modules.sigsa3.models import Sigsa3Model, Sigsa3RegistroModel
from modules.sigsa3.schemas import Sigsa3Create, Sigsa3Update, Sigsa3RegistroOut

# Mapeo de columnas Excel → campos SIGSA-3
EXCEL_COLUMN_MAP = {
    "personal salud": "personal_salud",
    "fecha de la consulta": "fecha_consulta",
    "no. historia clinica": "no_historia_clinica",
    "nombre del paciente": "nombre_paciente",
    "sexo": "sexo",
    "edad en dias": "edad_dias",
    "edad en meses": "edad_meses",
    "edad en anos": "edad_anios",
    "consulta nueva": "consulta_nueva",
    "consulta primera": "consulta_primera",
    "reconsulta": "reconsulta",
    "emergencia": "emergencia",
    "control": "control",
    "semana gestacional": "semana_gestacional",
    "codigo cie-10": "codigo_cie_10",
    "descripcion de diagnostico/control": "descripcion_diagnostico",
    "tipo consulta": "tipo_consulta",
    "especialidad": "especialidad",
    "paciente_id": "paciente_id",
    "consulta_id": "consulta_id",
}


def _normalizar_columna(col: str) -> str:
    """Normaliza nombre de columna para matching (minúsculas, sin acentos)."""
    import unicodedata
    col = col.strip().lower()
    # Eliminar acentos
    col = unicodedata.normalize('NFD', col)
    col = ''.join(c for c in col if unicodedata.category(c) != 'Mn')
    return col

MESES_ES = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}


def _parse_fecha_excel(fecha_str: str) -> Opt[date]:
    """Parsea fecha en formato 'dd-mmm' (22-jun) o 'DD/MM/YYYY' (1/01/2020)."""
    if not fecha_str:
        return None
    fecha_str = fecha_str.strip().lower()

    match_ymd = re.match(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$", fecha_str)
    if match_ymd:
        dia, mes, anio = int(match_ymd.group(1)), int(match_ymd.group(2)), int(match_ymd.group(3))
        if anio < 100:
            anio += 2000
        try:
            return date(anio, mes, dia)
        except ValueError:
            return None

    match_mmm = re.match(r"(\d{1,2})[-/](\w+)", fecha_str)
    if match_mmm:
        dia = int(match_mmm.group(1))
        mes_str = match_mmm.group(2)[:3]
        mes = MESES_ES.get(mes_str)
        if mes:
            anio = date.today().year
            try:
                return date(anio, mes, dia)
            except ValueError:
                return None

    return None


def _determinar_tipo_consulta(row: dict) -> str:
    """Determina tipo_consulta: columna 'Tipo Consulta' directa o columnas con 'X'."""
    tipo_directo = row.get("tipo_consulta")
    if tipo_directo and tipo_directo.strip():
        val = tipo_directo.strip()
        if val[0].isdigit():
            return val
        if val.upper() == "PRIMERA" or val.upper() == "NUEVA":
            return "1 Primera"
        if val.upper() == "RECONSULTA":
            return "2 Reconsulta"
        if val.upper() == "EMERGENCIA":
            return "3 Emergencia"
        return val
    if (row.get("consulta_nueva") or "").strip().upper() == "X":
        return "1 Primera"
    if (row.get("consulta_primera") or "").strip().upper() == "X":
        return "1 Primera"
    if (row.get("reconsulta") or "").strip().upper() == "X":
        return "2 Reconsulta"
    if (row.get("emergencia") or "").strip().upper() == "X":
        return "3 Emergencia"
    return "4 Interconsulta"


def _parse_int_safe(value: str) -> Opt[int]:
    """Convierte string a int de forma segura."""
    if not value:
        return None
    value = value.strip()
    if value in ("--", "", "N/A", "NA"):
        return None
    try:
        return int(value)
    except ValueError:
        return None


async def importar_excel_csv(file: UploadFile, db: Session) -> dict:
    """Importa CSV exportado desde Excel con formato SIGSA-3."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo debe tener extensión .csv",
        )

    try:
        content = await file.read()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo leer el archivo",
        )

    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            csv_text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se pudo decodificar el archivo. Use UTF-8 o Latin-1",
        )

    if csv_text.startswith("\ufeff"):
        csv_text = csv_text[1:]

    try:
        dialect = csv.Sniffer().sniff(csv_text[:8192])
    except csv.Error:
        dialect = csv.excel

    reader = csv.DictReader(io.StringIO(csv_text), dialect=dialect)

    if not reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo CSV está vacío o no tiene encabezados",
        )

    col_map = {}
    for col in reader.fieldnames:
        normalized = _normalizar_columna(col)
        if normalized in EXCEL_COLUMN_MAP:
            col_map[col] = EXCEL_COLUMN_MAP[normalized]

    ps_rows = db.execute(
        text("SELECT nombre, medico_id FROM personal_salud WHERE medico_id IS NOT NULL")
    ).fetchall()
    nombre_a_medico = {r[0].strip().lower(): r[1] for r in ps_rows}

    registros = []
    errores = []
    for i, row in enumerate(reader, start=2):
        try:
            mapped = {}
            for orig_col, target_field in col_map.items():
                val = row.get(orig_col, "").strip()
                if val in ("--", "", "N/A", "NA"):
                    val = None
                mapped[target_field] = val

            personal_salud = mapped.get("personal_salud")
            fecha_consulta = _parse_fecha_excel(mapped.get("fecha_consulta"))
            no_historia_clinica = mapped.get("no_historia_clinica")
            nombre_paciente = mapped.get("nombre_paciente")
            sexo = mapped.get("sexo")
            edad_dias = _parse_int_safe(mapped.get("edad_dias"))
            edad_meses = _parse_int_safe(mapped.get("edad_meses"))
            edad_anios = _parse_int_safe(mapped.get("edad_anios"))
            tipo_consulta = _determinar_tipo_consulta(mapped)
            control = mapped.get("control")
            semana_gestacional = _parse_int_safe(mapped.get("semana_gestacional"))
            codigo_cie_10 = mapped.get("codigo_cie_10")
            descripcion_diag = mapped.get("descripcion_diagnostico")
            especialidad = mapped.get("especialidad")
            paciente_id = _parse_int_safe(mapped.get("paciente_id"))
            consulta_id = _parse_int_safe(mapped.get("consulta_id"))

            medico_id = nombre_a_medico.get(personal_salud.strip().lower()) if personal_salud else None

            dx = None
            if codigo_cie_10 and descripcion_diag:
                dx = f"{codigo_cie_10} {descripcion_diag}"
            elif descripcion_diag:
                dx = descripcion_diag

            registro = Sigsa3Create(
                personal_salud=personal_salud,
                fecha_consulta=fecha_consulta,
                no_historia_clinica=no_historia_clinica,
                nombre_paciente=nombre_paciente,
                sexo=sexo,
                edad_dias=edad_dias,
                edad_meses=edad_meses,
                edad_anios=edad_anios,
                tipo_consulta=tipo_consulta,
                control=control,
                semana_gestacional=semana_gestacional,
                codigo_cie_10=codigo_cie_10,
                dx=dx,
                especialidad=especialidad,
                paciente_id=paciente_id,
                medico_id=medico_id,
                consulta_id=consulta_id,
            )
            registros.append(registro)
        except Exception as e:
            errores.append({"fila": i, "error": str(e)})

    if not registros:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se encontraron registros válidos en el archivo",
        )

    existing_pacientes = set()
    existing_consultas = set()

    ids_paciente = {r.paciente_id for r in registros if r.paciente_id is not None}
    ids_consulta = {r.consulta_id for r in registros if r.consulta_id is not None}

    if ids_paciente:
        rows = db.execute(text("SELECT id FROM pacientes WHERE id = ANY(:ids)"), {"ids": list(ids_paciente)}).fetchall()
        existing_pacientes = {r[0] for r in rows}
    if ids_consulta:
        rows = db.execute(text("SELECT id FROM consultas WHERE id = ANY(:ids)"), {"ids": list(ids_consulta)}).fetchall()
        existing_consultas = {r[0] for r in rows}
    for r in registros:
        if r.paciente_id is not None and r.paciente_id not in existing_pacientes:
            r.paciente_id = None
        if r.consulta_id is not None and r.consulta_id not in existing_consultas:
            r.consulta_id = None

    try:
        objs = [Sigsa3Model(**r.model_dump()) for r in registros]
        db.add_all(objs)
        db.commit()
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        import logging
        logging.error(f"Error insertando registros SIGSA-3: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al insertar los registros en la base de datos: {error_msg}",
        )

    return {"insertados": len(registros), "errores": errores}




def listar_registros(
    db: Session,
    personal_salud: Opt[str] = None,
    fecha_consulta: Opt[date] = None,
    no_historia_clinica: Opt[str] = None,
    nombre_paciente: Opt[str] = None,
    sexo: Opt[str] = None,
    tipo_consulta: Opt[str] = None,
    especialidad: Opt[str] = None,
    especialidad_id: Opt[int] = None,
    codigo_cie_10: Opt[str] = None,
    q: Opt[str] = None,
    limit: int = 100,
) -> List[Sigsa3Model]:
    query = db.query(Sigsa3Model)

    if personal_salud:
        query = query.filter(Sigsa3Model.personal_salud.ilike(f"%{personal_salud}%"))
    if fecha_consulta:
        query = query.filter(Sigsa3Model.fecha_consulta == fecha_consulta)
    if no_historia_clinica:
        query = query.filter(Sigsa3Model.no_historia_clinica.ilike(f"%{no_historia_clinica}%"))
    if nombre_paciente:
        query = query.filter(Sigsa3Model.nombre_paciente.ilike(f"%{nombre_paciente}%"))
    if sexo:
        query = query.filter(Sigsa3Model.sexo == sexo)
    if tipo_consulta:
        query = query.filter(Sigsa3Model.tipo_consulta.ilike(f"%{tipo_consulta}%"))
    if especialidad:
        query = query.filter(Sigsa3Model.especialidad.ilike(f"%{especialidad}%"))
    if especialidad_id is not None:
        query = query.filter(Sigsa3Model.especialidad_id == especialidad_id)
    if codigo_cie_10:
        query = query.filter(Sigsa3Model.codigo_cie_10.ilike(f"%{codigo_cie_10}%"))
    if q:
        query = query.filter(
            or_(
                Sigsa3Model.nombre_paciente.ilike(f"%{q}%"),
                Sigsa3Model.no_historia_clinica.ilike(f"%{q}%"),
                Sigsa3Model.dx.ilike(f"%{q}%"),
                Sigsa3Model.personal_salud.ilike(f"%{q}%"),
            )
        )

    limit = min(limit, 500)
    return query.order_by(Sigsa3Model.fecha_consulta.desc(), Sigsa3Model.id.desc()).limit(limit).all()


def obtener_registro(registro_id: int, db: Session) -> Sigsa3Model:
    registro = db.query(Sigsa3Model).filter(Sigsa3Model.id == registro_id).first()
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro SIGSA-3 no encontrado"
        )
    return registro


def crear_registro(data: Sigsa3Create, db: Session) -> Sigsa3Model:
    registro = Sigsa3Model(**data.model_dump())
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


def actualizar_registro(registro_id: int, data: Sigsa3Update, db: Session) -> Sigsa3Model:
    registro = db.query(Sigsa3Model).filter(Sigsa3Model.id == registro_id).first()
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro SIGSA-3 no encontrado"
        )
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(registro, key, value)
    db.commit()
    db.refresh(registro)
    return registro


def eliminar_registro(registro_id: int, db: Session) -> None:
    registro = db.query(Sigsa3Model).filter(Sigsa3Model.id == registro_id).first()
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro SIGSA-3 no encontrado"
        )
    try:
        db.delete(registro)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el registro, está relacionado con otros datos"
        )


def eliminar_por_ids(ids: List[int], db: Session) -> dict:
    if not ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La lista de IDs no puede estar vacía"
        )
    registros = db.query(Sigsa3Model).filter(Sigsa3Model.id.in_(ids)).all()
    if not registros:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron registros con los IDs proporcionados"
        )
    try:
        eliminados = len(registros)
        for reg in registros:
            db.delete(reg)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al eliminar los registros"
        )
    return {"eliminados": eliminados}


def eliminar_por_periodo(desde: date, hasta: date, db: Session) -> dict:
    if desde > hasta:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha 'desde' debe ser menor o igual a 'hasta'"
        )
    registros = db.query(Sigsa3Model).filter(
        Sigsa3Model.fecha_consulta >= desde,
        Sigsa3Model.fecha_consulta <= hasta,
    ).all()
    if not registros:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron registros en el periodo {desde} al {hasta}"
        )
    try:
        eliminados = len(registros)
        for reg in registros:
            db.delete(reg)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al eliminar los registros"
        )
    return {"eliminados": eliminados, "desde": desde.isoformat(), "hasta": hasta.isoformat()}


def sincronizar_sigsa3(db: Session) -> dict:
    """Paso 1: asocia medico_id en SIGSA-3 por nombre (personal_salud → personal_salud.medico_id).
    Paso 2: actualiza especialidad + especialidad_id en SIGSA-3 desde medicos."""
    from modules.personal_salud.models import PersonalSaludModel

    registros = db.query(Sigsa3Model).filter(
        Sigsa3Model.personal_salud.isnot(None),
    ).all()
    if not registros:
        return {"asociados": 0, "especialidades_actualizadas": 0}

    personal = db.query(PersonalSaludModel).filter(
        PersonalSaludModel.medico_id.isnot(None)
    ).all()
    nombre_to_medico = {p.nombre.strip().lower(): (p.medico_id, p.nombre, p.especialidad_id) for p in personal}

    medico_ids = set()
    asociados = 0
    for reg in registros:
        nombre = reg.personal_salud.strip().lower() if reg.personal_salud else ""
        if not nombre:
            continue
        match = nombre_to_medico.get(nombre)
        if not match:
            for ps_nombre, (ps_mid, ps_name, ps_esp_id) in nombre_to_medico.items():
                if ps_nombre in nombre or nombre in ps_nombre:
                    match = (ps_mid, ps_name, ps_esp_id)
                    break
        if match:
            medico_id, _, personal_esp_id = match
            if reg.medico_id != medico_id:
                reg.medico_id = medico_id
                asociados += 1
            if personal_esp_id and reg.especialidad_id != personal_esp_id:
                reg.especialidad_id = personal_esp_id
            medico_ids.add(medico_id)

    db.commit()
    return {
        "asociados": asociados,
        "especialidades_actualizadas": asociados,
    }


def asociar_paciente_y_consulta(db: Session):
    """Pipeline completo usando pandas para asociación masiva.
    Generador que yield eventos de progreso como dicts.
    1. nombre_paciente = nombre_completo AND no_historia_clinica = expediente → paciente_id
    2. no_historia_clinica = expediente (tipo 1/2) o = documento + fecha (tipo 3) → paciente_id / consulta_id
    3. nombre_paciente vs nombre_completo: trigram similarity >0.3 o ILIKE bidireccional ≥4 chars → paciente_id
    4. paciente_id + fecha ±1d + tipo coincidente → consulta_id
    5. no_historia_clinica = documento + fecha ±1d → consulta_id (+ paciente_id si faltaba)
    6a. paciente_id + fecha ±1d (cualquier tipo) → consulta_id (rezagados)
    6b. nombre_paciente vs nombre_completo: trigram similarity >0.2 → paciente_id (rezagados)
    """
    import pandas as pd
    from datetime import datetime
    from sqlalchemy import text

    ahora = datetime.now
    t0 = ahora()

    resultados = {k: 0 for k in (
        "paso1_paciente", "paso2_paciente", "paso2_consulta", "paso3_paciente",
        "paso4_consulta", "paso5_consulta", "paso5_paciente",
        "paso6a_consulta", "paso6b_paciente",
    )}
    yield {"step": "load", "message": "Iniciando asociación...", "progress": 0, **resultados}

    # ── Cargar datos con pd.read_sql (40-60% más rápido que ORM) ──
    from core.database import engine

    df = pd.read_sql(
        "SELECT id, nombre_paciente, no_historia_clinica, fecha_consulta, tipo_consulta, paciente_id, consulta_id FROM sigsa3 WHERE paciente_id IS NULL OR consulta_id IS NULL",
        engine, parse_dates=["fecha_consulta"]
    )
    print(f"[PIPELINE] registros cargados={len(df)}")
    if df.empty:
        yield {"step": "done", "message": "Sin registros SIGSA-3 pendientes", "progress": 100, **resultados}
        return

    yield {
        "step": "data_loaded", "progress": 5,
        "message": f"{len(df)} registros SIGSA-3 pendientes",
        **resultados,
    }

    # Cargar pacientes y consultas para pasos basados en pandas (4, 5, 6a)
    df_pac = pd.read_sql(
        "SELECT id AS pac_id, nombre_completo, expediente FROM pacientes WHERE nombre_completo IS NOT NULL",
        engine
    )
    df_con = pd.read_sql(
        "SELECT id AS con_id, paciente_id, fecha_consulta, tipo_consulta, documento FROM consultas",
        engine, parse_dates=["fecha_consulta"]
    )

    updates_paciente = {}
    updates_consulta = {}

    def _aplicar_updates():
        if updates_paciente:
            params = [{"pid": int(v), "rid": int(k)} for k, v in updates_paciente.items()]
            db.execute(text("UPDATE sigsa3 SET paciente_id = :pid WHERE id = :rid"), params)
        if updates_consulta:
            params = [{"cid": int(v), "rid": int(k)} for k, v in updates_consulta.items()]
            db.execute(text("UPDATE sigsa3 SET consulta_id = :cid WHERE id = :rid"), params)
        db.commit()
        updates_paciente.clear()
        updates_consulta.clear()

    # ── PASO 1: nombre_paciente = nombre_completo AND no_historia_clinica = expediente ──
    rows = db.execute(text("""
        SELECT s.id, p.id AS pac_id
        FROM sigsa3 s
        JOIN pacientes p ON unaccent(s.nombre_paciente) = unaccent(p.nombre_completo)
          AND s.no_historia_clinica = p.expediente
        WHERE s.paciente_id IS NULL
          AND s.nombre_paciente IS NOT NULL
          AND s.no_historia_clinica IS NOT NULL
    """)).fetchall()
    for sigsa3_id, pac_id in rows:
        updates_paciente[int(sigsa3_id)] = int(pac_id)
        resultados["paso1_paciente"] += 1
    _aplicar_updates()
    yield {"step": "paso1", "progress": 20, "message": f"Paso 1 — nombre exacto + expediente: {resultados['paso1_paciente']} pacientes", **resultados}

    # ── PASO 2: no_historia_clinica = expediente (cualquier tipo) o documento (tipo 3) ──
    # 2a: match contra pacientes.expediente (todos los tipos, incluido 3)
    rows = db.execute(text("""
        SELECT s.id, p.id AS pac_id
        FROM sigsa3 s
        JOIN pacientes p ON s.no_historia_clinica = p.expediente
        WHERE s.paciente_id IS NULL
          AND s.no_historia_clinica IS NOT NULL
    """)).fetchall()
    for sigsa3_id, pac_id in rows:
        updates_paciente[int(sigsa3_id)] = int(pac_id)
        resultados["paso2_paciente"] += 1

    # 2b: tipo = 3 → match contra consultas.documento + fecha
    rows = db.execute(text("""
        SELECT s.id, c.id AS con_id, c.paciente_id
        FROM sigsa3 s
        JOIN consultas c ON s.no_historia_clinica = c.documento
          AND s.fecha_consulta = c.fecha_consulta
        WHERE s.paciente_id IS NULL
          AND s.no_historia_clinica IS NOT NULL
          AND s.tipo_consulta ~ '^3'
    """)).fetchall()
    for sigsa3_id, con_id, pac_id in rows:
        cid = int(con_id)
        pid = int(pac_id)
        updates_consulta[int(sigsa3_id)] = cid
        updates_paciente[int(sigsa3_id)] = pid
        resultados["paso2_consulta"] += 1
    yield {"step": "paso2", "progress": 40, "message": f"Paso 2 — expediente/doc: {resultados['paso2_paciente']} pacientes, {resultados['paso2_consulta']} consultas", **resultados}

    # Commit parcial: paso 2 escrito en DB + refrescar df
    _aplicar_updates()
    df = pd.read_sql(
        "SELECT id, nombre_paciente, no_historia_clinica, fecha_consulta, tipo_consulta, paciente_id, consulta_id FROM sigsa3 WHERE paciente_id IS NULL OR consulta_id IS NULL",
        engine, parse_dates=["fecha_consulta"]
    )

    # ── PASO 3a: last-2-words key JOIN + trigram similarity > 0.3 ──
    mask = df["paciente_id"].isna() & df["nombre_paciente"].notna()
    if mask.any():
        paso3a = pd.read_sql(text("""\
            SELECT DISTINCT ON (s.id) s.id, p.id AS pac_id
            FROM (
                SELECT id, nombre_paciente,
                       CASE WHEN unaccent(nombre_paciente) LIKE '% % %'
                           THEN SUBSTRING(unaccent(nombre_paciente) FROM '\\S+\\s+(\\S+\\s+\\S+)$')
                           ELSE SUBSTRING(unaccent(nombre_paciente) FROM '(\\S+)$')
                       END AS key
                FROM sigsa3
                WHERE paciente_id IS NULL AND nombre_paciente IS NOT NULL AND nombre_paciente <> ''
            ) s
            JOIN (
                SELECT id, nombre_completo,
                       CASE WHEN unaccent(nombre_completo) LIKE '% % %'
                           THEN SUBSTRING(unaccent(nombre_completo) FROM '\\S+\\s+(\\S+\\s+\\S+)$')
                           ELSE SUBSTRING(unaccent(nombre_completo) FROM '(\\S+)$')
                       END AS key
                FROM pacientes
                WHERE nombre_completo IS NOT NULL AND nombre_completo <> ''
            ) p ON s.key = p.key
              AND similarity(unaccent(s.nombre_paciente), unaccent(p.nombre_completo)) > 0.3
            ORDER BY s.id,
              similarity(unaccent(s.nombre_paciente), unaccent(p.nombre_completo)) DESC
        """), engine)
        for _, row in paso3a.iterrows():
            rid = int(row["id"])
            pid = int(row["pac_id"])
            updates_paciente[rid] = pid
            df.loc[df["id"] == rid, "paciente_id"] = pid
            resultados["paso3_paciente"] += 1

    # Commit paso 3a
    _aplicar_updates()

    # ── PASO 3b: last-word key JOIN + trigram similarity > 0.3 (SQL, leftovers) ──
    mask = df["paciente_id"].isna() & df["nombre_paciente"].notna()
    if mask.any():
        paso3b = pd.read_sql(text("""\
            WITH sig AS MATERIALIZED (
                SELECT id, nombre_paciente,
                       SUBSTRING(unaccent(nombre_paciente) FROM '(\\S+)$') AS key1
                FROM sigsa3
                WHERE paciente_id IS NULL AND nombre_paciente IS NOT NULL AND nombre_paciente <> ''
            ),
            pac AS MATERIALIZED (
                SELECT id, nombre_completo,
                       SUBSTRING(unaccent(nombre_completo) FROM '(\\S+)$') AS key1
                FROM pacientes
                WHERE nombre_completo IS NOT NULL AND nombre_completo <> ''
            )
            SELECT DISTINCT ON (s.id) s.id, p.id AS pac_id
            FROM sig s
            JOIN pac p ON s.key1 = p.key1
              AND similarity(unaccent(s.nombre_paciente), unaccent(p.nombre_completo)) > 0.3
            ORDER BY s.id,
              similarity(unaccent(s.nombre_paciente), unaccent(p.nombre_completo)) DESC
        """), engine)
        for _, row in paso3b.iterrows():
            rid = int(row["id"])
            pid = int(row["pac_id"])
            updates_paciente[rid] = pid
            df.loc[df["id"] == rid, "paciente_id"] = pid
            resultados["paso3_paciente"] += 1

    # Commit paso 3
    _aplicar_updates()
    yield {"step": "paso3", "progress": 55, "message": f"Paso 3 — clave (apellidos) + trigram: {resultados['paso3_paciente']} pacientes", **resultados}

    # ── PASO 4: consulta_id por paciente_id + fecha_consulta ±1d + tipo_consulta ──
    mask = df["consulta_id"].isna() & df["paciente_id"].notna() & df["fecha_consulta"].notna()
    if mask.any() and not df_con.empty:
        sub = df.loc[mask, ["id", "paciente_id", "fecha_consulta", "tipo_consulta"]].copy()
        sub["tipo_num"] = pd.to_numeric(
            sub["tipo_consulta"].astype(str).str.strip().str.split(n=1).str[0],
            errors="coerce"
        )
        sub_exp = pd.concat([
            sub.assign(_match_date=sub["fecha_consulta"] - pd.Timedelta(days=1), _dist=1),
            sub.assign(_match_date=sub["fecha_consulta"], _dist=0),
            sub.assign(_match_date=sub["fecha_consulta"] + pd.Timedelta(days=1), _dist=1),
        ])

        df_con = df_con.copy()
        df_con["tipo_num"] = df_con["tipo_consulta"]

        merged = sub_exp.merge(df_con, left_on=["paciente_id", "_match_date"],
                               right_on=["paciente_id", "fecha_consulta"],
                               how="inner", suffixes=("_sig", "_con"))
        merged = merged[
            merged["tipo_num_sig"].isna() | (merged["tipo_num_sig"] == merged["tipo_num_con"])
        ]
        # Best match per sigsa3: exact date (_dist=0) preferred over ±1
        merged = merged.loc[merged.groupby("id")["_dist"].idxmin()]
        merged = merged.drop_duplicates(subset="id", keep="first")

        for _, row in merged.iterrows():
            rid = row["id"]
            updates_consulta[rid] = int(row["con_id"])
            df.loc[df["id"] == rid, "consulta_id"] = row["con_id"]
            resultados["paso4_consulta"] += 1
    yield {"step": "paso4", "progress": 70, "message": f"Paso 4 — paciente+fecha±1d+tipo: {resultados['paso4_consulta']} consultas", **resultados}

    # ── PASO 5: consulta_id por no_historia_clinica = documento + fecha_consulta ±1d ──
    mask = df["consulta_id"].isna() & df["no_historia_clinica"].notna() & df["fecha_consulta"].notna()
    if mask.any() and not df_con.empty:
        sub = df.loc[mask, ["id", "no_historia_clinica", "fecha_consulta", "paciente_id"]].copy()
        sub_exp = pd.concat([
            sub.assign(_match_date=sub["fecha_consulta"] - pd.Timedelta(days=1), _dist=1),
            sub.assign(_match_date=sub["fecha_consulta"], _dist=0),
            sub.assign(_match_date=sub["fecha_consulta"] + pd.Timedelta(days=1), _dist=1),
        ])
        merged = sub_exp.merge(df_con, left_on=["no_historia_clinica", "_match_date"],
                               right_on=["documento", "fecha_consulta"],
                               how="inner", suffixes=("_sig", "_con"))
        # Best match per sigsa3: exact date preferred
        merged = merged.loc[merged.groupby("id")["_dist"].idxmin()]
        merged = merged.drop_duplicates(subset="id", keep="first")
        for _, row in merged.iterrows():
            rid = row["id"]
            updates_consulta[rid] = int(row["con_id"])
            df.loc[df["id"] == rid, "consulta_id"] = row["con_id"]
            resultados["paso5_consulta"] += 1
            if pd.isna(row["paciente_id_sig"]):
                updates_paciente[rid] = int(row["paciente_id_con"])
                df.loc[df["id"] == rid, "paciente_id"] = row["paciente_id_con"]
                resultados["paso5_paciente"] += 1
    yield {"step": "paso5", "progress": 85, "message": f"Paso 5 — documento+fecha±1d: {resultados['paso5_consulta']} consultas, {resultados['paso5_paciente']} pacientes adicionales", **resultados}

    # Commit parcial: pasos 3-5 escritos en DB para que paso 6 vea estado actualizado
    _aplicar_updates()

    # ── PASO 6: barrido final para rezagados ──
    # 6a: paciente_id sin consulta_id → buscar por paciente_id + fecha ±1d (cualquier tipo)
    mask = df["consulta_id"].isna() & df["paciente_id"].notna() & df["fecha_consulta"].notna()
    if mask.any() and not df_con.empty:
        sub = df.loc[mask, ["id", "paciente_id", "fecha_consulta"]].copy()
        sub_exp = pd.concat([
            sub.assign(_match_date=sub["fecha_consulta"] - pd.Timedelta(days=1), _dist=1),
            sub.assign(_match_date=sub["fecha_consulta"], _dist=0),
            sub.assign(_match_date=sub["fecha_consulta"] + pd.Timedelta(days=1), _dist=1),
        ])
        merged = sub_exp.merge(df_con, left_on=["paciente_id", "_match_date"],
                               right_on=["paciente_id", "fecha_consulta"],
                               how="inner", suffixes=("_sig", "_con"))
        if not merged.empty:
            merged = merged.loc[merged.groupby("id")["_dist"].idxmin()]
            merged = merged.drop_duplicates(subset="id", keep="first")
        for _, row in merged.iterrows():
            rid = row["id"]
            updates_consulta[rid] = int(row["con_id"])
            df.loc[df["id"] == rid, "consulta_id"] = row["con_id"]
            resultados["paso6a_consulta"] += 1
    yield {"step": "paso6a", "progress": 90, "message": f"Paso 6a — paciente+fecha±1d (cualquier tipo): {resultados['paso6a_consulta']} consultas", **resultados}

    # 6b: sin paciente_id → key JOIN + trigram similarity > 0.2 (rezagados)
    mask = df["paciente_id"].isna() & df["nombre_paciente"].notna()
    if mask.any():
        paso6b = pd.read_sql(text("""\
            SELECT DISTINCT ON (s.id) s.id, p.id AS pac_id
            FROM (
                SELECT id, nombre_paciente,
                       CASE WHEN unaccent(nombre_paciente) LIKE '% % %'
                           THEN SUBSTRING(unaccent(nombre_paciente) FROM '\\S+\\s+(\\S+\\s+\\S+)$')
                           ELSE SUBSTRING(unaccent(nombre_paciente) FROM '(\\S+)$')
                       END AS key
                FROM sigsa3
                WHERE paciente_id IS NULL AND nombre_paciente IS NOT NULL AND nombre_paciente <> ''
            ) s
            JOIN (
                SELECT id, nombre_completo,
                       CASE WHEN unaccent(nombre_completo) LIKE '% % %'
                           THEN SUBSTRING(unaccent(nombre_completo) FROM '\\S+\\s+(\\S+\\s+\\S+)$')
                           ELSE SUBSTRING(unaccent(nombre_completo) FROM '(\\S+)$')
                       END AS key
                FROM pacientes
                WHERE nombre_completo IS NOT NULL AND nombre_completo <> ''
            ) p ON s.key = p.key
              AND similarity(unaccent(s.nombre_paciente), unaccent(p.nombre_completo)) > 0.2
            ORDER BY s.id,
              similarity(unaccent(s.nombre_paciente), unaccent(p.nombre_completo)) DESC
        """), engine)
        for _, row in paso6b.iterrows():
            rid = int(row["id"])
            pid = int(row["pac_id"])
            updates_paciente[rid] = pid
            df.loc[df["id"] == rid, "paciente_id"] = pid
            resultados["paso6b_paciente"] += 1
    yield {"step": "paso6b", "progress": 95, "message": f"Paso 6b — clave + trigram >0.2: {resultados['paso6b_paciente']} pacientes", **resultados}

    _aplicar_updates()
    total_pac = sum(resultados[k] for k in ("paso1_paciente", "paso2_paciente", "paso3_paciente", "paso6b_paciente"))
    total_con = sum(resultados[k] for k in ("paso2_consulta", "paso4_consulta", "paso5_consulta", "paso6a_consulta"))
    elapsed = (ahora() - t0).total_seconds()
    yield {"step": "done", "progress": 100, "message": f"✅ {total_pac} pacientes, {total_con} consultas asociados ({elapsed:.1f}s)", **resultados}


def asociar_paciente(expediente: str, no_historia_clinica: str, db: Session) -> dict:
    from modules.pacientes.models import PacienteModel

    paciente = db.query(PacienteModel).filter(
        PacienteModel.expediente == expediente
    ).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con expediente '{expediente}' no encontrado"
        )

    registros = db.query(Sigsa3Model).filter(
        Sigsa3Model.no_historia_clinica == no_historia_clinica
    ).all()
    if not registros:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron registros SIGSA-3 con historia clínica '{no_historia_clinica}'"
        )

    asociados = 0
    for reg in registros:
        if reg.paciente_id != paciente.id:
            reg.paciente_id = paciente.id
            asociados += 1

    db.commit()
    return {
        "expediente": expediente,
        "no_historia_clinica": no_historia_clinica,
        "paciente_id": paciente.id,
        "registros_encontrados": len(registros),
        "registros_asociados": asociados,
    }


def _parse_fechas(desde: str, hasta: str) -> tuple[date, date]:
    try:
        return (
            datetime.strptime(desde, "%Y-%m-%d").date(),
            datetime.strptime(hasta, "%Y-%m-%d").date(),
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")


def dx_por_codigo_cie(db: Session, desde: str, hasta: str, codigos: list[str]) -> dict:
    f_desde, f_hasta = _parse_fechas(desde, hasta)

    placeholders = ", ".join(f":c{i}" for i in range(len(codigos)))
    params = {"desde": f_desde, "hasta": f_hasta}
    for i, c in enumerate(codigos):
        params[f"c{i}"] = c

    rows = db.execute(text(f"""
        SELECT
            tipo_consulta,
            codigo_cie_10,
            COUNT(*) AS total,
            COUNT(DISTINCT paciente_id) AS pacientes
        FROM sigsa3
        WHERE fecha_consulta BETWEEN :desde AND :hasta
          AND codigo_cie_10 IS NOT NULL
          AND codigo_cie_10 <> ''
          AND codigo_cie_10 IN ({placeholders})
        GROUP BY tipo_consulta, codigo_cie_10
        ORDER BY tipo_consulta, total DESC
    """), params).fetchall()

    total_pacientes = db.execute(text(f"""
        SELECT COUNT(DISTINCT paciente_id) AS total
        FROM sigsa3
        WHERE fecha_consulta BETWEEN :desde AND :hasta
          AND codigo_cie_10 IS NOT NULL
          AND codigo_cie_10 <> ''
          AND codigo_cie_10 IN ({placeholders})
    """), params).scalar()

    datos = []
    total_general = 0
    for r in rows:
        m = r._mapping
        t = int(m["total"])
        total_general += t
        datos.append({
            "tipo_consulta": str(m["tipo_consulta"]),
            "codigo_cie_10": str(m["codigo_cie_10"]),
            "total": t,
            "pacientes": int(m["pacientes"]),
        })

    return {
        "titulo": "Diagnósticos por Código CIE-10",
        "desde": f_desde,
        "hasta": f_hasta,
        "codigos_filtrados": codigos,
        "datos": datos,
        "total_general": total_general,
        "total_pacientes": int(total_pacientes) if total_pacientes else 0,
        "generado_en": datetime.now().isoformat(),
    }


def dx_z34(db: Session, desde: str, hasta: str) -> dict:
    return dx_por_codigo_cie(db, desde, hasta, ["Z:34"])


def dx_z10(db: Session, desde: str, hasta: str) -> dict:
    return dx_por_codigo_cie(db, desde, hasta, ["Z:10:4", "Z:10:5", "Z:10:6"])





def truncate_tabla(db: Session) -> dict:
    db.execute(text("TRUNCATE TABLE sigsa3 RESTART IDENTITY CASCADE"))
    db.commit()
    return {"truncado": True, "tabla": "sigsa3"}


def exportar_csv(db: Session) -> bytes:
    import csv
    import io

    registros = db.query(Sigsa3Model).order_by(Sigsa3Model.id).all()
    if not registros:
        return b""

    output = io.StringIO()
    writer = csv.writer(output)
    columns = [
        "id", "paciente_id", "medico_id", "consulta_id", "personal_salud",
        "fecha_consulta", "no_historia_clinica", "nombre_paciente", "sexo",
        "edad_dias", "edad_meses", "edad_anios", "tipo_consulta", "control",
        "semana_gestacional", "codigo_cie_10", "dx", "especialidad",
    ]
    writer.writerow(columns)
    for r in registros:
        writer.writerow([
            r.id, r.paciente_id, r.medico_id, r.consulta_id, r.personal_salud,
            r.fecha_consulta, r.no_historia_clinica, r.nombre_paciente, r.sexo,
            r.edad_dias, r.edad_meses, r.edad_anios, r.tipo_consulta, r.control,
            r.semana_gestacional, r.codigo_cie_10, r.dx, r.especialidad,
        ])
    return ("\ufeff" + output.getvalue()).encode("utf-8")


def listar_no_asociados(db: Session, limit: int = 100) -> list[Sigsa3Model]:
    return (
        db.query(Sigsa3Model)
        .filter(Sigsa3Model.paciente_id.is_(None))
        .order_by(Sigsa3Model.id.desc())
        .limit(min(limit, 500))
        .all()
    )


# =====================================================================
# NORMALIZACIÓN: sigsa3 (staging) → sigsa3_registros
# =====================================================================

def _normalizar_codigo_cie10(codigo: str) -> str:
    """Convierte código CIE-10 del formato SIGSA-3 (Z:34, O:82:9) a formato estándar (Z34, O82.9)."""
    if not codigo:
        return ""
    c = codigo.strip().upper()
    c = c.replace(":", "")
    if len(c) > 3 and c[3] != ".":
        c = c[:3] + "." + c[3:]
    return c


def _resolver_cie10_id(db: Session, codigo_sigsa3: str, cie10_cache: dict) -> int | None:
    """Resuelve código CIE-10 string → FK a cie10_catalogo.id usando caché en memoria."""
    if not codigo_sigsa3:
        return None
    if codigo_sigsa3 in cie10_cache:
        return cie10_cache[codigo_sigsa3]
    estandar = _normalizar_codigo_cie10(codigo_sigsa3)
    if estandar in cie10_cache:
        return cie10_cache[estandar]
    # Buscar en DB
    row = db.execute(
        text("SELECT id FROM cie10_catalogo WHERE codigo = :c OR codigo = :e LIMIT 1"),
        {"c": codigo_sigsa3, "e": estandar},
    ).first()
    if row:
        cid = row[0]
        cie10_cache[codigo_sigsa3] = cid
        cie10_cache[estandar] = cid
        return cid
    cie10_cache[codigo_sigsa3] = None
    return None


def _resolver_especialidad_id(db: Session, especialidad: str, esp_cache: dict) -> int | None:
    """Resuelve especialidad string → FK a especialidades.id."""
    if not especialidad:
        return None
    key = especialidad.strip().lower()
    if key in esp_cache:
        return esp_cache[key]
    row = db.execute(
        text("SELECT id FROM especialidades WHERE LOWER(nombre) = :n OR LOWER(abreviatura) = :n LIMIT 1"),
        {"n": key},
    ).first()
    if row:
        eid = row[0]
        esp_cache[key] = eid
        return eid
    esp_cache[key] = None
    return None


def _resolver_tipo_consulta_id(tipo_str: str | None) -> int | None:
    """Resuelve tipo_consulta string ('1 Primera', '3 Emergencia') → id."""
    if not tipo_str:
        return None
    t = tipo_str.strip()
    num = t.split()[0] if " " in t else t
    try:
        n = int(num)
        if n in (1, 2, 3):
            return n
    except ValueError:
        return None
    return None


def normalizar(db: Session, batch_size: int = 1000) -> dict:
    """Migra registros de sigsa3 (staging) a sigsa3_registros (normalizado).
    Solo migra registros con paciente_id + (medico_id o personal_salud_id).
    Los registros migrados se eliminan de sigsa3 para ahorrar espacio."""
    cie10_cache = {}
    esp_cache = {}

    total_migrados = 0
    total_omitidos = 0
    total_errores = 0

    while True:
        registros = (
            db.query(Sigsa3Model)
            .filter(
                Sigsa3Model.paciente_id.isnot(None),
                Sigsa3Model.paciente_id != 0,
            )
            .order_by(Sigsa3Model.id)
            .limit(batch_size)
            .all()
        )
        if not registros:
            break

        for reg in registros:
            try:
                tipo_id = _resolver_tipo_consulta_id(reg.tipo_consulta) or reg.tipo_consulta_id
                cie10_id = reg.codigo_cie_10_id or _resolver_cie10_id(db, reg.codigo_cie_10, cie10_cache)
                esp_id = reg.especialidad_id or _resolver_especialidad_id(db, reg.especialidad, esp_cache)

                nuevo = Sigsa3RegistroModel(
                    paciente_id=reg.paciente_id,
                    medico_id=reg.medico_id,
                    personal_salud_id=reg.personal_salud_id,
                    consulta_id=reg.consulta_id,
                    fecha_consulta=reg.fecha_consulta,
                    tipo_consulta_id=tipo_id,
                    control=reg.control,
                    semana_gestacional=reg.semana_gestacional,
                    codigo_cie_10_id=cie10_id,
                    especialidad_id=esp_id,
                )
                db.add(nuevo)
                db.flush()
                db.delete(reg)
                total_migrados += 1
            except Exception:
                total_errores += 1
                continue

        db.commit()

    # Omitidos: los que tienen paciente_id pero no medico_id ni personal_salud_id
    omitidos = db.query(Sigsa3Model).filter(
        Sigsa3Model.paciente_id.isnot(None),
        Sigsa3Model.paciente_id != 0,
        Sigsa3Model.medico_id.is_(None),
        Sigsa3Model.personal_salud_id.is_(None),
    ).count()

    return {
        "migrados": total_migrados,
        "omitidos_sin_medico": omitidos,
        "pendientes_sin_paciente": db.query(Sigsa3Model).filter(
            Sigsa3Model.paciente_id.is_(None)
        ).count(),
        "errores": total_errores,
    }


