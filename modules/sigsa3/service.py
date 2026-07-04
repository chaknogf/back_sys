import csv
import io
import re
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
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
        return "1 Primeras"
    if (row.get("consulta_primera") or "").strip().upper() == "X":
        return "1 Primeras"
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

CSV_HEADERS = [
    "personal_salud", "fecha_consulta", "no_historia_clinica",
    "nombre_paciente", "sexo", "edad_dias", "edad_meses", "edad_anios",
    "tipo_consulta", "control", "semana_gestacional",
    "codigo_cie_10", "dx", "especialidad",
]

INTEGER_FIELDS = {"edad_dias", "edad_meses", "edad_anios", "semana_gestacional"}
DATE_FIELDS = {"fecha_consulta"}
MAX_LENGTHS = {
    "personal_salud": 100, "no_historia_clinica": 30, "nombre_paciente": 150,
    "sexo": 1, "tipo_consulta": 80, "control": 80,
    "codigo_cie_10": 30, "especialidad": 100,
}


def generar_plantilla_csv() -> io.StringIO:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(CSV_HEADERS)
    writer.writerow([
        "Dr. Juan Perez", "2025-01-15", "HC-00123",
        "Maria Lopez", "F", "0", "6", "25",
        "Consulta Externa", "Control Prenatal", "32",
        "Z34.9", "Embarazo normal", "Medicina General",
    ])
    buf.seek(0)
    return buf


def _parse_row(row: dict) -> dict:
    parsed = {}
    for key in CSV_HEADERS:
        value = row.get(key, "").strip()
        if value == "":
            parsed[key] = None
        elif key in INTEGER_FIELDS:
            try:
                parsed[key] = int(value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Valor inválido en columna '{key}': se esperaba un número entero, se recibió '{value}'",
                )
        elif key in DATE_FIELDS:
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    parsed[key] = datetime.strptime(value, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Valor inválido en columna '{key}': formato de fecha no reconocido '{value}' (use YYYY-MM-DD)",
                )
        else:
            max_len = MAX_LENGTHS.get(key)
            if max_len and len(value) > max_len:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Valor demasiado largo en columna '{key}': máximo {max_len} caracteres, se recibió {len(value)}",
                )
            parsed[key] = value
    return parsed


async def importar_csv(file: UploadFile, db: Session) -> dict:
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

    normalized_headers = [h.strip().lower() for h in reader.fieldnames]
    missing = [h for h in CSV_HEADERS if h not in normalized_headers]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Faltan columnas requeridas: {', '.join(missing)}",
        )

    registros = []
    errores = []
    for i, row in enumerate(reader, start=2):
        try:
            clean_row = {k.strip().lower(): v for k, v in row.items()}
            parsed = _parse_row(clean_row)
            registros.append(Sigsa3Create(**parsed))
        except HTTPException as e:
            errores.append({"fila": i, "error": e.detail})
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
