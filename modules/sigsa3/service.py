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
from modules.pacientes.models import PacienteModel
from modules.medicos.models import MedicoModel
from modules.consultas.models import ConsultaModel
from modules.especialidades.models import EspecialidadModel
from modules.cie10.models import Cie10Model
from modules.personal_salud.models import PersonalSaludModel
from modules.sigsa3_registros.models import TipoConsultaSigsa3Model
from modules.common.vector_similarity import (
    CONFIANZA_ALTA,
    CONFIANZA_MEDIA,
    idf_por_token,
    mejor_candidato,
    pesado_por_idf,
    similitud_compuesta,
    tokenizar,
    tokens_equivalentes,
)

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

    mapa_ps = _build_personal_salud_map(db)
    esp_cache = {}

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
            especialidad_str = mapped.get("especialidad")
            especialidad_id = _resolver_especialidad_id(db, especialidad_str, esp_cache) if especialidad_str else None
            paciente_id = _parse_int_safe(mapped.get("paciente_id"))
            consulta_id = _parse_int_safe(mapped.get("consulta_id"))

            ps_id = None
            medico_id = None
            if personal_salud:
                match_ps = _resolver_personal_salud(mapa_ps, personal_salud)
                if match_ps:
                    ps_id, medico_id, esp_from_ps = match_ps
                    if especialidad_id is None and esp_from_ps is not None:
                        especialidad_id = esp_from_ps

            dx = None
            if codigo_cie_10 and descripcion_diag:
                dx = f"{codigo_cie_10} {descripcion_diag}"
            elif descripcion_diag:
                dx = descripcion_diag

            registro = Sigsa3Create(
                personal_salud=personal_salud,
                personal_salud_id=ps_id,
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
                especialidad_id=especialidad_id,
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
    fecha_desde: Opt[date] = None,
    fecha_hasta: Opt[date] = None,
    no_historia_clinica: Opt[str] = None,
    nombre_paciente: Opt[str] = None,
    sexo: Opt[str] = None,
    tipo_consulta: Opt[str] = None,
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
    if fecha_desde:
        query = query.filter(Sigsa3Model.fecha_consulta >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Sigsa3Model.fecha_consulta <= fecha_hasta)
    if no_historia_clinica:
        query = query.filter(Sigsa3Model.no_historia_clinica.ilike(f"%{no_historia_clinica}%"))
    if nombre_paciente:
        query = query.filter(Sigsa3Model.nombre_paciente.ilike(f"%{nombre_paciente}%"))
    if sexo:
        query = query.filter(Sigsa3Model.sexo == sexo)
    if tipo_consulta:
        query = query.filter(Sigsa3Model.tipo_consulta.ilike(f"%{tipo_consulta}%"))
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


def _validar_fk_staging(db: Session, model, fk_id: int | None, campo: str, tabla: str) -> None:
    """Valida que el FK exista en su catálogo. 404 si no existe."""
    if fk_id is None:
        return
    if not db.get(model, fk_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{campo} con id {fk_id} no existe en {tabla}",
        )


def _resolver_fks_staging(db: Session, datos: dict, mapa_ps: dict | None = None) -> dict:
    """Resuelve FKs del staging por string usando la tabla puente personal_salud:
    - personal_salud (string) → personal_salud_id + medico_id + especialidad_id
    - codigo_cie_10 (string) → codigo_cie_10_id
    - validación de FKs numéricas contra catálogos
    """
    if mapa_ps is None:
        mapa_ps = _build_personal_salud_map(db)

    # personal_salud string → personal_salud_id / medico_id / especialidad_id
    nombre_ps = (datos.get("personal_salud") or "").strip()
    if nombre_ps:
        match = _resolver_personal_salud(mapa_ps, nombre_ps)
        if match:
            ps_id, medico_id, esp_id = match
            if datos.get("personal_salud_id") is None:
                datos["personal_salud_id"] = ps_id
            if datos.get("medico_id") is None and medico_id is not None:
                datos["medico_id"] = medico_id
            if datos.get("especialidad_id") is None and esp_id is not None:
                datos["especialidad_id"] = esp_id

    # tipo_consulta string ('1 Primera', '4 Interconsulta') → tipo_consulta_id
    if not datos.get("tipo_consulta_id") and datos.get("tipo_consulta"):
        datos["tipo_consulta_id"] = _resolver_tipo_consulta_id(datos["tipo_consulta"])

    # codigo_cie_10 string → codigo_cie_10_id
    if not datos.get("codigo_cie_10_id") and datos.get("codigo_cie_10"):
        cie10_cache = {}
        datos["codigo_cie_10_id"] = _resolver_cie10_id(db, datos["codigo_cie_10"], cie10_cache)

    # Validación de FKs numéricas contra catálogos
    _validar_fk_staging(db, PacienteModel, datos.get("paciente_id"), "paciente_id", "pacientes")
    _validar_fk_staging(db, MedicoModel, datos.get("medico_id"), "medico_id", "medicos")
    _validar_fk_staging(db, PersonalSaludModel, datos.get("personal_salud_id"), "personal_salud_id", "personal_salud")
    _validar_fk_staging(db, ConsultaModel, datos.get("consulta_id"), "consulta_id", "consultas")
    _validar_fk_staging(db, EspecialidadModel, datos.get("especialidad_id"), "especialidad_id", "especialidades")
    _validar_fk_staging(db, Cie10Model, datos.get("codigo_cie_10_id"), "codigo_cie_10_id", "cie10_catalogo")
    _validar_fk_staging(db, TipoConsultaSigsa3Model, datos.get("tipo_consulta_id"), "tipo_consulta_id", "tipos_consulta_sigsa3")
    return datos


def crear_registro(data: Sigsa3Create, db: Session) -> Sigsa3Model:
    datos = _resolver_fks_staging(db, data.model_dump())
    registro = Sigsa3Model(**datos)
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
    # Para resolver por string necesitamos el nombre previo si no viene
    if "personal_salud" not in update_data:
        update_data["personal_salud"] = registro.personal_salud
    update_data = _resolver_fks_staging(db, update_data)
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
    try:
        # Normalizado primero (sigsa3_registros), luego staging (sigsa3)
        q_normalizado = db.query(Sigsa3RegistroModel).filter(
            Sigsa3RegistroModel.fecha_consulta >= desde,
            Sigsa3RegistroModel.fecha_consulta <= hasta,
        )
        eliminados_normalizados = q_normalizado.count()
        q_normalizado.delete(synchronize_session=False)

        q_staging = db.query(Sigsa3Model).filter(
            Sigsa3Model.fecha_consulta >= desde,
            Sigsa3Model.fecha_consulta <= hasta,
        )
        eliminados_staging = q_staging.count()
        q_staging.delete(synchronize_session=False)

        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al eliminar los registros"
        )

    total = eliminados_staging + eliminados_normalizados
    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron registros en el periodo {desde} al {hasta}"
        )
    return {
        "eliminados": total,
        "sigsa3": eliminados_staging,
        "sigsa3_registros": eliminados_normalizados,
        "desde": desde.isoformat(),
        "hasta": hasta.isoformat(),
    }


def _build_personal_salud_map(db: Session) -> dict:
    """Construye el mapa nombre(personal_salud) → (id, medico_id, especialidad_id).
    personal_salud es la tabla puente depurada: su nombre es la clave de match y
    su medico_id es el mismo id que usa la tabla medicos."""
    from modules.personal_salud.models import PersonalSaludModel

    personal = db.query(PersonalSaludModel).all()
    mapa = {}
    for p in personal:
        clave = p.nombre.strip().lower()
        if clave:
            mapa[clave] = (p.id, p.medico_id, p.especialidad_id)
    return mapa


def _resolver_personal_salud(mapa: dict, nombre: str) -> tuple | None:
    """Resuelve un nombre de personal_salud contra el mapa puente.
    Devuelve (personal_salud_id, medico_id, especialidad_id) o None.
    Match exacto primero; si no, match por subcadena bidireccional."""
    if not nombre:
        return None
    clave = nombre.strip().lower()
    directo = mapa.get(clave)
    if directo:
        return directo
    for ps_clave, valores in mapa.items():
        if ps_clave in clave or clave in ps_clave:
            return valores
    return None


def _idf_personal_salud(mapa: dict) -> dict:
    """IDF sobre el corpus de nombres de personal_salud: pondera las
    características (tokens/apellidos) que discriminan entre personas."""
    return idf_por_token([tokenizar(n) for n in mapa])


def _resolver_personal_salud_vectorizado(
    mapa: dict, idf: dict, nombre: str, umbral_auto: float = CONFIANZA_ALTA
) -> dict | None:
    """Resuelve personal_salud con lógica vectorial.

    - Match exacto normalizado (títulos/sinónimos/acentos absorbidos) → 1.0.
    - Si no, similitud vectorial ponderada por IDF sobre TODOS los tokens del
      nombre (no solo el primero), y se devuelve la confianza EXPLÍCITA.
    - 'asociar' es True solo cuando la confianza supera el umbral: nunca se
      convierte una similitud baja en una certeza (el reporte lo deja visible).
    Devuelve dict con id/medico_id/especialidad_id/confianza/nivel/asociar
    o None si el nombre no tiene candidatos."""
    if not nombre:
        return None
    directo = mapa.get(nombre.strip().lower())
    if directo:
        return {
            "id": directo[0], "medico_id": directo[1], "especialidad_id": directo[2],
            "candidato": nombre, "confianza": 1.0, "nivel": "exacto", "asociar": True,
        }
    resultado = mejor_candidato(nombre, list(mapa.keys()), idf=idf, umbral=umbral_auto)
    if not resultado:
        return None
    valores = mapa.get(resultado["candidato"])
    if not valores:
        return None
    confianza = resultado["confianza"]
    return {
        "id": valores[0], "medico_id": valores[1], "especialidad_id": valores[2],
        "candidato": resultado["candidato"], "score": resultado["score"],
        "confianza": confianza, "nivel": resultado["nivel"],
        "asociar": confianza >= umbral_auto,
    }


def _personal_salud_baja_confianza(mapa: dict, idf: dict, registros) -> list[dict]:
    """Nombres con candidato vectorial por DEBAJO del umbral de certeza
    (similitud media): se exponen para revisión, no se asocian solos."""
    por_nombre: dict[str, dict] = {}
    for reg in registros:
        r = _resolver_personal_salud_vectorizado(mapa, idf, reg.personal_salud)
        if r is None or r.get("asociar"):
            continue
        item = por_nombre.setdefault(reg.personal_salud, {
            "nombre": reg.personal_salud, "total": 0,
            "candidato": r.get("candidato"), "confianza": r.get("confianza"), "nivel": r.get("nivel"),
        })
        item["total"] += 1
    return sorted(por_nombre.values(), key=lambda d: -d["total"])[:500]


_UMBRAL_SUBMATCH = 0.82
_MARCAS_PARENTESCO = ("HO/", "H/", "HIJO", "HIJA", "R.N", "RN-", "RECIEN", "NB")

# ── Modelo de decisión por evidencia combinada (record linkage, Fellegi-Sunter) ──
# Ningún campo basta por sí solo. Cada campo comparable aporta una evidencia
# proporcional a su poder discriminante y la decisión se toma sobre la suma,
# en tres zonas. Regla de oro: minimizar falsos positivos (más barato revisar
# un caso dudoso que fusionar dos identidades).
PESO_EXPEDIENTE_COINCIDE = 0.80   # igualar el número de historia equiv. a identidad casi segura
CASTIGO_EXPEDIENTE_DIFIERE = -0.15  # el expediente de SIGSA-3 puede estar desactualizado: castigo suave
PESO_SEXO_COINCIDE = 0.15          # campo común: coindicir apoya poco, pero apoya
CASTIGO_SEXO_CONFLICTO = -0.50     # sexo divergente: evidencia en contra (madre/hijo, homónimos)
ZONA_MATCH = 0.85                  # score ≥ 0.85 → match automático
ZONA_REVISION = 0.70               # 0.70 ≤ score < 0.85 → zona gris, revisión humana


def _evidencia_expediente(no_historia: str, expediente: str) -> float:
    """Igualdad exacta (normalizada) de número de historia: la evidencia más
    fuerte disponible. NO coincidir penaliza poco, porque el número en SIGSA-3
    está desactualizado (decisión de negocio documentada)."""
    if not no_historia or not expediente:
        return 0.0
    a = str(no_historia).strip().lower()
    b = str(expediente).strip().lower()
    return PESO_EXPEDIENTE_COINCIDE if a == b else CASTIGO_EXPEDIENTE_DIFIERE


def _evidencia_sexo(sexo_sig: str, sexo_pac: str) -> float:
    if not sexo_sig or not sexo_pac:
        return 0.0
    return PESO_SEXO_COINCIDE if sexo_sig == sexo_pac else CASTIGO_SEXO_CONFLICTO


def _score_combinado(nombre_sim: float, no_historia: str, expediente: str,
                     sexo_sig: str, sexo_pac: str) -> float:
    """Score único = similitud de nombre + evidencia de historia + evidencia de
    sexo, acotado a [0, 1]. El nombre se mide contra candidatos únicos con el
    sesgo de que el expediente desactualizado no lo bloquea."""
    total = nombre_sim + _evidencia_expediente(no_historia, expediente) + _evidencia_sexo(sexo_sig, sexo_pac)
    return max(0.0, min(1.0, total))


def _zona_decision(score: float) -> str:
    if score >= ZONA_MATCH:
        return "match"
    if score >= ZONA_REVISION:
        return "revision"
    return "no_match"


def _es_relacion_familiar(nombre_a: str, nombre_b: str) -> bool:
    """True si un nombre lleva marca de parentesco ('HIJO/HIJA DE …', 'HO/…',
    'R.N …') y el otro no: son personas distintas (madre vs recién nacido)."""
    def kin(nombre: str) -> bool:
        alto = nombre.strip().upper()
        if alto.startswith(_MARCAS_PARENTESCO):
            return True
        return any(t in _MARCAS_PARENTESCO for t in tokenizar(nombre))
    return kin(nombre_a) != kin(nombre_b)


def _asociar_pacientes_por_nombre_vectorial(df_sigsa, df_pacientes):
    """Devuelve (asociaciones, revision).

    Record linkage SIGSA-3 → pacientes, discriminando por evidencia combinada:
    1. Normalización (tokenización/idf) y bloqueo por firma de tokens.
    2. Identidad exacta: un único paciente → match (aunque el sexo discrepe, se
       reporta para corregir el dato).
    3. Homónimo exacto (2+ pacientes): se desambigua por número de historia
       exacto o por sexo; si quedan varios → zona gris (reportado, y se marca
       como posible duplicado de pacientes).
    4. Submatch por apellido de casada/abreviado (firma ⊆ paciente o
       paciente ⊆ firma, diferencia de 1-2 tokens): candidato único con
       score combinado ≥ zona match → asocia, aunque el expediente de
       SIGSA-3 esté desactualizado.
    5. Excluye coincidencias de parentesco (HIJO/HIJA/HO/) y todo caso dudoso
       se enumera en 'revision' para revisión humana (zona gris/minimizar FP).
    """
    from collections import defaultdict

    por_sign: dict[tuple, list] = defaultdict(list)   # firma -> [(pid, nombre, sexo, exp)]
    sig_con_token: dict[str, set] = defaultdict(set)   # token -> firmas que lo contienen
    corpus = []
    for _, paciente in df_pacientes.iterrows():
        nombre = paciente.get("nombre_completo")
        if not isinstance(nombre, str) or not nombre.strip():
            continue
        firma = tuple(sorted(tokenizar(nombre)))
        if not firma:
            continue
        sexo = paciente.get("sexo")
        sexo = sexo.strip().upper() if isinstance(sexo, str) else ""
        expo = paciente.get("expediente")
        expo = str(expo).strip().lower() if expo is not None and str(expo).strip() else ""
        estado = paciente.get("estado")
        estado = estado.strip().upper() if isinstance(estado, str) else ""
        por_sign[firma].append((int(paciente["pac_id"]), nombre, sexo, expo, estado))
        for token in set(firma):
            sig_con_token[token].add(firma)
        corpus.append(firma)
    idf = idf_por_token(corpus)
    perfiles: dict[str, tuple] = {}

    asociaciones: dict[int, int] = {}
    revision: list[dict] = []

    def _perfil(nombre):
        perfil = perfiles.get(nombre)
        if perfil is None:
            perfil = (tokenizar(nombre), pesado_por_idf(tokenizar(nombre), idf))
            perfiles[nombre] = perfil
        return perfil

    def _ficha(rid, **campos):
        campos.setdefault("sigsa3_id", rid)
        revision.append(campos)

    pendientes = df_sigsa[
        df_sigsa["paciente_id"].isna() & df_sigsa["nombre_paciente"].notna()
    ]
    for _, registro in pendientes.iterrows():
        nombre_sigsa = registro["nombre_paciente"]
        tokens = tokenizar(nombre_sigsa)
        if len(tokens) < 2:
            continue
        firma = tuple(sorted(tokens))
        sexo_sigsa = registro.get("sexo")
        sexo_sigsa = sexo_sigsa.strip().upper() if isinstance(sexo_sigsa, str) else ""
        nh = registro.get("no_historia_clinica")
        no_historia = str(nh).strip().lower() if nh is not None and str(nh).strip() else ""
        rid = int(registro["id"])

        ident = por_sign[firma]

        if len(ident) == 1:
            pid, nombre, sexo_pac, exp_pac, _estado_pac = ident[0]
            if sexo_sigsa and sexo_pac and sexo_sigsa != sexo_pac:
                _ficha(rid, tipo="sexo_discrepante", nombre_sigsa=nombre_sigsa,
                       sexo_sigsa=sexo_sigsa, nombre_paciente=nombre,
                       sexo_paciente=sexo_pac)
            asociaciones[rid] = pid
            continue

        if len(ident) > 1:
            por_hist = [c for c in ident if _evidencia_expediente(no_historia, c[3]) == PESO_EXPEDIENTE_COINCIDE]
            if len(por_hist) == 1:
                asociaciones[rid] = por_hist[0][0]
                continue
            por_estado = [c for c in ident if c[4] in ("V", "F")]
            if len(por_estado) == 1:
                asociaciones[rid] = por_estado[0][0]
                continue
            por_sex = [c for c in ident if not sexo_sigsa or not c[2] or sexo_sigsa == c[2]]
            por_sex = [c for c in por_sex if c[4] in ("V", "F")] or por_sex
            if len(por_sex) == 1:
                asociaciones[rid] = por_sex[0][0]
                continue
            _ficha(rid, tipo="homonimo", nombre_sigsa=nombre_sigsa,
                   sexo_sigsa=sexo_sigsa,
                   pacientes=sorted({c[1] for c in ident if c[4] in ("V", "F")}))
            continue

        sigs_cand = None
        for token in set(firma):
            s = sig_con_token[token]
            sigs_cand = s if sigs_cand is None else (sigs_cand & s)
        if not sigs_cand:
            # Dirección inversa: el registro trae tokens que el paciente no
            # (p.ej. apellido de casada 'DE LEÓN' solo en SIGSA-3). Busca firmas
            # contenidas en la firma del registro, partiendo del token más raro
            # para no barrer todo el corpus.
            raro = min(set(firma), key=lambda t: idf.get(t, 1.0))
            sigs_cand = {
                key for key in sig_con_token[raro]
                if len(key) < len(firma) <= len(key) + 2 and set(key) < set(firma)
            }
        if not sigs_cand:
            continue
        candidatos = []
        for key in sigs_cand:
            dif = len(key) - len(firma)
            if dif == 0 or abs(dif) > 2:
                continue
            if not (set(firma) <= set(key) or set(key) <= set(firma)):
                continue
            candidatos.extend(por_sign[key])
        by_nombre: dict[str, set] = defaultdict(set)  # nombre -> set(pid)
        for pid, nombre, sexo, expo, _est in candidatos:
            by_nombre[nombre].add(pid)
        unicos = [n for n, ids in by_nombre.items() if len(ids) == 1]
        unicos = [n for n in unicos if not _es_relacion_familiar(nombre_sigsa, n)]
        if not unicos:
            continue
        pesos = pesado_por_idf(tokens, idf)
        puntuados = []
        for nombre in unicos:
            _, pesos_candidato = _perfil(nombre)
            puntuados.append((similitud_compuesta(pesos, pesos_candidato), nombre))
        puntuados.sort(reverse=True)
        mejor_score, mejor_nombre = puntuados[0]
        if len(puntuados) > 1 and puntuados[1][0] == mejor_score:
            continue
        cd = next(c for c in candidatos if c[1] == mejor_nombre)
        pid, _, sexo_pac, expo_pac, _est_pac = cd
        score = _score_combinado(mejor_score, no_historia, expo_pac, sexo_sigsa, sexo_pac)
        zona = _zona_decision(score)

        if mejor_score >= _UMBRAL_SUBMATCH or zona == "match":
            if sexo_sigsa and sexo_pac and sexo_sigsa != sexo_pac:
                _ficha(rid, tipo="sexo_discrepante", nombre_sigsa=nombre_sigsa,
                       sexo_sigsa=sexo_sigsa, nombre_paciente=mejor_nombre,
                       sexo_paciente=sexo_pac)
            asociaciones[rid] = pid
        else:
            _ficha(rid, tipo="submatch_bajo_score", nombre_sigsa=nombre_sigsa,
                   nombre_paciente=mejor_nombre, score=round(score, 3),
                   zona=zona,
                   evolucion={
                       "nombre": round(mejor_score, 3),
                       "expediente": _evidencia_expediente(no_historia, expo_pac),
                       "sexo": _evidencia_sexo(sexo_sigsa, sexo_pac),
                   })
    return asociaciones, revision


def sincronizar_sigsa3(db: Session, dry_run: bool = False) -> dict:
    """Paso 1: asocia personal_salud_id y medico_id en SIGSA-3 por nombre
    (personal_salud → personal_salud.medico_id, tabla puente depurada).
    Paso 2: actualiza especialidad_id desde personal_salud (y medicos).

    Emparejamiento con LÓGICA VECTORIAL: match exacto masivo en SQL para los
    500K+ filas; para los pocos sin medico_id se usa similitud de vectores de
    características (nombres completos tokenizados, pesos por IDF). Solo se
    asocia automáticamente cuando la confianza supera el umbral; los nombres
    con candidato pero sin certeza se reportan en personal_salud_baja_confianza
    para revisión humana (no se convierte similitud en certidumbre).

    Con dry_run=True no escribe nada: solo cuenta lo que se asociaría.
    """
    def _stats_vacios():
        return {
            "asociados": 0,
            "personal_salud_asociados": 0,
            "especialidades_actualizadas": 0,
            "sin_match": 0,
            "personal_salud_baja_confianza": [],
        }

    if dry_run:
        # Match exacto: cuántos se asociarían (SELECT, sin escribir)
        exactos = db.execute(
            text("""
                SELECT COUNT(*)
                FROM sigsa3 s
                JOIN personal_salud ps
                  ON LOWER(TRIM(s.personal_salud)) = LOWER(TRIM(ps.nombre))
                WHERE s.personal_salud IS NOT NULL
            """)
        ).scalar()
        sin_medico = db.query(Sigsa3Model).filter(
            Sigsa3Model.personal_salud.isnot(None),
            Sigsa3Model.medico_id.is_(None),
        ).count()
        mapa = _build_personal_salud_map(db)
        idf = _idf_personal_salud(mapa)
        fuzzy = 0
        sin_match = 0
        registros_sin_medico = db.query(Sigsa3Model).filter(
            Sigsa3Model.personal_salud.isnot(None),
            Sigsa3Model.medico_id.is_(None),
        ).all()
        for reg in registros_sin_medico:
            match = _resolver_personal_salud_vectorizado(mapa, idf, reg.personal_salud)
            if match is None:
                sin_match += 1
            elif match.get("asociar"):
                fuzzy += 1
        return {
            "asociados": int(sin_medico or 0),
            "personal_salud_asociados": int(exactos or 0) + fuzzy,
            "especialidades_actualizadas": int(exactos or 0) + fuzzy,
            "sin_match": sin_match,
            "personal_salud_sin_match": _personal_salud_sin_match(db),
            "personal_salud_baja_confianza": _personal_salud_baja_confianza(mapa, idf, registros_sin_medico),
            "modo": "dry_run",
        }

    registros = db.query(Sigsa3Model).filter(
        Sigsa3Model.personal_salud.isnot(None),
    ).all()
    if not registros:
        return _stats_vacios()

    # ── Paso masivo en SQL (match exacto) para los ~500K con nombre ──
    # personal_salud.nombre es la clave depurada; su medico_id es el id de medicos.
    res = db.execute(
        text("""
            UPDATE sigsa3 s
            SET personal_salud_id = ps.id,
                medico_id = COALESCE(s.medico_id, ps.medico_id),
                especialidad_id = COALESCE(s.especialidad_id, ps.especialidad_id)
            FROM personal_salud ps
            WHERE LOWER(TRIM(s.personal_salud)) = LOWER(TRIM(ps.nombre))
              AND s.personal_salud IS NOT NULL
              AND (s.personal_salud_id IS DISTINCT FROM ps.id
                   OR s.medico_id IS DISTINCT FROM COALESCE(s.medico_id, ps.medico_id)
                   OR s.especialidad_id IS DISTINCT FROM COALESCE(s.especialidad_id, ps.especialidad_id))
        """)
    ).rowcount
    db.commit()
    personal_salud_asociados = int(res or 0)

    # ── Barrido vectorial solo para los sin medico_id (pocos, ~2K) ──
    mapa = _build_personal_salud_map(db)
    idf = _idf_personal_salud(mapa)
    asociados = 0
    especialidades_actualizadas = 0
    sin_match = 0
    registros_sin_medico = db.query(Sigsa3Model).filter(
        Sigsa3Model.personal_salud.isnot(None),
        Sigsa3Model.medico_id.is_(None),
    ).all()
    for reg in registros_sin_medico:
        match = _resolver_personal_salud_vectorizado(mapa, idf, reg.personal_salud)
        if match is None:
            sin_match += 1
            continue
        if not match.get("asociar"):
            continue  # candidato sin certeza: se reporta, no se asocia
        ps_id = match["id"]
        medico_id = match["medico_id"]
        personal_esp_id = match["especialidad_id"]
        if ps_id is not None and reg.personal_salud_id != ps_id:
            reg.personal_salud_id = ps_id
        if medico_id is not None and reg.medico_id != medico_id:
            reg.medico_id = medico_id
            asociados += 1
        if personal_esp_id and reg.especialidad_id != personal_esp_id:
            reg.especialidad_id = personal_esp_id
            especialidades_actualizadas += 1

    db.commit()
    return {
        "asociados": asociados,
        "personal_salud_asociados": personal_salud_asociados,
        "especialidades_actualizadas": especialidades_actualizadas,
        "sin_match": sin_match,
        "personal_salud_sin_match": _personal_salud_sin_match(db),
        "personal_salud_baja_confianza": _personal_salud_baja_confianza(mapa, idf, registros_sin_medico),
    }


def asociar_paciente_y_consulta(db: Session):
    """Ejecuta el pipeline en exclusión mutua para evitar asociaciones
    concurrentes sobre los mismos registros SIGSA-3."""
    bloqueado = db.execute(
        text("SELECT pg_try_advisory_lock(hashtext('sigsa3_asociar_pacientes_masivo'))")
    ).scalar()
    if not bloqueado:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya hay una asociación masiva SIGSA-3 en ejecución",
        )
    try:
        yield from _asociar_paciente_y_consulta_pipeline(db)
    finally:
        db.execute(text("SELECT pg_advisory_unlock(hashtext('sigsa3_asociar_pacientes_masivo'))"))


def _asociar_paciente_y_consulta_pipeline(db: Session):
    """Pipeline completo usando pandas para asociación masiva.
    Generador que yield eventos de progreso como dicts.
    1. nombre_paciente = nombre_completo AND no_historia_clinica = expediente → paciente_id
    2. no_historia_clinica = expediente (tipo 1/2) o = documento + fecha (tipo 3) → paciente_id / consulta_id
    3. nombre_paciente vs nombre_completo: similitud vectorial con umbral alto
       y margen frente al segundo candidato → paciente_id
    4. paciente_id + fecha ±1d + tipo coincidente → consulta_id
    5. no_historia_clinica = documento + fecha ±1d → consulta_id (+ paciente_id si faltaba)
    6a. paciente_id + fecha ±1d (cualquier tipo) → consulta_id (rezagados)
    6b. reservado para revisión humana: no se autoasocian nombres ambiguos.
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
        "SELECT id, nombre_paciente, no_historia_clinica, fecha_consulta, tipo_consulta, sexo, paciente_id, consulta_id FROM sigsa3 WHERE paciente_id IS NULL OR consulta_id IS NULL",
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
        "SELECT id AS pac_id, nombre_completo, expediente, sexo, estado FROM pacientes WHERE nombre_completo IS NOT NULL",
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
        "SELECT id, nombre_paciente, no_historia_clinica, fecha_consulta, tipo_consulta, sexo, paciente_id, consulta_id FROM sigsa3 WHERE paciente_id IS NULL OR consulta_id IS NULL",
        engine, parse_dates=["fecha_consulta"]
    )

    # ── PASO 3: nombre vectorial; solo candidatos inequívocos ──
    paso3, revision = _asociar_pacientes_por_nombre_vectorial(df, df_pac)
    for rid, pid in paso3.items():
        updates_paciente[rid] = pid
        df.loc[df["id"] == rid, "paciente_id"] = pid
        resultados["paso3_paciente"] += 1
    _aplicar_updates()
    aviso3 = ""
    if revision:
        por_tipo: dict[str, int] = {}
        for r in revision:
            por_tipo[r.get("tipo", "?")] = por_tipo.get(r.get("tipo", "?"), 0) + 1
        detalle = " | ".join(f"{k}: {v}" for k, v in por_tipo.items())
        ejemplos = revision[:2]
        aviso3 = (
            f"⚠️ {len(revision)} pendientes para revisar ({detalle}). "
            f"Expediente desactualizado o nombre ambiguo; ej: {ejemplos}. "
            f"Los homónimos exactos suelen ser pacientes duplicados (merge)."
        )
        print(f"[PIPELINE] {aviso3}")
    yield {"step": "paso3", "progress": 55, "message": f"Paso 3 — nombre vectorial inequívoco: {resultados['paso3_paciente']} pacientes", "aviso": aviso3, **resultados}

    # ── PASO 3b: tolerancia a typos en apellido (último recurso) ──
    # Solo para registros que siguen sin paciente_id tras paso 3.
    # Requiere: nombre de pila EXACTO, apellido con typo tolerado, y corroboración
    # por expediente o sexo para auto-asociar; si no hay corroboración -> revisión.
    from modules.common.similitud_fonetica import intentar_match_por_typo
    mask_typo = df["paciente_id"].isna() & df["nombre_paciente"].notna()
    paso3b_count = 0
    paso3b_revision = 0
    if mask_typo.any() and not df_pac.empty:
        # Preparar candidatos: lista de tuplas (pid, nombre_completo, sexo, expediente, estado)
        candidatos = []
        for _, pac in df_pac.iterrows():
            nombre = pac.get("nombre_completo")
            if not isinstance(nombre, str) or not nombre.strip():
                continue
            sexo = pac.get("sexo")
            sexo = sexo.strip().upper() if isinstance(sexo, str) else ""
            expo = pac.get("expediente")
            expo = str(expo).strip().lower() if expo is not None and str(expo).strip() else ""
            estado = pac.get("estado")
            estado = estado.strip().upper() if isinstance(estado, str) else ""
            candidatos.append((int(pac["pac_id"]), nombre, sexo, expo, estado))

        for _, reg in df.loc[mask_typo].iterrows():
            rid = int(reg["id"])
            nombre_sigsa = reg["nombre_paciente"]
            nh = reg.get("no_historia_clinica")
            no_historia = str(nh).strip().lower() if nh is not None and str(nh).strip() else ""
            sexo_sigsa = reg.get("sexo")
            sexo_sigsa = sexo_sigsa.strip().upper() if isinstance(sexo_sigsa, str) else ""

            pid, motivo = intentar_match_por_typo(nombre_sigsa, candidatos, no_historia, sexo_sigsa, tokenizar)
            if pid and motivo == "typo_corroborado":
                updates_paciente[rid] = pid
                df.loc[df["id"] == rid, "paciente_id"] = pid
                paso3b_count += 1
            elif motivo:
                paso3b_revision += 1
                # La ficha ya tiene tipo "typo_sin_corroborar" o "typo_probable_ambiguo"
                # La agregamos a revision global (se procesa después del paso 4)
                pass  # en dry_run o logging se vería; aquí solo contamos

    _aplicar_updates()
    yield {"step": "paso3b", "progress": 58, "message": f"Paso 3b — typo apellido corroborado: {paso3b_count} pacientes, {paso3b_revision} a revisión", **resultados}

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

    yield {"step": "paso6b", "progress": 95, "message": "Paso 6b — nombres ambiguos pendientes de revisión", **resultados}

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


def _normalizar_equal(codigo: str) -> str:
    """Solo alfanuméricos en mayúsculas, para comparar códigos ignorando puntuación."""
    return "".join(ch for ch in codigo.upper() if ch.isalnum())


def dx_por_codigo_cie(db: Session, desde: str, hasta: str, codigos: list[str]) -> dict:
    """Diagnósticos (Z:34, Z:10, ...) basados en sigsa3_registros (normalizado).

    Fuente: sigsa3_registros.codigo_cie_10_id → cie10_catalogo.codigo.
    Se comparan los códigos ignorando puntuación, de modo que Z:10:4, Z10.4 y Z104
    del catálogo colapsan a la misma fila normalizada."""
    f_desde, f_hasta = _parse_fechas(desde, hasta)

    estandares = []
    for c in codigos:
        est = _normalizar_codigo_cie10(c)
        if est and est not in estandares:
            estandares.append(est)
    if not estandares:
        raise HTTPException(status_code=400, detail="No se especificaron códigos CIE-10")

    display_por_norm = {_normalizar_equal(nb): nb for nb in estandares}

    placeholders = ", ".join(f":n{i}" for i in range(len(estandares)))
    params: dict = {"desde": f_desde, "hasta": f_hasta}
    for i, e in enumerate(estandares):
        params[f"n{i}"] = _normalizar_equal(e)

    rows = db.execute(text(f"""
        SELECT
            COALESCE(tc.nombre, '—') AS tipo_consulta,
            REGEXP_REPLACE(UPPER(COALESCE(c.codigo, '')), '[^A-Z0-9]', '', 'g') AS norm_code,
            COUNT(*) AS total,
            COUNT(DISTINCT r.paciente_id) AS pacientes
        FROM sigsa3_registros r
        LEFT JOIN cie10_catalogo c ON c.id = r.codigo_cie_10_id
        LEFT JOIN tipos_consulta_sigsa3 tc ON tc.id = r.tipo_consulta_id
        WHERE r.fecha_consulta BETWEEN :desde AND :hasta
          AND c.codigo IS NOT NULL
          AND c.codigo <> ''
          AND REGEXP_REPLACE(UPPER(c.codigo), '[^A-Z0-9]', '', 'g') IN ({placeholders})
        GROUP BY tc.nombre, norm_code
        ORDER BY norm_code, total DESC
    """), params).fetchall()

    total_pacientes = db.execute(text(f"""
        SELECT COUNT(DISTINCT r.paciente_id) AS total
        FROM sigsa3_registros r
        LEFT JOIN cie10_catalogo c ON c.id = r.codigo_cie_10_id
        WHERE r.fecha_consulta BETWEEN :desde AND :hasta
          AND c.codigo IS NOT NULL
          AND c.codigo <> ''
          AND REGEXP_REPLACE(UPPER(c.codigo), '[^A-Z0-9]', '', 'g') IN ({placeholders})
    """), params).scalar()

    datos = []
    total_general = 0
    for r in rows:
        m = r._mapping
        t = int(m["total"])
        total_general += t
        datos.append({
            "tipo_consulta": str(m["tipo_consulta"]),
            "codigo_cie_10": display_por_norm.get(str(m["norm_code"]), str(m["norm_code"])),
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
    db.execute(text("TRUNCATE TABLE sigsa3_registros RESTART IDENTITY CASCADE"))
    db.commit()
    return {"truncado": True, "tabla": "sigsa3", "tabla_normalizada": "sigsa3_registros"}


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
        "semana_gestacional", "codigo_cie_10", "dx", "especialidad_nombre",
    ]
    writer.writerow(columns)
    for r in registros:
        writer.writerow([
            r.id, r.paciente_id, r.medico_id, r.consulta_id, r.personal_salud,
            r.fecha_consulta, r.no_historia_clinica, r.nombre_paciente, r.sexo,
            r.edad_dias, r.edad_meses, r.edad_anios, r.tipo_consulta, r.control,
            r.semana_gestacional, r.codigo_cie_10, r.dx, r.especialidad_nombre,
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
    """Convierte código CIE-10 del formato SIGSA-3 (Z:34, O:82:9) al formato del catálogo (Z34, O829).

    El catálogo cie10_catalogo guarda los códigos SIN punto ni dos puntos (O829), así que
    aquí solo se elimina la puntuación (:, ., espacios) y se normaliza a mayúsculas."""
    if not codigo:
        return ""
    return "".join(ch for ch in codigo.strip().upper() if ch.isalnum())


def _resolver_cie10_id(db: Session, codigo_sigsa3: str, cie10_cache: dict) -> int | None:
    """Resuelve código CIE-10 string → FK a cie10_catalogo.id usando caché en memoria."""
    if not codigo_sigsa3:
        return None
    if codigo_sigsa3 in cie10_cache:
        return cie10_cache[codigo_sigsa3]
    estandar = _normalizar_codigo_cie10(codigo_sigsa3)
    if estandar in cie10_cache:
        return cie10_cache[estandar]
    # Buscar en DB (compara el código normalizado sin puntuación, igual al formato del catálogo)
    row = db.execute(
        text("SELECT id FROM cie10_catalogo WHERE codigo = :e LIMIT 1"),
        {"e": estandar},
    ).first()
    if row:
        cid = row[0]
        cie10_cache[codigo_sigsa3] = cid
        cie10_cache[estandar] = cid
        return cid
    cie10_cache[codigo_sigsa3] = None
    cie10_cache[estandar] = None
    return None


def _resolver_cie10_o_crear(db: Session, codigo_sigsa3: str, cie10_cache: dict) -> int | None:
    """Resuelve código CIE-10 string → FK a cie10_catalogo.id.

    Igual que _resolver_cie10_id pero si el código normalizado NO existe en el
    catálogo, lo CREA (fuente SIGSA-3) para que sigsa3_registros siempre conserve
    el código y el diagnóstico sea recuperable a través de él. La descripción se
    deja como el propio código hasta que se complete en el catálogo."""
    if not codigo_sigsa3:
        return None
    estandar = _normalizar_codigo_cie10(codigo_sigsa3)
    if not estandar:
        return None
    if codigo_sigsa3 in cie10_cache:
        return cie10_cache[codigo_sigsa3]
    if estandar in cie10_cache:
        return cie10_cache[estandar]

    row = db.execute(
        text("SELECT id FROM cie10_catalogo WHERE codigo = :e LIMIT 1"),
        {"e": estandar},
    ).first()
    if row:
        cid = row[0]
        cie10_cache[codigo_sigsa3] = cid
        cie10_cache[estandar] = cid
        return cid

    # No existe: crear entrada normalizada para que el FK nunca quede vacío.
    db.execute(
        text("""
            INSERT INTO cie10_catalogo (codigo, descripcion, nivel, fuente)
            VALUES (:e, :e, 0, 'sigsa3_auto')
            ON CONFLICT (codigo) DO NOTHING
        """),
        {"e": estandar},
    )
    db.commit()
    row = db.execute(
        text("SELECT id FROM cie10_catalogo WHERE codigo = :e LIMIT 1"),
        {"e": estandar},
    ).first()
    cid = row[0] if row else None
    cie10_cache[codigo_sigsa3] = cid
    cie10_cache[estandar] = cid
    return cid


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
    """Resuelve tipo_consulta string ('1 Primera', '4 Interconsulta') → id.

    Categorías SIGSA-3: 1 Primeras, 2 Reconsultas, 3 Emergencia, 4 Interconsultas.
    Devuelve el número de la categoría (1-4), o None si no es reconocible."""
    if not tipo_str:
        return None
    t = tipo_str.strip()
    num = t.split()[0] if " " in t else t
    try:
        n = int(num)
        if n in (1, 2, 3, 4):
            return n
    except ValueError:
        return None
    return None


def _stats_staging(db: Session) -> dict:
    """Conteos de staging para el reporte: pendientes, omitidos y huérfanos."""
    pendientes_sin_paciente = db.query(Sigsa3Model).filter(
        Sigsa3Model.paciente_id.is_(None)
    ).count()
    omitidos_sin_medico = db.query(Sigsa3Model).filter(
        Sigsa3Model.paciente_id.isnot(None),
        Sigsa3Model.paciente_id != 0,
        Sigsa3Model.medico_id.is_(None),
    ).count()
    return {
        "omitidos_sin_medico": omitidos_sin_medico,
        "pendientes_sin_paciente": pendientes_sin_paciente,
    }


def _personal_salud_sin_match(db: Session) -> list[dict]:
    """Nombres de personal_salud de staging que NO encontraron coincidencia
    (ni médico ni personal_salud), con su conteo. Agrupado y ordenado."""
    rows = db.execute(
        text("""
            SELECT personal_salud AS nombre, COUNT(*) AS total
            FROM sigsa3
            WHERE personal_salud IS NOT NULL
              AND personal_salud <> ''
              AND personal_salud_id IS NULL
              AND medico_id IS NULL
            GROUP BY personal_salud
            ORDER BY total DESC, nombre
            LIMIT 500
        """)
    ).fetchall()
    return [{"nombre": r[0], "total": r[1]} for r in rows]


def normalizar(db: Session, batch_size: int = 1000, dry_run: bool = False,
             ids: list[int] | None = None, max_registros: int | None = None) -> dict:
    """Migra registros de sigsa3 (staging) a sigsa3_registros (normalizado).

    - Solo migra registros con paciente_id + medico_id (ambos obligatorios).
      consulta_id es opcional.
    - Copia sigsa3_id (id del staging) en sigsa3_registros para trazabilidad.
    - NO borra en línea: al final purga de sigsa3 los id migrados (los que
      tienen sigsa3_id en sigsa3_registros). En staging solo quedan huérfanos.
    - Reporta los nombres de personal_salud sin coincidencia.

    - ids: si se pasa, migra SOLO esos registros staging (útil para pruebas
      puntuales o re-procesar casos concretos).
    - max_registros: tope máximo de registros a migrar en esta corrida
      (para tandas incrementales controladas).
    - Con dry_run=True solo cuenta y reporta, sin escribir ni borrar nada.

    ⚠️ No invocar dos veces en paralelo sobre la misma BD: la normalización
    masiva tarda y no tiene bloqueo de concurrencia.
    """
    cie10_cache = {}
    esp_cache = {}

    base_filter = [
        Sigsa3Model.paciente_id.isnot(None),
        Sigsa3Model.paciente_id != 0,
        Sigsa3Model.medico_id.isnot(None),
        Sigsa3Model.medico_id != 0,
    ]
    if ids:
        base_filter.append(Sigsa3Model.id.in_(ids))

    if dry_run:
        q = db.query(Sigsa3Model).filter(*base_filter)
        migrables = q.count()
        stats = _stats_staging(db)
        if ids:
            # En dry_run con ids, el conteo es el de esos ids
            stats = {
                "omitidos_sin_medico": 0,
                "pendientes_sin_paciente": 0,
            }
        return {
            "modo": "dry_run",
            "migrarian": migrables,
            **stats,
            "resoluciones": {
                "tipo_consulta_resuelto": 0,
                "cie10_existente": 0,
                "cie10_creado_auto": 0,
                "cie10_pendiente": 0,
            },
            "personal_salud_sin_match": _personal_salud_sin_match(db),
            "errores": 0,
        }

    total_migrados = 0
    total_errores = 0
    res_tipo = 0
    res_cie10_existente = 0
    res_cie10_creado = 0
    res_cie10_pendiente = 0

    def _resoluciones():
        return {
            "tipo_consulta_resuelto": res_tipo,
            "cie10_existente": res_cie10_existente,
            "cie10_creado_auto": res_cie10_creado,
            "cie10_pendiente": res_cie10_pendiente,
        }

    while True:
        query = (
            db.query(Sigsa3Model)
            .filter(*base_filter)
            .order_by(Sigsa3Model.id)
            .limit(batch_size)
        )
        registros = query.all()
        if not registros:
            break

        lote_ids = []  # sigsa3_id de los migrados en este lote (rastro de purga)
        for reg in registros:
            try:
                tipo_id = _resolver_tipo_consulta_id(reg.tipo_consulta) or reg.tipo_consulta_id
                if tipo_id is not None:
                    res_tipo += 1
                codigo_str = reg.codigo_cie_10
                if codigo_str and not reg.codigo_cie_10_id:
                    estandar = _normalizar_codigo_cie10(codigo_str)
                    existia = estandar in cie10_cache and cie10_cache.get(estandar) is not None
                else:
                    existia = True
                cie10_id = reg.codigo_cie_10_id or _resolver_cie10_o_crear(db, codigo_str, cie10_cache)
                if cie10_id is not None:
                    if existia:
                        res_cie10_existente += 1
                    else:
                        res_cie10_creado += 1
                else:
                    res_cie10_pendiente += 1
                esp_id = reg.especialidad_id

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
                    sigsa3_id=reg.id,
                )
                db.add(nuevo)
                db.flush()
                lote_ids.append(reg.id)
                total_migrados += 1
                if max_registros is not None and total_migrados >= max_registros:
                    break
            except Exception:
                total_errores += 1
                continue

        db.commit()

        # Purga incremental del lote: borrar de staging los id migrados
        # (rastreados por sigsa3_id en sigsa3_registros). Esto evita que el
        # bucle re-seleccione los mismos registros (loop infinito).
        if lote_ids:
            db.execute(
                text("DELETE FROM sigsa3 s WHERE s.id = ANY(:ids)"),
                {"ids": lote_ids},
            )
            db.commit()

        if max_registros is not None and total_migrados >= max_registros:
            break

    stats = _stats_staging(db)
    return {
        "modo": "real",
        "migrados": total_migrados,
        "purgeados_de_staging": total_migrados,
        **stats,
        "resoluciones": _resoluciones(),
        "personal_salud_sin_match": _personal_salud_sin_match(db),
        "errores": total_errores,
    }
