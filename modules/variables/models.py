from sqlalchemy import (
    Column, Integer, SmallInteger, String, Text, Boolean, Numeric, ForeignKey,
    UniqueConstraint, TIMESTAMP, text,
)
from sqlalchemy.orm import relationship
from core.database import Base


class VhHospitalModel(Base):
    __tablename__ = "vh_hospitals"

    hospital_id = Column(Integer, primary_key=True, index=True)
    hospital_name = Column(String(255), nullable=False, unique=True)
    hospital_type = Column(String(50))
    location = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    departments = relationship("VhDepartmentModel", back_populates="hospital")


class VhDepartmentModel(Base):
    __tablename__ = "vh_departments"
    __table_args__ = (
        UniqueConstraint("hospital_id", "department_name", "subdepartment_name", name="uq_vh_dept_per_hospital"),
    )

    department_id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("vh_hospitals.hospital_id", ondelete="CASCADE"), nullable=False, index=True)
    department_name = Column(String(255), nullable=False)
    subdepartment_name = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    hospital = relationship("VhHospitalModel", back_populates="departments")


class VhMonthModel(Base):
    __tablename__ = "vh_months"

    month_id = Column(Integer, primary_key=True, index=True)
    month_name = Column(String(20), nullable=False, unique=True)
    month_number = Column(Integer, nullable=False, unique=True)
    abbreviation = Column(String(3), nullable=False, unique=True)


class VhGenderModel(Base):
    __tablename__ = "vh_genders"

    gender_id = Column(Integer, primary_key=True, index=True)
    gender_name = Column(String(50), nullable=False, unique=True)
    abbreviation = Column(String(10))


class VhVariableCategoryModel(Base):
    __tablename__ = "vh_variable_categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    variables = relationship("VhVariableModel", back_populates="category", cascade="all, delete-orphan")


class VhVariableModel(Base):
    __tablename__ = "vh_variables"
    __table_args__ = (
        UniqueConstraint("category_id", "variable_code", name="uq_vh_var_code_category"),
    )

    variable_id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("vh_variable_categories.category_id", ondelete="CASCADE"), nullable=False, index=True)
    variable_name = Column(String(255), nullable=False)
    variable_code = Column(String(50))
    description = Column(Text)
    unit_of_measure = Column(String(100), default="unidades")
    data_type = Column(String(20), default="numeric")
    is_aggregate = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    category = relationship("VhVariableCategoryModel", back_populates="variables")


class VhMeasurementModel(Base):
    __tablename__ = "vh_measurements"
    __table_args__ = (
        UniqueConstraint("hospital_id", "department_id", "variable_id", "month_id", "gender_id", "year", name="uq_vh_measurement"),
    )

    measurement_id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("vh_hospitals.hospital_id", ondelete="CASCADE"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("vh_departments.department_id", ondelete="CASCADE"), nullable=False, index=True)
    variable_id = Column(Integer, ForeignKey("vh_variables.variable_id", ondelete="CASCADE"), nullable=False, index=True)
    month_id = Column(Integer, ForeignKey("vh_months.month_id", ondelete="CASCADE"), nullable=False, index=True)
    gender_id = Column(Integer, ForeignKey("vh_genders.gender_id", ondelete="CASCADE"), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    measurement_value = Column(Numeric(12, 2))
    notes = Column(Text)
    is_calculated = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    hospital = relationship("VhHospitalModel")
    department = relationship("VhDepartmentModel")
    variable = relationship("VhVariableModel")
    month = relationship("VhMonthModel")
    gender = relationship("VhGenderModel")
