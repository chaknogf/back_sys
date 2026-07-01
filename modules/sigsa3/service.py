import csv
import io
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional as Opt
from datetime import date, datetime

from modules.sigsa3.models import Sigsa3Model
from modules.sigsa3.schemas import Sigsa3Create, Sigsa3Update

CSV_HEADERS = [
    "personal_salud", "fecha_consulta", "no_historia_clinica",
    "nombre_paciente", "sexo", "pueblo", "comunidad_linguistica",
    "edad_dias", "edad_meses", "edad_anios",
    "departamento_residencia", "municipio_residencia", "comunidad",
    "direccion", "tipo_consulta", "control", "semana_gestacional",
    "descripcion_diagnostico_control", "codigo_cie_10", "dx",
    "tipologia", "especialidad",
]

INTEGER_FIELDS = {"edad_dias", "edad_meses", "edad_anios", "semana_gestacional"}
DATE_FIELDS = {"fecha_consulta"}
MAX_LENGTHS = {
    "personal_salud": 100, "no_historia_clinica": 30, "nombre_paciente": 150,
    "sexo": 1, "pueblo": 80, "comunidad_linguistica": 80,
    "departamento_residencia": 100, "municipio_residencia": 100,
    "comunidad": 150, "tipo_consulta": 80, "control": 80,
    "codigo_cie_10": 30, "tipologia": 100, "especialidad": 100,
}


def generar_plantilla_csv() -> io.StringIO:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(CSV_HEADERS)
    writer.writerow([
        "Dr. Juan Perez", "2025-01-15", "HC-00123",
        "Maria Lopez", "F", "Kaqchikel", "Kaqchikel",
        "0", "6", "25",
        "Chimaltenango", "Tecpán", "Centro",
        "5a Avenida 12-34", "Consulta Externa", "Control Prenatal", "32",
        "Control prenatal normal", "Z34.9", "Embarazo normal",
        "Población General", "Medicina General",
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

    for encoding in ("utf-8", "latin-1", "cp1252"):
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

    reader = csv.DictReader(io.StringIO(text))

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
