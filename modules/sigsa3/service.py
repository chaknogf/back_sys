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
    """Asocia medico_id a registros SIGSA3 usando personal_salud con medicos.nombre."""
    from modules.medicos.models import MedicoModel

    registros = db.query(Sigsa3Model).filter(
        Sigsa3Model.medico_id.is_(None),
        Sigsa3Model.personal_salud.isnot(None),
    ).all()
    if not registros:
        return {"registros_encontrados": 0, "asociados": 0}

    medicos_cache = {}
    asociados = 0
    for reg in registros:
        nombre = reg.personal_salud.strip()
        if nombre not in medicos_cache:
            medico = db.query(MedicoModel).filter(
                MedicoModel.nombre.ilike(f"%{nombre}%")
            ).first()
            medicos_cache[nombre] = medico.id if medico else None
        medico_id = medicos_cache[nombre]
        if medico_id:
            reg.medico_id = medico_id
            asociados += 1

    db.commit()
    return {"registros_encontrados": len(registros), "asociados": asociados}


def asociar_paciente_y_consulta(db: Session) -> dict:
    """Pipeline completo usando pandas para asociación masiva:
    1. paciente_id: nombre_paciente = nombre_completo AND no_historia_clinica = expediente
    2. paciente_id: nombre_paciente CONTAINS nombre_completo (nulls)
    3. paciente_id: no_historia_clinica = expediente (nulls)
    4. consulta_id: paciente_id + fecha_consulta + tipo_consulta (nulls)
    5. consulta_id: no_historia_clinica = documento + fecha_consulta (nulls) + paciente_id
    """
    import pandas as pd
    from modules.pacientes.models import PacienteModel
    from modules.consultas.models import ConsultaModel

    resultados = {
        "paso1_paciente": 0,
        "paso2_paciente": 0,
        "paso3_paciente": 0,
        "paso4_consulta": 0,
        "paso5_consulta": 0,
        "paso5_paciente": 0,
    }

    def _extraer_tipo_consulta(tipo_str):
        if not tipo_str:
            return None
        try:
            return int(tipo_str.strip().split()[0])
        except (ValueError, IndexError):
            return None

    # Cargar todos los registros SIGSA3
    registros = db.query(Sigsa3Model).all()
    if not registros:
        return resultados

    # Convertir a DataFrame
    data = []
    for r in registros:
        data.append({
            "id": r.id,
            "nombre_paciente": r.nombre_paciente,
            "no_historia_clinica": r.no_historia_clinica,
            "fecha_consulta": r.fecha_consulta,
            "tipo_consulta": r.tipo_consulta,
            "paciente_id": r.paciente_id,
            "consulta_id": r.consulta_id,
            "medico_id": r.medico_id,
        })
    df = pd.DataFrame(data)

    # Cargar pacientes y consultas como DataFrames
    pacientes = db.query(PacienteModel).filter(
        PacienteModel.nombre_completo.isnot(None),
        PacienteModel.expediente.isnot(None),
    ).all()
    df_pac = pd.DataFrame([{
        "pac_id": p.id,
        "nombre_completo": p.nombre_completo,
        "expediente": p.expediente,
    } for p in pacientes]) if pacientes else pd.DataFrame(columns=["pac_id", "nombre_completo", "expediente"])

    consultas = db.query(ConsultaModel).filter(
        ConsultaModel.documento.isnot(None),
    ).all()
    df_con = pd.DataFrame([{
        "con_id": c.id,
        "paciente_id": c.paciente_id,
        "fecha_consulta": c.fecha_consulta,
        "tipo_consulta": c.tipo_consulta,
        "documento": c.documento,
    } for c in consultas]) if consultas else pd.DataFrame(columns=["con_id", "paciente_id", "fecha_consulta", "tipo_consulta", "documento"])

    # Mapear ID → objeto SIGSA3 para escritura rápida
    reg_map = {r.id: r for r in registros}

    # PASO 1: nombre_paciente = nombre_completo AND no_historia_clinica = expediente
    nulls = df[df["paciente_id"].isna() & df["nombre_paciente"].notna() & df["no_historia_clinica"].notna()]
    if not nulls.empty and not df_pac.empty:
        merged = nulls.merge(df_pac, left_on=["nombre_paciente", "no_historia_clinica"],
                             right_on=["nombre_completo", "expediente"], how="inner")
        for _, row in merged.iterrows():
            reg_map[row["id"]].paciente_id = int(row["pac_id"])
            resultados["paso1_paciente"] += 1
        df = pd.DataFrame([{
            "id": r.id, "nombre_paciente": r.nombre_paciente, "no_historia_clinica": r.no_historia_clinica,
            "fecha_consulta": r.fecha_consulta, "tipo_consulta": r.tipo_consulta,
            "paciente_id": r.paciente_id, "consulta_id": r.consulta_id, "medico_id": r.medico_id,
        } for r in registros])

    # PASO 2: nombre_paciente CONTAINS nombre_completo (nulls)
    nulls = df[df["paciente_id"].isna() & df["nombre_paciente"].notna()]
    if not nulls.empty and not df_pac.empty:
        for _, row in nulls.iterrows():
            match = df_pac[df_pac["nombre_completo"].str.contains(row["nombre_paciente"], case=False, na=False)]
            if not match.empty:
                reg_map[row["id"]].paciente_id = int(match.iloc[0]["pac_id"])
                resultados["paso2_paciente"] += 1
        df = pd.DataFrame([{
            "id": r.id, "nombre_paciente": r.nombre_paciente, "no_historia_clinica": r.no_historia_clinica,
            "fecha_consulta": r.fecha_consulta, "tipo_consulta": r.tipo_consulta,
            "paciente_id": r.paciente_id, "consulta_id": r.consulta_id, "medico_id": r.medico_id,
        } for r in registros])

    # PASO 3: no_historia_clinica = expediente (nulls)
    nulls = df[df["paciente_id"].isna() & df["no_historia_clinica"].notna()]
    if not nulls.empty and not df_pac.empty:
        merged = nulls.merge(df_pac, left_on="no_historia_clinica", right_on="expediente", how="inner")
        for _, row in merged.iterrows():
            reg_map[row["id"]].paciente_id = int(row["pac_id"])
            resultados["paso3_paciente"] += 1
        df = pd.DataFrame([{
            "id": r.id, "nombre_paciente": r.nombre_paciente, "no_historia_clinica": r.no_historia_clinica,
            "fecha_consulta": r.fecha_consulta, "tipo_consulta": r.tipo_consulta,
            "paciente_id": r.paciente_id, "consulta_id": r.consulta_id, "medico_id": r.medico_id,
        } for r in registros])

    # PASO 4: consulta_id por paciente_id + fecha_consulta + tipo_consulta (nulls)
    nulls = df[df["consulta_id"].isna() & df["paciente_id"].notna() & df["fecha_consulta"].notna()]
    if not nulls.empty and not df_con.empty:
        df_con["tipo_num"] = df_con["tipo_consulta"].apply(lambda x: x if isinstance(x, (int, float)) else None)
        for _, row in nulls.iterrows():
            tipo_num = _extraer_tipo_consulta(row["tipo_consulta"])
            masks = [
                df_con["paciente_id"] == row["paciente_id"],
                df_con["fecha_consulta"] == row["fecha_consulta"],
            ]
            if tipo_num is not None:
                masks.append(df_con["tipo_num"] == tipo_num)
            match = df_con[pd.Series(masks).all()]
            if not match.empty:
                reg_map[row["id"]].consulta_id = int(match.iloc[0]["con_id"])
                resultados["paso4_consulta"] += 1
        df = pd.DataFrame([{
            "id": r.id, "nombre_paciente": r.nombre_paciente, "no_historia_clinica": r.no_historia_clinica,
            "fecha_consulta": r.fecha_consulta, "tipo_consulta": r.tipo_consulta,
            "paciente_id": r.paciente_id, "consulta_id": r.consulta_id, "medico_id": r.medico_id,
        } for r in registros])

    # PASO 5: consulta_id por no_historia_clinica = documento + fecha_consulta (nulls)
    nulls = df[df["consulta_id"].isna() & df["no_historia_clinica"].notna() & df["fecha_consulta"].notna()]
    if not nulls.empty and not df_con.empty:
        merged = nulls.merge(df_con, left_on=["no_historia_clinica", "fecha_consulta"],
                             right_on=["documento", "fecha_consulta"], how="inner")
        for _, row in merged.iterrows():
            reg_map[row["id"]].consulta_id = int(row["con_id"])
            resultados["paso5_consulta"] += 1
            if pd.isna(row["paciente_id_x"]) or row["paciente_id_x"] is None:
                reg_map[row["id"]].paciente_id = int(row["paciente_id_y"])
                resultados["paso5_paciente"] += 1

    db.commit()
    return resultados


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


def listar_no_asociados(db: Session, limit: int = 100) -> list[Sigsa3Model]:
    return (
        db.query(Sigsa3Model)
        .filter(Sigsa3Model.paciente_id.is_(None))
        .order_by(Sigsa3Model.id.desc())
        .limit(min(limit, 500))
        .all()
    )


def actualizar_especialidad_por_medico(personal_salud: str, db: Session) -> dict:
    from modules.medicos.models import MedicoModel

    medico = db.query(MedicoModel).filter(
        MedicoModel.nombre.ilike(f"%{personal_salud}%")
    ).first()
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró médico con nombre '{personal_salud}'"
        )
    if not medico.especialidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El médico '{medico.nombre}' no tiene especialidad registrada"
        )

    registros = db.query(Sigsa3Model).filter(
        Sigsa3Model.personal_salud == personal_salud
    ).all()
    if not registros:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron registros SIGSA-3 con personal_salud '{personal_salud}'"
        )

    actualizados = 0
    for reg in registros:
        if reg.especialidad != medico.especialidad:
            reg.especialidad = medico.especialidad
            actualizados += 1

    db.commit()
    return {
        "personal_salud": personal_salud,
        "medico_id": medico.id,
        "medico_nombre": medico.nombre,
        "especialidad": medico.especialidad,
        "registros_encontrados": len(registros),
        "registros_actualizados": actualizados,
    }
