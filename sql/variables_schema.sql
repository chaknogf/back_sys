-- ============================================================================
-- MIGRACIÓN: Tablas de Variables Hospitalarias
-- Base de datos: hospital
-- Compatible con el módulo modules/variables/ del backend
-- Ejecutar: psql -U postgres -d hospital -f sql/variables_schema.sql
-- ============================================================================

-- 1. TABLA: HOSPITALES (estadísticas)
CREATE TABLE IF NOT EXISTS vh_hospitals (
    hospital_id SERIAL PRIMARY KEY,
    hospital_name VARCHAR(255) NOT NULL UNIQUE,
    hospital_type VARCHAR(50),
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA: DEPARTAMENTOS
CREATE TABLE IF NOT EXISTS vh_departments (
    department_id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL REFERENCES vh_hospitals(hospital_id) ON DELETE CASCADE,
    department_name VARCHAR(255) NOT NULL,
    subdepartment_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_vh_dept_per_hospital UNIQUE(hospital_id, department_name, subdepartment_name)
);

-- 3. TABLA: MESES
CREATE TABLE IF NOT EXISTS vh_months (
    month_id SERIAL PRIMARY KEY,
    month_name VARCHAR(20) NOT NULL UNIQUE,
    month_number INTEGER NOT NULL UNIQUE CHECK(month_number BETWEEN 1 AND 12),
    abbreviation VARCHAR(3) NOT NULL UNIQUE
);

-- 4. TABLA: GÉNEROS/SEXO
CREATE TABLE IF NOT EXISTS vh_genders (
    gender_id SERIAL PRIMARY KEY,
    gender_name VARCHAR(50) NOT NULL UNIQUE,
    abbreviation VARCHAR(10)
);

-- 5. TABLA: CATEGORÍAS DE VARIABLES
CREATE TABLE IF NOT EXISTS vh_variable_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. TABLA: VARIABLES
CREATE TABLE IF NOT EXISTS vh_variables (
    variable_id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES vh_variable_categories(category_id) ON DELETE CASCADE,
    variable_name VARCHAR(255) NOT NULL,
    variable_code VARCHAR(50) UNIQUE,
    description TEXT,
    unit_of_measure VARCHAR(100) DEFAULT 'unidades',
    data_type VARCHAR(20) DEFAULT 'numeric' CHECK(data_type IN ('numeric', 'boolean', 'text')),
    is_aggregate BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. TABLA PRINCIPAL: MEDICIONES
CREATE TABLE IF NOT EXISTS vh_measurements (
    measurement_id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL REFERENCES vh_hospitals(hospital_id) ON DELETE CASCADE,
    department_id INTEGER NOT NULL REFERENCES vh_departments(department_id) ON DELETE CASCADE,
    variable_id INTEGER NOT NULL REFERENCES vh_variables(variable_id) ON DELETE CASCADE,
    month_id INTEGER NOT NULL REFERENCES vh_months(month_id) ON DELETE CASCADE,
    gender_id INTEGER NOT NULL REFERENCES vh_genders(gender_id) ON DELETE CASCADE,
    year INTEGER NOT NULL CHECK(year > 1900 AND year < 2100),
    measurement_value DECIMAL(12, 2),
    notes TEXT,
    is_calculated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_vh_measurement UNIQUE(hospital_id, department_id, variable_id, month_id, gender_id, year)
);

-- ============================================================================
-- ÍNDICES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_vh_meas_hospital ON vh_measurements(hospital_id);
CREATE INDEX IF NOT EXISTS idx_vh_meas_department ON vh_measurements(department_id);
CREATE INDEX IF NOT EXISTS idx_vh_meas_variable ON vh_measurements(variable_id);
CREATE INDEX IF NOT EXISTS idx_vh_meas_month ON vh_measurements(month_id);
CREATE INDEX IF NOT EXISTS idx_vh_meas_gender ON vh_measurements(gender_id);
CREATE INDEX IF NOT EXISTS idx_vh_meas_year ON vh_measurements(year);
CREATE INDEX IF NOT EXISTS idx_vh_meas_composite ON vh_measurements(hospital_id, department_id, year, month_id, variable_id);
CREATE INDEX IF NOT EXISTS idx_vh_vars_category ON vh_variables(category_id);
CREATE INDEX IF NOT EXISTS idx_vh_dept_hospital ON vh_departments(hospital_id);

-- ============================================================================
-- DATOS ESTÁTICOS: Meses y Géneros
-- ============================================================================
INSERT INTO vh_months (month_name, month_number, abbreviation) VALUES
('Enero', 1, 'ENE'),
('Febrero', 2, 'FEB'),
('Marzo', 3, 'MAR'),
('Abril', 4, 'ABR'),
('Mayo', 5, 'MAY'),
('Junio', 6, 'JUN'),
('Julio', 7, 'JUL'),
('Agosto', 8, 'AGO'),
('Septiembre', 9, 'SEP'),
('Octubre', 10, 'OCT'),
('Noviembre', 11, 'NOV'),
('Diciembre', 12, 'DIC')
ON CONFLICT (month_name) DO NOTHING;

INSERT INTO vh_genders (gender_name, abbreviation) VALUES
('Masculino', 'M'),
('Femenino', 'F'),
('Total', 'T')
ON CONFLICT (gender_name) DO NOTHING;

-- ============================================================================
-- VISTAS PARA REPORTES
-- ============================================================================

-- Vista 1: Datos detallados con todos los nombres
CREATE OR REPLACE VIEW v_vh_measurements_detailed AS
SELECT
    m.measurement_id,
    h.hospital_name,
    d.department_name,
    d.subdepartment_name,
    vc.category_name,
    v.variable_name,
    v.variable_code,
    mo.month_name,
    mo.month_number,
    g.gender_name,
    m.year,
    m.measurement_value,
    m.notes,
    m.is_calculated,
    m.created_at,
    m.updated_at
FROM vh_measurements m
JOIN vh_hospitals h ON m.hospital_id = h.hospital_id
JOIN vh_departments d ON m.department_id = d.department_id
JOIN vh_variables v ON m.variable_id = v.variable_id
JOIN vh_variable_categories vc ON v.category_id = vc.category_id
JOIN vh_months mo ON m.month_id = mo.month_id
JOIN vh_genders g ON m.gender_id = g.gender_id
ORDER BY m.year DESC, mo.month_number, vc.category_name, v.variable_name, g.gender_name;

-- Vista 2: Resumen mensual por variable
CREATE OR REPLACE VIEW v_vh_monthly_summary AS
SELECT
    vc.category_name,
    v.variable_name,
    v.variable_code,
    mo.month_name,
    mo.month_number,
    m.year,
    SUM(CASE WHEN g.gender_name = 'Masculino' THEN m.measurement_value ELSE 0 END) as masculino,
    SUM(CASE WHEN g.gender_name = 'Femenino' THEN m.measurement_value ELSE 0 END) as femenino,
    SUM(CASE WHEN g.gender_name = 'Total' THEN m.measurement_value ELSE 0 END) as total
FROM vh_measurements m
JOIN vh_variables v ON m.variable_id = v.variable_id
JOIN vh_variable_categories vc ON v.category_id = vc.category_id
JOIN vh_months mo ON m.month_id = mo.month_id
JOIN vh_genders g ON m.gender_id = g.gender_id
GROUP BY vc.category_id, vc.category_name, v.variable_id, v.variable_name, v.variable_code, mo.month_number, mo.month_name, m.year
ORDER BY m.year DESC, mo.month_number, vc.category_name, v.variable_name;

-- Vista 3: Resumen anual por variable
CREATE OR REPLACE VIEW v_vh_annual_summary AS
SELECT
    vc.category_name,
    v.variable_name,
    v.variable_code,
    m.year,
    SUM(CASE WHEN g.gender_name = 'Masculino' THEN m.measurement_value ELSE 0 END) as masculino_total,
    SUM(CASE WHEN g.gender_name = 'Femenino' THEN m.measurement_value ELSE 0 END) as femenino_total,
    SUM(CASE WHEN g.gender_name = 'Total' THEN m.measurement_value ELSE 0 END) as total_anual
FROM vh_measurements m
JOIN vh_variables v ON m.variable_id = v.variable_id
JOIN vh_variable_categories vc ON v.category_id = vc.category_id
JOIN vh_genders g ON m.gender_id = g.gender_id
GROUP BY vc.category_id, vc.category_name, v.variable_id, v.variable_name, v.variable_code, m.year
ORDER BY m.year DESC, vc.category_name, v.variable_name;

-- Vista 4: Inventario de categorías y variables
CREATE OR REPLACE VIEW v_vh_variables_inventory AS
SELECT
    vc.category_id,
    vc.category_name,
    vc.description as category_description,
    COUNT(DISTINCT v.variable_id) as total_variables,
    STRING_AGG(v.variable_name, ', ' ORDER BY v.variable_name) as variables_list
FROM vh_variable_categories vc
LEFT JOIN vh_variables v ON vc.category_id = v.category_id
GROUP BY vc.category_id, vc.category_name, vc.description
ORDER BY vc.category_name;

-- ============================================================================
-- FUNCIÓN DE VALIDACIÓN
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_vh_validate_totals(p_year INTEGER)
RETURNS TABLE (
    p_measurement_id INTEGER,
    p_category_name VARCHAR,
    p_variable_name VARCHAR,
    p_month_name VARCHAR,
    p_year INTEGER,
    p_masculino DECIMAL,
    p_femenino DECIMAL,
    p_total_registrado DECIMAL,
    p_total_esperado DECIMAL,
    p_es_valido BOOLEAN
) AS $$
SELECT
    m1.measurement_id,
    vc.category_name,
    v.variable_name,
    mo.month_name,
    m1.year,
    (SELECT measurement_value FROM vh_measurements m WHERE m.variable_id = m1.variable_id
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM vh_genders WHERE gender_name = 'Masculino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year),
    (SELECT measurement_value FROM vh_measurements m WHERE m.variable_id = m1.variable_id
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM vh_genders WHERE gender_name = 'Femenino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year),
    m1.measurement_value,
    COALESCE((SELECT measurement_value FROM vh_measurements m WHERE m.variable_id = m1.variable_id
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM vh_genders WHERE gender_name = 'Masculino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year), 0) +
    COALESCE((SELECT measurement_value FROM vh_measurements m WHERE m.variable_id = m1.variable_id
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM vh_genders WHERE gender_name = 'Femenino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year), 0),
    m1.measurement_value =
    (COALESCE((SELECT measurement_value FROM vh_measurements m WHERE m.variable_id = m1.variable_id
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM vh_genders WHERE gender_name = 'Masculino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year), 0) +
    COALESCE((SELECT measurement_value FROM vh_measurements m WHERE m.variable_id = m1.variable_id
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM vh_genders WHERE gender_name = 'Femenino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year), 0))
FROM vh_measurements m1
JOIN vh_variables v ON m1.variable_id = v.variable_id
JOIN vh_variable_categories vc ON v.category_id = vc.category_id
JOIN vh_months mo ON m1.month_id = mo.month_id
JOIN vh_genders g ON m1.gender_id = g.gender_id
WHERE g.gender_name = 'Total'
AND m1.year = p_year
ORDER BY m1.year DESC, mo.month_number, vc.category_name, v.variable_name;
$$ LANGUAGE SQL;
