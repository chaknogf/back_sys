from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ── Categories ──

class CategoryCreate(BaseModel):
    category_name: str = Field(..., max_length=255)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class CategoryOut(BaseModel):
    category_id: int
    category_name: str
    description: Optional[str]
    total_variables: int = 0
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    total: int
    categorias: list[CategoryOut]


# ── Variables ──

class VariableCreate(BaseModel):
    category_id: int
    variable_name: str = Field(..., max_length=255)
    variable_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    unit_of_measure: str = "unidades"
    data_type: str = Field("numeric", pattern="^(numeric|boolean|text)$")
    is_aggregate: bool = False


class VariableUpdate(BaseModel):
    category_id: Optional[int] = None
    variable_name: Optional[str] = Field(None, max_length=255)
    variable_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    unit_of_measure: Optional[str] = None
    data_type: Optional[str] = Field(None, pattern="^(numeric|boolean|text)$")
    is_aggregate: Optional[bool] = None


class VariableOut(BaseModel):
    variable_id: int
    category_id: int
    category_name: Optional[str] = None
    variable_name: str
    variable_code: Optional[str]
    description: Optional[str]
    unit_of_measure: Optional[str]
    data_type: Optional[str]
    is_aggregate: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class VariableListResponse(BaseModel):
    total: int
    variables: list[VariableOut]


# ── Measurements ──

class MeasurementCreate(BaseModel):
    hospital_id: int
    department_id: int
    variable_id: int
    month_id: int
    gender_id: int
    year: int = Field(..., gt=1900, lt=2100)
    measurement_value: Optional[Decimal] = None
    notes: Optional[str] = None
    is_calculated: bool = False


class MeasurementUpdate(BaseModel):
    measurement_value: Optional[Decimal] = None
    notes: Optional[str] = None
    is_calculated: Optional[bool] = None


class MeasurementOut(BaseModel):
    measurement_id: int
    hospital_id: int
    hospital_name: Optional[str] = None
    department_id: int
    department_name: Optional[str] = None
    variable_id: int
    variable_name: Optional[str] = None
    variable_code: Optional[str] = None
    month_id: int
    month_name: Optional[str] = None
    month_number: Optional[int] = None
    gender_id: int
    gender_name: Optional[str] = None
    year: int
    measurement_value: Optional[Decimal]
    notes: Optional[str]
    is_calculated: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class MeasurementListResponse(BaseModel):
    total: int
    mediciones: list[MeasurementOut]


# ── Bulk / Import ──

class MeasurementBulkItem(BaseModel):
    hospital_id: int
    department_id: int
    variable_id: int
    month_id: int
    gender_id: int
    year: int
    measurement_value: Optional[Decimal] = None
    notes: Optional[str] = None
    is_calculated: bool = False


class BulkImportRequest(BaseModel):
    mediciones: list[MeasurementBulkItem]


class BulkImportResponse(BaseModel):
    creados: int
    actualizados: int
    errores: list[dict]


# ── Summary / Inventory ──

class MonthlySummaryItem(BaseModel):
    category_name: str
    variable_name: str
    variable_code: Optional[str]
    month_name: str
    month_number: int
    year: int
    masculino: Decimal
    femenino: Decimal
    total: Decimal

    model_config = ConfigDict(from_attributes=True)


class AnnualSummaryItem(BaseModel):
    category_name: str
    variable_name: str
    variable_code: Optional[str]
    year: int
    masculino_total: Decimal
    femenino_total: Decimal
    total_anual: Decimal

    model_config = ConfigDict(from_attributes=True)


class InventoryItem(BaseModel):
    category_id: int
    category_name: str
    category_description: Optional[str]
    total_variables: int
    variables_list: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ValidateResult(BaseModel):
    measurement_id: int
    category_name: str
    variable_name: str
    month_name: str
    year: int
    masculino: Optional[Decimal]
    femenino: Optional[Decimal]
    total_registrado: Decimal
    total_esperado: Decimal
    es_valido: bool

    model_config = ConfigDict(from_attributes=True)


# ── Hospital / Department ──

class HospitalCreate(BaseModel):
    hospital_name: str = Field(..., max_length=255)
    hospital_type: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)


class HospitalOut(BaseModel):
    hospital_id: int
    hospital_name: str
    hospital_type: Optional[str]
    location: Optional[str]
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class DepartmentCreate(BaseModel):
    hospital_id: int
    department_name: str = Field(..., max_length=255)
    subdepartment_name: Optional[str] = Field(None, max_length=255)


class DepartmentOut(BaseModel):
    department_id: int
    hospital_id: int
    department_name: str
    subdepartment_name: Optional[str]
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ── Static refs ──

class MonthOut(BaseModel):
    month_id: int
    month_name: str
    month_number: int
    abbreviation: str

    model_config = ConfigDict(from_attributes=True)


class GenderOut(BaseModel):
    gender_id: int
    gender_name: str
    abbreviation: Optional[str]

    model_config = ConfigDict(from_attributes=True)
