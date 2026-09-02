from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from decimal import Decimal

from modules.variables.models import (
    VhHospitalModel, VhDepartmentModel, VhMonthModel, VhGenderModel,
    VhVariableCategoryModel, VhVariableModel, VhMeasurementModel,
)
from modules.variables.schemas import (
    CategoryCreate, CategoryUpdate, VariableCreate, VariableUpdate,
    MeasurementCreate, MeasurementUpdate, MeasurementBulkItem,
)


# ── Categories ──

def listar_categorias(db: Session, q: Optional[str] = None, skip: int = 0, limit: int = 200) -> tuple[list[dict], int]:
    query = db.query(VhVariableCategoryModel)
    if q:
        query = query.filter(func.unaccent(VhVariableCategoryModel.category_name).ilike(f"%{q}%"))
    total = query.count()
    cats = query.order_by(VhVariableCategoryModel.category_name).offset(skip).limit(limit).all()
    result = []
    for c in cats:
        var_count = db.query(func.count(VhVariableModel.variable_id)).filter(VhVariableModel.category_id == c.category_id).scalar()
        result.append({
            "category_id": c.category_id,
            "category_name": c.category_name,
            "description": c.description,
            "total_variables": var_count,
            "created_at": c.created_at,
        })
    return result, total


def obtener_categoria(cat_id: int, db: Session) -> dict:
    cat = db.query(VhVariableCategoryModel).filter(VhVariableCategoryModel.category_id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    var_count = db.query(func.count(VhVariableModel.variable_id)).filter(VhVariableModel.category_id == cat.category_id).scalar()
    return {
        "category_id": cat.category_id,
        "category_name": cat.category_name,
        "description": cat.description,
        "total_variables": var_count,
        "created_at": cat.created_at,
    }


def crear_categoria(data: CategoryCreate, db: Session) -> dict:
    existe = db.query(VhVariableCategoryModel).filter(VhVariableCategoryModel.category_name == data.category_name).first()
    if existe:
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre")
    cat = VhVariableCategoryModel(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {"category_id": cat.category_id, "category_name": cat.category_name, "description": cat.description, "total_variables": 0, "created_at": cat.created_at}


def actualizar_categoria(cat_id: int, data: CategoryUpdate, db: Session) -> dict:
    cat = db.query(VhVariableCategoryModel).filter(VhVariableCategoryModel.category_id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    var_count = db.query(func.count(VhVariableModel.variable_id)).filter(VhVariableModel.category_id == cat.category_id).scalar()
    return {"category_id": cat.category_id, "category_name": cat.category_name, "description": cat.description, "total_variables": var_count, "created_at": cat.created_at}


def eliminar_categoria(cat_id: int, db: Session) -> None:
    cat = db.query(VhVariableCategoryModel).filter(VhVariableCategoryModel.category_id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    try:
        db.delete(cat)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar, tiene variables asociadas")
    return None


# ── Variables ──

def listar_variables(
    db: Session,
    category_id: Optional[int] = None,
    q: Optional[str] = None,
    data_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 200,
) -> tuple[list[dict], int]:
    query = db.query(VhVariableModel)
    if category_id:
        query = query.filter(VhVariableModel.category_id == category_id)
    if q:
        query = query.filter(
            func.unaccent(VhVariableModel.variable_name).ilike(f"%{q}%")
            | func.unaccent(VhVariableModel.variable_code).ilike(f"%{q}%")
        )
    if data_type:
        query = query.filter(VhVariableModel.data_type == data_type)
    total = query.count()
    vars_ = query.order_by(VhVariableModel.variable_name).offset(skip).limit(limit).all()
    result = []
    for v in vars_:
        cat_name = db.query(VhVariableCategoryModel.category_name).filter(VhVariableCategoryModel.category_id == v.category_id).scalar()
        result.append({
            "variable_id": v.variable_id,
            "category_id": v.category_id,
            "category_name": cat_name,
            "variable_name": v.variable_name,
            "variable_code": v.variable_code,
            "description": v.description,
            "unit_of_measure": v.unit_of_measure,
            "data_type": v.data_type,
            "is_aggregate": v.is_aggregate,
            "created_at": v.created_at,
            "updated_at": v.updated_at,
        })
    return result, total


def obtener_variable(var_id: int, db: Session) -> dict:
    var = db.query(VhVariableModel).filter(VhVariableModel.variable_id == var_id).first()
    if not var:
        raise HTTPException(status_code=404, detail="Variable no encontrada")
    cat_name = db.query(VhVariableCategoryModel.category_name).filter(VhVariableCategoryModel.category_id == var.category_id).scalar()
    return {
        "variable_id": var.variable_id,
        "category_id": var.category_id,
        "category_name": cat_name,
        "variable_name": var.variable_name,
        "variable_code": var.variable_code,
        "description": var.description,
        "unit_of_measure": var.unit_of_measure,
        "data_type": var.data_type,
        "is_aggregate": var.is_aggregate,
        "created_at": var.created_at,
        "updated_at": var.updated_at,
    }


def crear_variable(data: VariableCreate, db: Session) -> dict:
    cat = db.query(VhVariableCategoryModel).filter(VhVariableCategoryModel.category_id == data.category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    if data.variable_code:
        existe = db.query(VhVariableModel).filter(VhVariableModel.variable_code == data.variable_code).first()
        if existe:
            raise HTTPException(status_code=409, detail="Ya existe una variable con ese código")
    var = VhVariableModel(**data.model_dump())
    db.add(var)
    db.commit()
    db.refresh(var)
    return {
        "variable_id": var.variable_id, "category_id": var.category_id, "category_name": cat.category_name,
        "variable_name": var.variable_name, "variable_code": var.variable_code, "description": var.description,
        "unit_of_measure": var.unit_of_measure, "data_type": var.data_type, "is_aggregate": var.is_aggregate,
        "created_at": var.created_at, "updated_at": var.updated_at,
    }


def actualizar_variable(var_id: int, data: VariableUpdate, db: Session) -> dict:
    var = db.query(VhVariableModel).filter(VhVariableModel.variable_id == var_id).first()
    if not var:
        raise HTTPException(status_code=404, detail="Variable no encontrada")
    if data.variable_code:
        existe = db.query(VhVariableModel).filter(VhVariableModel.variable_code == data.variable_code, VhVariableModel.variable_id != var_id).first()
        if existe:
            raise HTTPException(status_code=409, detail="Ya existe otra variable con ese código")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(var, key, value)
    db.commit()
    db.refresh(var)
    cat_name = db.query(VhVariableCategoryModel.category_name).filter(VhVariableCategoryModel.category_id == var.category_id).scalar()
    return {
        "variable_id": var.variable_id, "category_id": var.category_id, "category_name": cat_name,
        "variable_name": var.variable_name, "variable_code": var.variable_code, "description": var.description,
        "unit_of_measure": var.unit_of_measure, "data_type": var.data_type, "is_aggregate": var.is_aggregate,
        "created_at": var.created_at, "updated_at": var.updated_at,
    }


def eliminar_variable(var_id: int, db: Session) -> None:
    var = db.query(VhVariableModel).filter(VhVariableModel.variable_id == var_id).first()
    if not var:
        raise HTTPException(status_code=404, detail="Variable no encontrada")
    try:
        db.delete(var)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar, tiene mediciones asociadas")
    return None


# ── Measurements ──

def _measurement_to_dict(m: VhMeasurementModel, db: Session) -> dict:
    hosp_name = db.query(VhHospitalModel.hospital_name).filter(VhHospitalModel.hospital_id == m.hospital_id).scalar()
    dept_name = db.query(VhDepartmentModel.department_name).filter(VhDepartmentModel.department_id == m.department_id).scalar()
    var_name = db.query(VhVariableModel.variable_name).filter(VhVariableModel.variable_id == m.variable_id).scalar()
    var_code = db.query(VhVariableModel.variable_code).filter(VhVariableModel.variable_id == m.variable_id).scalar()
    month_name = db.query(VhMonthModel.month_name).filter(VhMonthModel.month_id == m.month_id).scalar()
    month_number = db.query(VhMonthModel.month_number).filter(VhMonthModel.month_id == m.month_id).scalar()
    gender_name = db.query(VhGenderModel.gender_name).filter(VhGenderModel.gender_id == m.gender_id).scalar()
    return {
        "measurement_id": m.measurement_id,
        "hospital_id": m.hospital_id, "hospital_name": hosp_name,
        "department_id": m.department_id, "department_name": dept_name,
        "variable_id": m.variable_id, "variable_name": var_name, "variable_code": var_code,
        "month_id": m.month_id, "month_name": month_name, "month_number": month_number,
        "gender_id": m.gender_id, "gender_name": gender_name,
        "year": m.year, "measurement_value": m.measurement_value,
        "notes": m.notes, "is_calculated": m.is_calculated,
        "created_at": m.created_at, "updated_at": m.updated_at,
    }


def listar_mediciones(
    db: Session,
    hospital_id: Optional[int] = None,
    department_id: Optional[int] = None,
    variable_id: Optional[int] = None,
    category_id: Optional[int] = None,
    month_id: Optional[int] = None,
    gender_id: Optional[int] = None,
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 200,
) -> tuple[list[dict], int]:
    query = db.query(VhMeasurementModel)
    count_q = db.query(func.count(VhMeasurementModel.measurement_id))

    filters = []
    if hospital_id:
        filters.append(VhMeasurementModel.hospital_id == hospital_id)
    if department_id:
        filters.append(VhMeasurementModel.department_id == department_id)
    if variable_id:
        filters.append(VhMeasurementModel.variable_id == variable_id)
    if category_id:
        var_ids = db.query(VhVariableModel.variable_id).filter(VhVariableModel.category_id == category_id).subquery()
        filters.append(VhMeasurementModel.variable_id.in_(var_ids))
    if month_id:
        filters.append(VhMeasurementModel.month_id == month_id)
    if gender_id:
        filters.append(VhMeasurementModel.gender_id == gender_id)
    if year:
        filters.append(VhMeasurementModel.year == year)

    for f in filters:
        query = query.filter(f)
        count_q = count_q.filter(f)

    total = count_q.scalar()
    meds = query.order_by(VhMeasurementModel.year.desc(), VhMeasurementModel.measurement_id).offset(skip).limit(limit).all()
    return [_measurement_to_dict(m, db) for m in meds], total


def obtener_medicion(measurement_id: int, db: Session) -> dict:
    m = db.query(VhMeasurementModel).filter(VhMeasurementModel.measurement_id == measurement_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Medición no encontrada")
    return _measurement_to_dict(m, db)


def crear_medicion(data: MeasurementCreate, db: Session) -> dict:
    existe = db.query(VhMeasurementModel).filter(
        VhMeasurementModel.hospital_id == data.hospital_id,
        VhMeasurementModel.department_id == data.department_id,
        VhMeasurementModel.variable_id == data.variable_id,
        VhMeasurementModel.month_id == data.month_id,
        VhMeasurementModel.gender_id == data.gender_id,
        VhMeasurementModel.year == data.year,
    ).first()
    if existe:
        raise HTTPException(status_code=409, detail="Ya existe una medición para esa combinación hospital/departamento/variable/mes/género/año")
    m = VhMeasurementModel(**data.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return _measurement_to_dict(m, db)


def actualizar_medicion(measurement_id: int, data: MeasurementUpdate, db: Session) -> dict:
    m = db.query(VhMeasurementModel).filter(VhMeasurementModel.measurement_id == measurement_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Medición no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(m, key, value)
    db.commit()
    db.refresh(m)
    return _measurement_to_dict(m, db)


def eliminar_medicion(measurement_id: int, db: Session) -> None:
    m = db.query(VhMeasurementModel).filter(VhMeasurementModel.measurement_id == measurement_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Medición no encontrada")
    db.delete(m)
    db.commit()
    return None


def bulk_upsert(mediciones: list[MeasurementBulkItem], db: Session) -> dict:
    creados = 0
    actualizados = 0
    errores = []
    for item in mediciones:
        try:
            existe = db.query(VhMeasurementModel).filter(
                VhMeasurementModel.hospital_id == item.hospital_id,
                VhMeasurementModel.department_id == item.department_id,
                VhMeasurementModel.variable_id == item.variable_id,
                VhMeasurementModel.month_id == item.month_id,
                VhMeasurementModel.gender_id == item.gender_id,
                VhMeasurementModel.year == item.year,
            ).first()
            if existe:
                existe.measurement_value = item.measurement_value
                existe.notes = item.notes
                existe.is_calculated = item.is_calculated
                actualizados += 1
            else:
                m = VhMeasurementModel(**item.model_dump())
                db.add(m)
                creados += 1
        except Exception as e:
            errores.append({"variable_id": item.variable_id, "month_id": item.month_id, "error": str(e)})
    if creados or actualizados:
        db.commit()
    return {"creados": creados, "actualizados": actualizados, "errores": errores}


# ── Static refs ──

def listar_meses(db: Session) -> list[dict]:
    meses = db.query(VhMonthModel).order_by(VhMonthModel.month_number).all()
    return [{"month_id": m.month_id, "month_name": m.month_name, "month_number": m.month_number, "abbreviation": m.abbreviation} for m in meses]


def listar_generos(db: Session) -> list[dict]:
    gens = db.query(VhGenderModel).order_by(VhGenderModel.gender_id).all()
    return [{"gender_id": g.gender_id, "gender_name": g.gender_name, "abbreviation": g.abbreviation} for g in gens]


# ── Hospitals & Departments ──

def listar_hospitales(db: Session) -> list[dict]:
    hosp = db.query(VhHospitalModel).order_by(VhHospitalModel.hospital_name).all()
    return [{"hospital_id": h.hospital_id, "hospital_name": h.hospital_name, "hospital_type": h.hospital_type, "location": h.location} for h in hosp]


def crear_hospital(data, db: Session) -> dict:
    existe = db.query(VhHospitalModel).filter(VhHospitalModel.hospital_name == data.hospital_name).first()
    if existe:
        raise HTTPException(status_code=409, detail="Ya existe un hospital con ese nombre")
    h = VhHospitalModel(**data.model_dump())
    db.add(h)
    db.commit()
    db.refresh(h)
    return {"hospital_id": h.hospital_id, "hospital_name": h.hospital_name, "hospital_type": h.hospital_type, "location": h.location, "created_at": h.created_at}


def listar_departamentos(db: Session, hospital_id: Optional[int] = None) -> list[dict]:
    query = db.query(VhDepartmentModel)
    if hospital_id:
        query = query.filter(VhDepartmentModel.hospital_id == hospital_id)
    depts = query.order_by(VhDepartmentModel.department_name).all()
    return [{"department_id": d.department_id, "hospital_id": d.hospital_id, "department_name": d.department_name, "subdepartment_name": d.subdepartment_name} for d in depts]


def crear_departamento(data, db: Session) -> dict:
    hosp = db.query(VhHospitalModel).filter(VhHospitalModel.hospital_id == data.hospital_id).first()
    if not hosp:
        raise HTTPException(status_code=404, detail="Hospital no encontrado")
    existe = db.query(VhDepartmentModel).filter(
        VhDepartmentModel.hospital_id == data.hospital_id,
        VhDepartmentModel.department_name == data.department_name,
        VhDepartmentModel.subdepartment_name == data.subdepartment_name,
    ).first()
    if existe:
        raise HTTPException(status_code=409, detail="Ya existe ese departamento en el hospital")
    d = VhDepartmentModel(**data.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return {"department_id": d.department_id, "hospital_id": d.hospital_id, "department_name": d.department_name, "subdepartment_name": d.subdepartment_name, "created_at": d.created_at}


# ── Views / Reports ──

def resumen_mensual(db: Session, year: Optional[int] = None, category_id: Optional[int] = None) -> list[dict]:
    query = text("""
        SELECT category_name, variable_name, variable_code, month_name, month_number, year,
               masculino, femenino, total
        FROM v_vh_monthly_summary
        WHERE 1=1
        """ + (" AND year = :year" if year else "") + ("""
        AND category_id = :category_id""" if category_id else "") + """
        ORDER BY year DESC, month_number, category_name, variable_name
    """)
    params = {}
    if year:
        params["year"] = year
    if category_id:
        params["category_id"] = category_id
    rows = db.execute(query, params).mappings().all()
    return [dict(r) for r in rows]


def resumen_anual(db: Session, year: Optional[int] = None, category_id: Optional[int] = None) -> list[dict]:
    query = text("""
        SELECT category_name, variable_name, variable_code, year,
               masculino_total, femenino_total, total_anual
        FROM v_vh_annual_summary
        WHERE 1=1
        """ + (" AND year = :year" if year else "") + ("""
        AND category_id = :category_id""" if category_id else "") + """
        ORDER BY year DESC, category_name, variable_name
    """)
    params = {}
    if year:
        params["year"] = year
    if category_id:
        params["category_id"] = category_id
    rows = db.execute(query, params).mappings().all()
    return [dict(r) for r in rows]


def inventario_categorias(db: Session) -> list[dict]:
    rows = db.execute(text("""
        SELECT category_id, category_name, category_description, total_variables, variables_list
        FROM v_vh_variables_inventory
        ORDER BY category_name
    """)).mappings().all()
    return [dict(r) for r in rows]


def validar_totales(db: Session, year: int) -> list[dict]:
    rows = db.execute(text("SELECT * FROM fn_vh_validate_totals(:y)"), {"y": year}).mappings().all()
    return [dict(r) for r in rows]
