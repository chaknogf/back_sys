from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.variables.schemas import (
    CategoryCreate, CategoryUpdate, CategoryOut, CategoryListResponse,
    VariableCreate, VariableUpdate, VariableOut, VariableListResponse,
    MeasurementCreate, MeasurementUpdate, MeasurementOut, MeasurementListResponse,
    BulkImportRequest, BulkImportResponse,
    MonthlySummaryItem, AnnualSummaryItem, InventoryItem, ValidateResult,
    HospitalCreate, HospitalOut, DepartmentCreate, DepartmentOut,
    MonthOut, GenderOut,
)
from modules.variables.service import (
    listar_categorias as svc_listar_cats,
    obtener_categoria as svc_obtener_cat,
    crear_categoria as svc_crear_cat,
    actualizar_categoria as svc_actualizar_cat,
    eliminar_categoria as svc_eliminar_cat,
    listar_variables as svc_listar_vars,
    obtener_variable as svc_obtener_var,
    crear_variable as svc_crear_var,
    actualizar_variable as svc_actualizar_var,
    eliminar_variable as svc_eliminar_var,
    listar_mediciones as svc_listar_meds,
    obtener_medicion as svc_obtener_med,
    crear_medicion as svc_crear_med,
    actualizar_medicion as svc_actualizar_med,
    eliminar_medicion as svc_eliminar_med,
    bulk_upsert as svc_bulk_upsert,
    listar_meses, listar_generos,
    listar_hospitales, crear_hospital,
    listar_departamentos, crear_departamento,
    resumen_mensual, resumen_anual, inventario_categorias, validar_totales,
)

router = APIRouter(
    prefix="/variables",
    tags=["Variables Hospitalarias"],
)


# ── Hospitals ──

@router.get("/hospitals")
def listar_hospitales_endpoint(db: Session = Depends(get_db)):
    return listar_hospitales(db)


@router.post("/hospitals", response_model=HospitalOut, status_code=201)
def crear_hospital_endpoint(data: HospitalCreate, db: Session = Depends(get_db)):
    return crear_hospital(data, db)


# ── Departments ──

@router.get("/departments")
def listar_departamentos_endpoint(
    hospital_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return listar_departamentos(db, hospital_id)


@router.post("/departments", response_model=DepartmentOut, status_code=201)
def crear_departamento_endpoint(data: DepartmentCreate, db: Session = Depends(get_db)):
    return crear_departamento(data, db)


# ── Static refs ──

@router.get("/months", response_model=list[MonthOut])
def listar_meses_endpoint(db: Session = Depends(get_db)):
    return listar_meses(db)


@router.get("/genders", response_model=list[GenderOut])
def listar_generos_endpoint(db: Session = Depends(get_db)):
    return listar_generos(db)


# ── Categories ──

@router.get("/categorias", response_model=CategoryListResponse)
def listar_categorias_endpoint(
    q: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    cats, total = svc_listar_cats(db, q=q, skip=skip, limit=limit)
    return CategoryListResponse(total=total, categorias=cats)


@router.get("/categorias/{cat_id}", response_model=CategoryOut)
def obtener_categoria_endpoint(cat_id: int, db: Session = Depends(get_db)):
    return svc_obtener_cat(cat_id, db)


@router.post("/categorias", response_model=CategoryOut, status_code=201)
def crear_categoria_endpoint(data: CategoryCreate, db: Session = Depends(get_db)):
    return svc_crear_cat(data, db)


@router.put("/categorias/{cat_id}", response_model=CategoryOut)
def actualizar_categoria_endpoint(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    return svc_actualizar_cat(cat_id, data, db)


@router.delete("/categorias/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria_endpoint(cat_id: int, db: Session = Depends(get_db)):
    return svc_eliminar_cat(cat_id, db)


# ── Variables ──

@router.get("/", response_model=VariableListResponse)
def listar_variables_endpoint(
    category_id: Optional[int] = Query(None),
    q: Optional[str] = Query(None),
    data_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    vars_, total = svc_listar_vars(db, category_id=category_id, q=q, data_type=data_type, skip=skip, limit=limit)
    return VariableListResponse(total=total, variables=vars_)


@router.get("/{var_id}", response_model=VariableOut)
def obtener_variable_endpoint(var_id: int, db: Session = Depends(get_db)):
    return svc_obtener_var(var_id, db)


@router.post("/", response_model=VariableOut, status_code=201)
def crear_variable_endpoint(data: VariableCreate, db: Session = Depends(get_db)):
    return svc_crear_var(data, db)


@router.put("/{var_id}", response_model=VariableOut)
def actualizar_variable_endpoint(var_id: int, data: VariableUpdate, db: Session = Depends(get_db)):
    return svc_actualizar_var(var_id, data, db)


@router.delete("/{var_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_variable_endpoint(var_id: int, db: Session = Depends(get_db)):
    return svc_eliminar_var(var_id, db)


# ── Measurements ──

@router.get("/mediciones/", response_model=MeasurementListResponse)
def listar_mediciones_endpoint(
    hospital_id: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    variable_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    month_id: Optional[int] = Query(None),
    gender_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    meds, total = svc_listar_meds(
        db, hospital_id=hospital_id, department_id=department_id, variable_id=variable_id,
        category_id=category_id, month_id=month_id, gender_id=gender_id, year=year,
        skip=skip, limit=limit,
    )
    return MeasurementListResponse(total=total, mediciones=meds)


@router.get("/mediciones/{measurement_id}", response_model=MeasurementOut)
def obtener_medicion_endpoint(measurement_id: int, db: Session = Depends(get_db)):
    return svc_obtener_med(measurement_id, db)


@router.post("/mediciones/", response_model=MeasurementOut, status_code=201)
def crear_medicion_endpoint(data: MeasurementCreate, db: Session = Depends(get_db)):
    return svc_crear_med(data, db)


@router.put("/mediciones/{measurement_id}", response_model=MeasurementOut)
def actualizar_medicion_endpoint(measurement_id: int, data: MeasurementUpdate, db: Session = Depends(get_db)):
    return svc_actualizar_med(measurement_id, data, db)


@router.delete("/mediciones/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medicion_endpoint(measurement_id: int, db: Session = Depends(get_db)):
    return svc_eliminar_med(measurement_id, db)


@router.post("/mediciones/bulk", response_model=BulkImportResponse)
def bulk_upsert_endpoint(body: BulkImportRequest, db: Session = Depends(get_db)):
    return svc_bulk_upsert(body.mediciones, db)


# ── Views / Reports ──

@router.get("/reportes/resumen-mensual")
def resumen_mensual_endpoint(
    year: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return resumen_mensual(db, year=year, category_id=category_id)


@router.get("/reportes/resumen-anual")
def resumen_anual_endpoint(
    year: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return resumen_anual(db, year=year, category_id=category_id)


@router.get("/reportes/inventario")
def inventario_endpoint(db: Session = Depends(get_db)):
    return inventario_categorias(db)


@router.get("/reportes/validar")
def validar_totales_endpoint(
    year: int = Query(..., gt=1900, lt=2100),
    db: Session = Depends(get_db),
):
    return validar_totales(db, year)
