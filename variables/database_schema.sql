-- ============================================================================
-- BASE DE DATOS NORMALIZADA - HOSPITAL GENERAL TIPO I DE TECPÁN GUATEMALA
-- Departamento: Laboratorio, Bacterología y Centro Transfusional
-- 
-- ESTRUCTURA COMPLETA CON 652 VARIABLES EN 59 CATEGORÍAS
-- Año: 2026
-- ============================================================================

-- 1. TABLA: HOSPITALES
CREATE TABLE hospitals (
    hospital_id SERIAL PRIMARY KEY,
    hospital_name VARCHAR(255) NOT NULL UNIQUE,
    hospital_type VARCHAR(50),
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA: DEPARTAMENTOS
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL REFERENCES hospitals(hospital_id) ON DELETE CASCADE,
    department_name VARCHAR(255) NOT NULL,
    subdepartment_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_dept_per_hospital UNIQUE(hospital_id, department_name, subdepartment_name)
);

-- 3. TABLA: MESES
CREATE TABLE months (
    month_id SERIAL PRIMARY KEY,
    month_name VARCHAR(20) NOT NULL UNIQUE,
    month_number INTEGER NOT NULL UNIQUE CHECK(month_number BETWEEN 1 AND 12),
    abbreviation VARCHAR(3) NOT NULL UNIQUE
);

-- 4. TABLA: GÉNEROS/SEXO
CREATE TABLE genders (
    gender_id SERIAL PRIMARY KEY,
    gender_name VARCHAR(50) NOT NULL UNIQUE,
    abbreviation VARCHAR(10)
);

-- 5. TABLA: CATEGORÍAS DE VARIABLES (59 categorías)
CREATE TABLE variable_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. TABLA: VARIABLES (652 variables en total)
CREATE TABLE variables (
    variable_id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES variable_categories(category_id) ON DELETE CASCADE,
    variable_name VARCHAR(255) NOT NULL,
    variable_code VARCHAR(50) UNIQUE,
    description TEXT,
    unit_of_measure VARCHAR(100) DEFAULT 'unidades',
    data_type VARCHAR(20) DEFAULT 'numeric' CHECK(data_type IN ('numeric', 'boolean', 'text')),
    is_aggregate BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. TABLA PRINCIPAL: MEASUREMENTS
-- Almacena todos los datos medibles (hospital × departamento × variable × mes × género × año)
CREATE TABLE measurements (
    measurement_id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL REFERENCES hospitals(hospital_id) ON DELETE CASCADE,
    department_id INTEGER NOT NULL REFERENCES departments(department_id) ON DELETE CASCADE,
    variable_id INTEGER NOT NULL REFERENCES variables(variable_id) ON DELETE CASCADE,
    month_id INTEGER NOT NULL REFERENCES months(month_id) ON DELETE CASCADE,
    gender_id INTEGER NOT NULL REFERENCES genders(gender_id) ON DELETE CASCADE,
    year INTEGER NOT NULL CHECK(year > 1900 AND year < 2100),
    measurement_value DECIMAL(12, 2),
    notes TEXT,
    is_calculated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Restricción de unicidad para evitar duplicados
    CONSTRAINT unique_measurement UNIQUE(hospital_id, department_id, variable_id, month_id, gender_id, year)
);

-- ============================================================================
-- ÍNDICES PARA OPTIMIZACIÓN (CRÍTICO para 652 variables)
-- ============================================================================

CREATE INDEX idx_measurements_hospital ON measurements(hospital_id);
CREATE INDEX idx_measurements_department ON measurements(department_id);
CREATE INDEX idx_measurements_variable ON measurements(variable_id);
CREATE INDEX idx_measurements_month ON measurements(month_id);
CREATE INDEX idx_measurements_gender ON measurements(gender_id);
CREATE INDEX idx_measurements_year ON measurements(year);
CREATE INDEX idx_measurements_composite ON measurements(hospital_id, department_id, year, month_id, variable_id);
CREATE INDEX idx_variables_category ON variables(category_id);
CREATE INDEX idx_departments_hospital ON departments(hospital_id);

-- ============================================================================
-- INSERCIÓN DE DATOS ESTÁTICOS
-- ============================================================================

-- Insertar meses
INSERT INTO months (month_name, month_number, abbreviation) VALUES
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
('Diciembre', 12, 'DIC');

-- Insertar géneros
INSERT INTO genders (gender_name, abbreviation) VALUES
('Masculino', 'M'),
('Femenino', 'F'),
('Total', 'T');

-- Insertar hospital base
INSERT INTO hospitals (hospital_name, hospital_type, location) VALUES
('Hospital General Tipo I de Tecpán Guatemala', 'Tipo I', 'Tecpán Guatemala');

-- Insertar departamento base
INSERT INTO departments (hospital_id, department_name, subdepartment_name) VALUES
((SELECT hospital_id FROM hospitals WHERE hospital_name = 'Hospital General Tipo I de Tecpán Guatemala'),
 'LABORATORIO, BACTEROLOGIA Y CENTRO TRANSFUSIONAL',
 'Centro Transfuncional');

-- ============================================================================
-- VISTAS PARA ANÁLISIS RÁPIDO
-- ============================================================================

-- Vista 1: Datos detallados con todos los nombres
CREATE VIEW v_measurements_detailed AS
SELECT 
    m.measurement_id,
    h.hospital_name,
    d.department_name,
    d.subdepartment_name,
    vc.category_name,
    v.variable_name,
    mo.month_name,
    mo.month_number,
    g.gender_name,
    m.year,
    m.measurement_value,
    m.notes,
    m.is_calculated,
    m.created_at,
    m.updated_at
FROM measurements m
JOIN hospitals h ON m.hospital_id = h.hospital_id
JOIN departments d ON m.department_id = d.department_id
JOIN variables v ON m.variable_id = v.variable_id
JOIN variable_categories vc ON v.category_id = vc.category_id
JOIN months mo ON m.month_id = mo.month_id
JOIN genders g ON m.gender_id = g.gender_id
ORDER BY m.year DESC, mo.month_number, vc.category_name, v.variable_name, g.gender_name;

-- Vista 2: Resumen mensual por variable
CREATE VIEW v_monthly_summary AS
SELECT 
    vc.category_name,
    v.variable_name,
    mo.month_name,
    mo.month_number,
    m.year,
    SUM(CASE WHEN g.gender_name = 'Masculino' THEN m.measurement_value ELSE 0 END) as masculino,
    SUM(CASE WHEN g.gender_name = 'Femenino' THEN m.measurement_value ELSE 0 END) as femenino,
    SUM(CASE WHEN g.gender_name = 'Total' THEN m.measurement_value ELSE 0 END) as total
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN variable_categories vc ON v.category_id = vc.category_id
JOIN months mo ON m.month_id = mo.month_id
JOIN genders g ON m.gender_id = g.gender_id
GROUP BY vc.category_id, vc.category_name, v.variable_id, v.variable_name, mo.month_number, mo.month_name, m.year
ORDER BY m.year DESC, mo.month_number, vc.category_name, v.variable_name;

-- Vista 3: Resumen anual por variable
CREATE VIEW v_annual_summary AS
SELECT 
    vc.category_name,
    v.variable_name,
    m.year,
    SUM(CASE WHEN g.gender_name = 'Masculino' THEN m.measurement_value ELSE 0 END) as masculino_total,
    SUM(CASE WHEN g.gender_name = 'Femenino' THEN m.measurement_value ELSE 0 END) as femenino_total,
    SUM(CASE WHEN g.gender_name = 'Total' THEN m.measurement_value ELSE 0 END) as total_anual
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN variable_categories vc ON v.category_id = vc.category_id
JOIN genders g ON m.gender_id = g.gender_id
GROUP BY vc.category_id, vc.category_name, v.variable_id, v.variable_name, m.year
ORDER BY m.year DESC, vc.category_name, v.variable_name;

-- Vista 4: Inventario de categorías y variables
CREATE VIEW v_variables_inventory AS
SELECT 
    vc.category_id,
    vc.category_name,
    COUNT(DISTINCT v.variable_id) as total_variables,
    STRING_AGG(v.variable_name, ', ' ORDER BY v.variable_name) as variables_list
FROM variable_categories vc
LEFT JOIN variables v ON vc.category_id = v.category_id
GROUP BY vc.category_id, vc.category_name
ORDER BY vc.category_name;

-- ============================================================================
-- FUNCIÓN DE VALIDACIÓN
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_measurement_totals(p_year INTEGER)
RETURNS TABLE (
    measurement_id INTEGER,
    category_name VARCHAR,
    variable_name VARCHAR,
    month_name VARCHAR,
    year INTEGER,
    masculino DECIMAL,
    femenino DECIMAL,
    total_registrado DECIMAL,
    total_esperado DECIMAL,
    es_valido BOOLEAN
) AS $$
SELECT 
    m1.measurement_id,
    vc.category_name,
    v.variable_name,
    mo.month_name,
    m1.year,
    (SELECT measurement_value FROM measurements m WHERE m.variable_id = m1.variable_id 
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Masculino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year) as masculino,
    (SELECT measurement_value FROM measurements m WHERE m.variable_id = m1.variable_id 
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Femenino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year) as femenino,
    m1.measurement_value as total_registrado,
    COALESCE((SELECT measurement_value FROM measurements m WHERE m.variable_id = m1.variable_id 
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Masculino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year), 0) +
    COALESCE((SELECT measurement_value FROM measurements m WHERE m.variable_id = m1.variable_id 
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Femenino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year), 0) as total_esperado,
    m1.measurement_value = 
    (COALESCE((SELECT measurement_value FROM measurements m WHERE m.variable_id = m1.variable_id 
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Masculino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year), 0) +
    COALESCE((SELECT measurement_value FROM measurements m WHERE m.variable_id = m1.variable_id 
        AND m.month_id = m1.month_id AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Femenino')
        AND m.hospital_id = m1.hospital_id AND m.department_id = m1.department_id AND m.year = m1.year), 0)) as es_valido
FROM measurements m1
JOIN variables v ON m1.variable_id = v.variable_id
JOIN variable_categories vc ON v.category_id = vc.category_id
JOIN months mo ON m1.month_id = mo.month_id
JOIN genders g ON m1.gender_id = g.gender_id
WHERE g.gender_name = 'Total'
AND m1.year = p_year
ORDER BY m1.year DESC, mo.month_number, vc.category_name, v.variable_name;
$$ LANGUAGE SQL;

-- ============================================================================
-- NOTAS IMPORTANTES
-- ============================================================================

/*
ESTE SCHEMA INCLUYE:

1. TABLAS PRINCIPALES:
   - hospitals: Información de hospitales
   - departments: Departamentos/áreas
   - variable_categories: 59 categorías de variables
   - variables: 652 variables en total
   - measurements: Datos principales (~652 variables × 12 meses × 3 géneros = 23,472 registros por año)
   - months: Meses del año (estático)
   - genders: Géneros (estático)

2. VISTAS PARA REPORTES RÁPIDOS:
   - v_measurements_detailed: Todos los datos con nombres
   - v_monthly_summary: Resumen mensual
   - v_annual_summary: Resumen anual
   - v_variables_inventory: Inventario de categorías y variables

3. ÍNDICES:
   - 9 índices para optimizar búsquedas
   - Índices compuestos para consultas frecuentes

4. FUNCIONES:
   - validate_measurement_totals: Validar integridad de datos (total = masculino + femenino)

PRÓXIMOS PASOS:
1. Ejecutar: psql -U postgres -d transfusiones -f database_schema_complete.sql
2. Ejecutar: psql -U postgres -d transfusiones -f insert_all_variables.sql
3. Ejecutar: python3 import_data.py 2026.xlsx

TAMAÑO ESTIMADO:
- Base de datos vacía: ~10 MB
- Con 1 año de datos: ~50 MB
- Con 5 años de datos: ~250 MB
*/
