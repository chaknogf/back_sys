import csv
import io
import re
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import text, or_
from sqlalchemy.orm import Session
from typing import List, Optional as Opt
from datetime import date, datetime

from modules.sigsa3.models import Sigsa3Model
from modules.sigsa3.schemas import Sigsa3Create, Sigsa3Update

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
    "especialidad": "especialidad",
    "paciente_id": "paciente_id",
    "medico_id": "medico_id",
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
    """Parsea formato '22-jun' a date (asume año actual)."""
    if not fecha_str:
        return None
    fecha_str = fecha_str.strip().lower()
    match = re.match(r"(\d{1,2})[-/](\w+)", fecha_str)
    if not match:
        return None
    dia = int(match.group(1))
    mes_str = match.group(2)[:3]
    mes = MESES_ES.get(mes_str)
    if not mes:
        return None
    anio = date.today().year
    try:
        return date(anio, mes, dia)
    except ValueError:
        return None


def _determinar_tipo_consulta(row: dict) -> str:
    """Determina tipo_consulta basado en las columnas con 'X'."""
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
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se pudo decodificar el archivo. Use UTF-8 o Latin-1",
        )

    if text.startswith("\ufeff"):
        text = text[1:]

    try:
        dialect = csv.Sniffer().sniff(text[:8192])
    except csv.Error:
        dialect = csv.excel

    reader = csv.DictReader(io.StringIO(text), dialect=dialect)

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
            medico_id = _parse_int_safe(mapped.get("medico_id"))
            consulta_id = _parse_int_safe(mapped.get("consulta_id"))

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

    try:
        objs = [Sigsa3Model(**r.model_dump()) for r in registros]
        db.add_all(objs)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al insertar los registros en la base de datos",
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


def asociar_medico(db: Session) -> dict:
    """Asocia medico_id a registros SIGSA3 usando personal_salud."""
    from modules.sigsa3.models import PersonalSaludModel

    registros = db.query(Sigsa3Model).filter(
        Sigsa3Model.medico_id.is_(None),
        Sigsa3Model.personal_salud.isnot(None),
    ).all()
    if not registros:
        return {"registros_encontrados": 0, "asociados": 0}

    personal = db.query(PersonalSaludModel).filter(
        PersonalSaludModel.medico_id.isnot(None)
    ).all()
    if not personal:
        return {"registros_encontrados": len(registros), "asociados": 0}

    nombre_to_medico = {p.nombre.strip().lower(): p.medico_id for p in personal}

    asociados = 0
    for reg in registros:
        nombre = reg.personal_salud.strip().lower() if reg.personal_salud else ""
        if not nombre:
            continue
        medico_id = nombre_to_medico.get(nombre)
        if not medico_id:
            for ps_nombre, ps_medico_id in nombre_to_medico.items():
                if ps_nombre in nombre or nombre in ps_nombre:
                    medico_id = ps_medico_id
                    break
        if medico_id:
            reg.medico_id = medico_id
            asociados += 1

    db.commit()
    return {"registros_encontrados": len(registros), "asociados": asociados}


def asociar_paciente_y_consulta(db: Session):
    """Pipeline completo usando pandas para asociación masiva.
    Generador que yield eventos de progreso como dicts.
    1. paciente_id: nombre_paciente = nombre_completo AND no_historia_clinica = expediente
    2. paciente_id: nombre_paciente CONTAINS nombre_completo (nulls)
    3. paciente_id: no_historia_clinica = expediente (nulls)
    4. consulta_id: paciente_id + fecha_consulta + tipo_consulta (nulls)
    5. consulta_id: no_historia_clinica = documento + fecha_consulta (nulls) + paciente_id
    """
    import pandas as pd
    from datetime import datetime
    from sqlalchemy import text

    ahora = datetime.now
    t0 = ahora()

    resultados = {k: 0 for k in (
        "paso1_paciente", "paso2_paciente", "paso3_paciente",
        "paso4_consulta", "paso5_consulta", "paso5_paciente",
    )}

    def _extraer_tipo_consulta(tipo_str):
        if not tipo_str:
            return None
        try:
            return int(str(tipo_str).strip().split()[0])
        except (ValueError, IndexError):
            return None

    yield {"step": "load", "message": "Iniciando asociación...", "progress": 0, **resultados}

    # ── Cargar datos con pd.read_sql (40-60% más rápido que ORM) ──
    from core.database import engine
    conn = engine.raw_connection()

    df = pd.read_sql(
        "SELECT id, nombre_paciente, no_historia_clinica, fecha_consulta, tipo_consulta, paciente_id, consulta_id FROM sigsa3 WHERE paciente_id IS NULL OR consulta_id IS NULL",
        conn, parse_dates=["fecha_consulta"]
    )
    print(f"[PIPELINE] registros cargados={len(df)}")
    if df.empty:
        conn.close()
        yield {"step": "done", "message": "Sin registros SIGSA-3 pendientes", "progress": 100, **resultados}
        return

    df_pac = pd.read_sql(
        "SELECT id AS pac_id, nombre_completo, expediente FROM pacientes WHERE nombre_completo IS NOT NULL",
        conn
    )

    df_con = pd.read_sql(
        "SELECT id AS con_id, paciente_id, fecha_consulta, tipo_consulta, documento FROM consultas WHERE documento IS NOT NULL",
        conn, parse_dates=["fecha_consulta"]
    )

    yield {
        "step": "data_loaded", "progress": 5,
        "message": f"{len(df)} registros SIGSA-3, {len(df_pac)} pacientes, {len(df_con)} consultas",
        **resultados,
    }

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
    mask = df["paciente_id"].isna() & df["nombre_paciente"].notna() & df["no_historia_clinica"].notna()
    if mask.any() and not df_pac.empty:
        merged = df[mask].merge(df_pac, left_on=["nombre_paciente", "no_historia_clinica"],
                                right_on=["nombre_completo", "expediente"], how="inner")
        for _, row in merged.iterrows():
            updates_paciente[row["id"]] = int(row["pac_id"])
            resultados["paso1_paciente"] += 1
    yield {"step": "paso1", "progress": 20, "message": f"Paso 1 — nombre exacto + expediente: {resultados['paso1_paciente']} pacientes", **resultados}

    # ── PASO 2: SQL con ILIKE + trigram GIN index ──
    mask_s2 = df["paciente_id"].isna() & df["nombre_paciente"].notna()
    if mask_s2.any():
        paso2 = pd.read_sql("""
            SELECT DISTINCT s.id, p.id AS pac_id
            FROM sigsa3 s
            JOIN pacientes p ON p.nombre_completo IS NOT NULL
              AND s.nombre_paciente ILIKE '%' || p.nombre_completo || '%'
            WHERE s.paciente_id IS NULL
              AND s.nombre_paciente IS NOT NULL
        """, conn)
        for _, row in paso2.iterrows():
            rid = row["id"]
            pid = int(row["pac_id"])
            updates_paciente[rid] = pid
            df.loc[df["id"] == rid, "paciente_id"] = pid
            resultados["paso2_paciente"] += 1
    yield {"step": "paso2", "progress": 40, "message": f"Paso 2 — nombre contiene: {resultados['paso2_paciente']} pacientes", **resultados}

    # ── PASO 3: no_historia_clinica = expediente ──
    mask = df["paciente_id"].isna() & df["no_historia_clinica"].notna()
    if mask.any() and not df_pac.empty:
        merged = df[mask].merge(df_pac, left_on="no_historia_clinica", right_on="expediente", how="inner")
        for _, row in merged.iterrows():
            updates_paciente[row["id"]] = int(row["pac_id"])
            resultados["paso3_paciente"] += 1
    yield {"step": "paso3", "progress": 55, "message": f"Paso 3 — expediente: {resultados['paso3_paciente']} pacientes", **resultados}

    # ── PASO 4: consulta_id por paciente_id + fecha_consulta + tipo_consulta ──
    mask = df["consulta_id"].isna() & df["paciente_id"].notna() & df["fecha_consulta"].notna()
    if mask.any() and not df_con.empty:
        sub = df.loc[mask, ["id", "paciente_id", "fecha_consulta", "tipo_consulta"]].copy()
        sub["tipo_num"] = sub["tipo_consulta"].apply(_extraer_tipo_consulta)

        df_con = df_con.copy()
        df_con["tipo_num"] = df_con["tipo_consulta"]

        merged = sub.merge(df_con, left_on=["paciente_id", "fecha_consulta"],
                           right_on=["paciente_id", "fecha_consulta"], how="inner", suffixes=("_sig", "_con"))
        merged = merged[
            merged["tipo_num_sig"].isna() | (merged["tipo_num_sig"] == merged["tipo_num_con"])
        ].drop_duplicates(subset="id", keep="first")

        for _, row in merged.iterrows():
            rid = row["id"]
            updates_consulta[rid] = int(row["con_id"])
            df.loc[df["id"] == rid, "consulta_id"] = row["con_id"]
            resultados["paso4_consulta"] += 1
    yield {"step": "paso4", "progress": 70, "message": f"Paso 4 — paciente+fecha+tipo: {resultados['paso4_consulta']} consultas", **resultados}

    # ── PASO 5: consulta_id por no_historia_clinica = documento + fecha_consulta ──
    mask = df["consulta_id"].isna() & df["no_historia_clinica"].notna() & df["fecha_consulta"].notna()
    print(f"  [PASO 5] candidatos={mask.sum()} | rango fechas sigsa3: {df.loc[mask, 'fecha_consulta'].min()} a {df.loc[mask, 'fecha_consulta'].max()} | rango fechas df_con: {df_con['fecha_consulta'].min()} a {df_con['fecha_consulta'].max()}")
    if mask.any() and not df_con.empty:
        merged = df[mask].merge(df_con, left_on=["no_historia_clinica", "fecha_consulta"],
                                right_on=["documento", "fecha_consulta"], how="inner", suffixes=("_sig", "_con"))
        print(f"  [PASO 5] merged rows={len(merged)}")
        merged = merged.drop_duplicates(subset="id", keep="first")
        print(f"  [PASO 5] merged after dedup={len(merged)}")
        for _, row in merged.iterrows():
            rid = row["id"]
            updates_consulta[rid] = int(row["con_id"])
            df.loc[df["id"] == rid, "consulta_id"] = row["con_id"]
            resultados["paso5_consulta"] += 1
            if pd.isna(row["paciente_id_sig"]):
                updates_paciente[rid] = int(row["paciente_id_con"])
                df.loc[df["id"] == rid, "paciente_id"] = row["paciente_id_con"]
                resultados["paso5_paciente"] += 1
    yield {"step": "paso5", "progress": 85, "message": f"Paso 5 — documento+fecha: {resultados['paso5_consulta']} consultas, {resultados['paso5_paciente']} pacientes adicionales", **resultados}

    _aplicar_updates()
    conn.close()
    total_pac = sum(resultados[k] for k in ("paso1_paciente", "paso2_paciente", "paso3_paciente"))
    total_con = sum(resultados[k] for k in ("paso4_consulta", "paso5_consulta"))
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


def listar_personal_salud(db: Session) -> list:
    from modules.sigsa3.models import PersonalSaludModel
    return db.query(PersonalSaludModel).order_by(PersonalSaludModel.nombre).all()


def crear_personal_salud(nombre: str, especialidad: str | None, medico_id: int | None, db: Session) -> dict:
    from modules.sigsa3.models import PersonalSaludModel
    existente = db.query(PersonalSaludModel).filter(PersonalSaludModel.nombre == nombre).first()
    if existente:
        raise HTTPException(status_code=409, detail=f"'{nombre}' ya existe en personal_salud")
    registro = PersonalSaludModel(nombre=nombre, especialidad=especialidad, medico_id=medico_id)
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return {"id": registro.id, "nombre": registro.nombre, "especialidad": registro.especialidad, "medico_id": registro.medico_id}


def actualizar_personal_salud(ps_id: int, nombre: str | None, especialidad: str | None, medico_id: int | None, db: Session) -> dict:
    from modules.sigsa3.models import PersonalSaludModel
    registro = db.query(PersonalSaludModel).filter(PersonalSaludModel.id == ps_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de personal_salud no encontrado")
    if nombre is not None:
        registro.nombre = nombre
    if especialidad is not None:
        registro.especialidad = especialidad
    if medico_id is not None:
        registro.medico_id = medico_id
    db.commit()
    db.refresh(registro)
    return {"id": registro.id, "nombre": registro.nombre, "especialidad": registro.especialidad, "medico_id": registro.medico_id}


def eliminar_personal_salud(ps_id: int, db: Session) -> dict:
    from modules.sigsa3.models import PersonalSaludModel
    registro = db.query(PersonalSaludModel).filter(PersonalSaludModel.id == ps_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de personal_salud no encontrado")
    db.delete(registro)
    db.commit()
    return {"eliminado": True}


def sincronizar_especialidad(db: Session) -> dict:
    """Sincroniza especialidad desde personal_salud → medicos y sigsa3."""
    from modules.sigsa3.models import PersonalSaludModel
    from modules.medicos.models import MedicoModel

    personal = db.query(PersonalSaludModel).filter(
        PersonalSaludModel.medico_id.isnot(None),
        PersonalSaludModel.especialidad.isnot(None),
    ).all()

    if not personal:
        return {"medicos_actualizados": 0, "sigsa3_actualizados": 0}

    medico_ids = [ps.medico_id for ps in personal]
    medicos = {
        m.id: m
        for m in db.query(MedicoModel).filter(MedicoModel.id.in_(medico_ids)).all()
    }

    nombre_a_especialidad = {}
    patrones = []
    for ps in personal:
        nombre_a_especialidad[ps.nombre.lower()] = ps.especialidad
        patrones.append(f"%{ps.nombre}%")

    condiciones = [
        Sigsa3Model.personal_salud.ilike(p) for p in patrones
    ]
    sigsa3_rows = db.query(Sigsa3Model).filter(or_(*condiciones)).all()

    medicos_actualizados = 0
    sigsa3_actualizados = 0

    for ps in personal:
        if not ps.especialidad:
            continue
        medico = medicos.get(ps.medico_id)
        if medico and medico.especialidad != ps.especialidad:
            medico.especialidad = ps.especialidad
            medicos_actualizados += 1

    for reg in sigsa3_rows:
        if reg.personal_salud:
            key = reg.personal_salud.strip().lower()
            target_esp = nombre_a_especialidad.get(key)
            if not target_esp:
                for ps_name, ps_esp in nombre_a_especialidad.items():
                    if key.endswith(ps_name) or ps_name.endswith(key):
                        target_esp = ps_esp
                        break
            if target_esp and reg.especialidad != target_esp:
                reg.especialidad = target_esp
                sigsa3_actualizados += 1

    db.commit()
    return {
        "medicos_actualizados": medicos_actualizados,
        "sigsa3_actualizados": sigsa3_actualizados,
    }


def listar_no_asociados(db: Session, limit: int = 100) -> list[Sigsa3Model]:
    return (
        db.query(Sigsa3Model)
        .filter(Sigsa3Model.paciente_id.is_(None))
        .order_by(Sigsa3Model.id.desc())
        .limit(min(limit, 500))
        .all()
    )


def actualizar_especialidad_por_medico(personal_salud_nombre: str, db: Session) -> dict:
    from modules.sigsa3.models import PersonalSaludModel

    ps = db.query(PersonalSaludModel).filter(
        PersonalSaludModel.nombre.ilike(personal_salud_nombre)
    ).first()
    if not ps:
        ps = db.query(PersonalSaludModel).filter(
            PersonalSaludModel.nombre.ilike(f"%{personal_salud_nombre}%")
        ).first()
    if not ps:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró '{personal_salud_nombre}' en personal_salud"
        )
    if not ps.especialidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{ps.nombre}' no tiene especialidad registrada en personal_salud"
        )

    registros = db.query(Sigsa3Model).filter(
        Sigsa3Model.personal_salud.ilike(f"%{ps.nombre}%")
    ).all()
    if not registros:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron registros SIGSA-3 con personal_salud que contenga '{ps.nombre}'"
        )

    actualizados = 0
    for reg in registros:
        if reg.especialidad != ps.especialidad:
            reg.especialidad = ps.especialidad
            actualizados += 1

    db.commit()
    return {
        "personal_salud": ps.nombre,
        "especialidad": ps.especialidad,
        "medico_id": ps.medico_id,
        "registros_encontrados": len(registros),
        "registros_actualizados": actualizados,
    }
