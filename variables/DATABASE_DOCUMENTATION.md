# 📊 Documentación de Base de Datos Normalizada - Transfusiones Hospitalarias

## 📋 Tabla de Contenidos
1. [Introducción](#introducción)
2. [Estructura de la Base de Datos](#estructura-de-la-base-de-datos)
3. [Descripción de Tablas](#descripción-de-tablas)
4. [Relaciones entre Tablas](#relaciones-entre-tablas)
5. [Cómo Insertar Datos](#cómo-insertar-datos)
6. [Consultas Útiles](#consultas-útiles)
7. [Vistas Predefinidas](#vistas-predefinidas)
8. [Escalabilidad](#escalabilidad)
9. [Mantenimiento](#mantenimiento)

---

## 🎯 Introducción

Esta base de datos está diseñada para almacenar datos de **transfusiones hospitalarias** de forma normalizada y escalable. Permite:

- ✅ Reutilizar datos estáticos (meses, géneros, hospitales)
- ✅ Agregar nuevas variables sin cambiar la estructura
- ✅ Soportar múltiples hospitales y departamentos
- ✅ Mantener integridad referencial
- ✅ Consultas rápidas gracias a índices optimizados

### Hospital Base
- **Nombre**: Hospital General Tipo I de Tecpán Guatemala
- **Servicio**: Estadística
- **Departamento**: Laboratorio, Bacterología y Centro Transfusional

---

## 🏗️ Estructura de la Base de Datos

```
┌─────────────────┐
│   HOSPITALS     │ ◄─── Hospital principal
└────────┬────────┘
         │
         ├─────────────────────────┐
         │                         │
    ┌────▼────────┐          ┌────▼──────────┐
    │ DEPARTMENTS │          │ MEASUREMENTS  │ ◄─── Datos principales
    └─────────────┘          └────┬──────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
           ┌────▼────────┐   ┌────▼────────┐  ┌────▼───────┐
           │  VARIABLES  │   │   MONTHS    │  │   GENDERS   │
           └────┬────────┘   └─────────────┘  └─────────────┘
                │
           ┌────▼──────────────┐
           │ VARIABLE_CATEGORIES│
           └────────────────────┘
```

---

## 📑 Descripción de Tablas

### 1. **HOSPITALS**
Almacena información sobre hospitales. Permite tener múltiples hospitales en la misma base de datos.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `hospital_id` | SERIAL PK | ID único del hospital |
| `hospital_name` | VARCHAR(255) | Nombre del hospital (único) |
| `hospital_type` | VARCHAR(50) | Tipo de hospital (Tipo I, Tipo II, etc.) |
| `location` | VARCHAR(255) | Ubicación geográfica |
| `created_at` | TIMESTAMP | Fecha de creación del registro |

**Uso**: Actualmente contiene al Hospital General Tipo I de Tecpán Guatemala. Se puede agregar más hospitales fácilmente.

---

### 2. **DEPARTMENTS**
Agrupa áreas/departamentos dentro de un hospital.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `department_id` | SERIAL PK | ID único del departamento |
| `hospital_id` | INTEGER FK | Referencia al hospital |
| `department_name` | VARCHAR(255) | Nombre del departamento |
| `subdepartment_name` | VARCHAR(255) | Subdepartamento (ej: Centro Transfuncional) |
| `created_at` | TIMESTAMP | Fecha de creación |

**Constraint**: Combinación única de (hospital_id, department_name, subdepartment_name)

**Uso**: Actualmente: "LABORATORIO, BACTEROLOGIA Y CENTRO TRANSFUSIONAL" > "Centro Transfuncional"

---

### 3. **MONTHS**
Tabla estática que almacena los meses del año. Permite reutilización.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `month_id` | SERIAL PK | ID único |
| `month_name` | VARCHAR(20) | Nombre completo (Enero, Febrero, etc.) |
| `month_number` | INTEGER | Número del mes (1-12) |
| `abbreviation` | VARCHAR(3) | Abreviatura (ENE, FEB, etc.) |

**Datos**: Precargada con los 12 meses del año.

---

### 4. **GENDERS**
Tabla estática que almacena tipos de sexo/género.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `gender_id` | SERIAL PK | ID único |
| `gender_name` | VARCHAR(50) | Nombre del género |
| `abbreviation` | VARCHAR(10) | Abreviatura (M, F, T) |

**Datos Precargados**:
- Masculino (M)
- Femenino (F)
- Total (T) - para valores sumados

---

### 5. **VARIABLE_CATEGORIES**
Agrupa variables por categoría (permite expandir en el futuro a diagnósticos, procedimientos, etc.)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `category_id` | SERIAL PK | ID único de la categoría |
| `category_name` | VARCHAR(100) | Nombre de la categoría |
| `description` | TEXT | Descripción de la categoría |
| `created_at` | TIMESTAMP | Fecha de creación |

**Categoría Actual**: "Transfusiones" - Variables relacionadas con transfusiones de sangre

---

### 6. **VARIABLES**
Define cada variable medible. Escalable para agregar nuevas variables.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `variable_id` | SERIAL PK | ID único |
| `category_id` | INTEGER FK | Categoría a la que pertenece |
| `variable_name` | VARCHAR(255) | Nombre descriptivo |
| `variable_code` | VARCHAR(50) | Código único para la variable (ej: TRANS_EFE) |
| `description` | TEXT | Descripción detallada |
| `unit_of_measure` | VARCHAR(100) | Unidad de medida |
| `data_type` | VARCHAR(20) | Tipo de dato (numeric, boolean, text) |
| `is_aggregate` | BOOLEAN | TRUE si es suma de otros valores |
| `created_at` | TIMESTAMP | Fecha de creación |
| `updated_at` | TIMESTAMP | Última actualización |

**Variables Precargadas**:
1. Transfunciones Efectuadas (TRANS_EFE) - Agregada
2. Células Empacadas (CEL_EMP)
3. Plasma Fresco Congelado (PFC)
4. Paquete Globular (PAQ_GLOB)
5. Concentrado Plaquetario (CONC_PLAQ)
6. Plaquetas por Aféresis (PLAQ_AFER)
7. Crioprecipitados (CRIOPRE)
8. Unidades Descartadas (UNIT_DESC)
9. Reacciones Diversas a la Transfusión (REAC_TRANS)

---

### 7. **MEASUREMENTS** ⭐ (Tabla Principal)
Almacena todos los datos reales. Esta es la tabla más importante.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `measurement_id` | SERIAL PK | ID único del registro |
| `hospital_id` | INTEGER FK | Referencia al hospital |
| `department_id` | INTEGER FK | Referencia al departamento |
| `variable_id` | INTEGER FK | Referencia a la variable |
| `month_id` | INTEGER FK | Referencia al mes |
| `gender_id` | INTEGER FK | Referencia al género |
| `year` | INTEGER | Año del dato |
| `measurement_value` | DECIMAL(10,2) | Valor numérico del dato |
| `notes` | TEXT | Notas o comentarios |
| `is_calculated` | BOOLEAN | TRUE si es un valor calculado (suma) |
| `created_at` | TIMESTAMP | Fecha de creación |
| `updated_at` | TIMESTAMP | Última actualización |

**Constraint Único**: (hospital_id, department_id, variable_id, month_id, gender_id, year)
- Garantiza que no hay duplicados para el mismo dato

**Índices**: Optimizados para búsquedas por hospital, departamento, variable, mes, año.

---

## 🔗 Relaciones entre Tablas

### Diagramas de Relación

```
HOSPITALS (1) ──────────── (N) DEPARTMENTS
     │
     │
     └──────────┬─────────────────────────────┐
                │                             │
         (1) MEASUREMENTS (N)                  │
             ├─ hospital_id ──────────────────┘
             ├─ department_id ──────┐
             ├─ variable_id ────┐   │
             ├─ month_id ──┐    │   │
             ├─ gender_id──┤    │   │
             │             │    │   │
             │        ┌────▼────▼───▼─────┐
             │        │    DEPARTMENTS    │
             │        └───────────────────┘
             │
             ├─ variable_id ──────────┐
             │                        │
             │                   ┌────▼─────────────┐
             │                   │    VARIABLES    │
             │                   │  (category_id) ◄─────┐
             │                   └────────────────┘      │
             │                                      ┌────┴──────────────┐
             │                                      │ VARIABLE_CATEGORIES
             │                                      └────────────────────┘
             │
             ├─ month_id ──────────────┐
             │                         │
             │                    ┌────▼───┐
             │                    │ MONTHS │
             │                    └────────┘
             │
             └─ gender_id ──────────────┐
                                        │
                                   ┌────▼───┐
                                   │ GENDERS│
                                   └────────┘
```

---

## 📥 Cómo Insertar Datos

### Paso 1: Asegurate que los datos estáticos existan

Los datos estáticos **ya están precargados**:
- ✅ Meses (12 meses del año)
- ✅ Géneros (Masculino, Femenino, Total)
- ✅ Hospital (Hospital General Tipo I de Tecpán Guatemala)
- ✅ Departamento (Laboratorio, Bacterología y Centro Transfusional)
- ✅ Variables de Transfusiones (9 variables)

### Paso 2: Insertar datos de mediciones

**Método 1: Insertar valores individuales**

```sql
INSERT INTO measurements 
(hospital_id, department_id, variable_id, month_id, gender_id, year, measurement_value, is_calculated)
VALUES
(
    (SELECT hospital_id FROM hospitals WHERE hospital_name = 'Hospital General Tipo I de Tecpán Guatemala'),
    (SELECT department_id FROM departments LIMIT 1),
    (SELECT variable_id FROM variables WHERE variable_code = 'TRANS_EFE'),
    (SELECT month_id FROM months WHERE abbreviation = 'ENE'),
    (SELECT gender_id FROM genders WHERE gender_name = 'Masculino'),
    2026,
    34,
    FALSE
);
```

**Método 2: Insertar lote de datos (más eficiente)**

```sql
INSERT INTO measurements 
(hospital_id, department_id, variable_id, month_id, gender_id, year, measurement_value, is_calculated)
VALUES
-- Enero 2026 - Transfunciones Efectuadas
((SELECT hospital_id FROM hospitals LIMIT 1), (SELECT department_id FROM departments LIMIT 1), 
 (SELECT variable_id FROM variables WHERE variable_code = 'TRANS_EFE'), 
 (SELECT month_id FROM months WHERE abbreviation = 'ENE'),
 (SELECT gender_id FROM genders WHERE gender_name = 'Masculino'), 2026, 34, FALSE),

((SELECT hospital_id FROM hospitals LIMIT 1), (SELECT department_id FROM departments LIMIT 1), 
 (SELECT variable_id FROM variables WHERE variable_code = 'TRANS_EFE'), 
 (SELECT month_id FROM months WHERE abbreviation = 'ENE'),
 (SELECT gender_id FROM genders WHERE gender_name = 'Femenino'), 2026, 59, FALSE),

((SELECT hospital_id FROM hospitals LIMIT 1), (SELECT department_id FROM departments LIMIT 1), 
 (SELECT variable_id FROM variables WHERE variable_code = 'TRANS_EFE'), 
 (SELECT month_id FROM months WHERE abbreviation = 'ENE'),
 (SELECT gender_id FROM genders WHERE gender_name = 'Total'), 2026, 93, TRUE),

-- Enero 2026 - Células Empacadas
((SELECT hospital_id FROM hospitals LIMIT 1), (SELECT department_id FROM departments LIMIT 1), 
 (SELECT variable_id FROM variables WHERE variable_code = 'CEL_EMP'), 
 (SELECT month_id FROM months WHERE abbreviation = 'ENE'),
 (SELECT gender_id FROM genders WHERE gender_name = 'Masculino'), 2026, 15, FALSE),

((SELECT hospital_id FROM hospitals LIMIT 1), (SELECT department_id FROM departments LIMIT 1), 
 (SELECT variable_id FROM variables WHERE variable_code = 'CEL_EMP'), 
 (SELECT month_id FROM months WHERE abbreviation = 'ENE'),
 (SELECT gender_id FROM genders WHERE gender_name = 'Femenino'), 2026, 35, FALSE),

((SELECT hospital_id FROM hospitals LIMIT 1), (SELECT department_id FROM departments LIMIT 1), 
 (SELECT variable_id FROM variables WHERE variable_code = 'CEL_EMP'), 
 (SELECT month_id FROM months WHERE abbreviation = 'ENE'),
 (SELECT gender_id FROM genders WHERE gender_name = 'Total'), 2026, 50, TRUE);
```

### Paso 3: Validar datos insertados

```sql
-- Ver todos los datos insertados
SELECT * FROM v_measurements_detailed;

-- Ver resumen mensual
SELECT * FROM v_monthly_summary WHERE year = 2026;
```

---

## 🔍 Consultas Útiles

### 1. Obtener todos los datos de un mes específico

```sql
SELECT 
    v.variable_name,
    g.gender_name,
    m.measurement_value
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
JOIN months mo ON m.month_id = mo.month_id
WHERE mo.abbreviation = 'ENE'
AND m.year = 2026
ORDER BY v.variable_name, g.gender_name;
```

### 2. Comparar valores entre meses

```sql
SELECT 
    mo.month_name,
    v.variable_name,
    SUM(CASE WHEN g.gender_name = 'Total' THEN m.measurement_value ELSE 0 END) as total
FROM measurements m
JOIN months mo ON m.month_id = mo.month_id
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
AND g.gender_name = 'Total'
GROUP BY mo.month_name, v.variable_name
ORDER BY mo.month_number, v.variable_name;
```

### 3. Desagregación por sexo de una variable

```sql
SELECT 
    v.variable_name,
    mo.month_name,
    MAX(CASE WHEN g.gender_name = 'Masculino' THEN m.measurement_value END) as masculino,
    MAX(CASE WHEN g.gender_name = 'Femenino' THEN m.measurement_value END) as femenino,
    MAX(CASE WHEN g.gender_name = 'Total' THEN m.measurement_value END) as total
FROM measurements m
JOIN months mo ON m.month_id = mo.month_id
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE v.variable_code = 'TRANS_EFE'
AND m.year = 2026
GROUP BY v.variable_name, mo.month_number, mo.month_name
ORDER BY mo.month_number;
```

### 4. Totales anuales por variable

```sql
SELECT 
    v.variable_name,
    SUM(CASE WHEN g.gender_name = 'Total' THEN m.measurement_value ELSE 0 END) as anual_total
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
AND g.gender_name = 'Total'
GROUP BY v.variable_name
ORDER BY v.variable_name;
```

### 5. Identificar datos faltantes

```sql
SELECT DISTINCT
    mo.month_name,
    v.variable_name
FROM months mo
CROSS JOIN variables v
WHERE NOT EXISTS (
    SELECT 1 FROM measurements m
    WHERE m.variable_id = v.variable_id
    AND m.month_id = mo.month_id
    AND m.year = 2026
)
ORDER BY mo.month_number, v.variable_name;
```

---

## 📊 Vistas Predefinidas

### Vista 1: `v_measurements_detailed`
Muestra todos los datos con nombres legibles (sin IDs).

```sql
SELECT * FROM v_measurements_detailed;
```

**Columnas**: hospital_name, department_name, subdepartment_name, category_name, variable_name, month_name, gender_name, year, measurement_value, notes, is_calculated

---

### Vista 2: `v_monthly_summary`
Resumen mensual de cada variable con totales por género.

```sql
SELECT * FROM v_monthly_summary WHERE year = 2026;
```

**Columnas**: hospital_name, department_name, variable_name, month_name, year, total_value, male_value, female_value

---

### Vista 3: `v_annual_summary`
Resumen anual de cada variable.

```sql
SELECT * FROM v_annual_summary WHERE year = 2026;
```

**Columnas**: hospital_name, department_name, variable_name, year, annual_total, annual_male, annual_female

---

## 🚀 Escalabilidad

### Cómo agregar una nueva variable

**Paso 1**: Insertar la variable en la tabla VARIABLES

```sql
INSERT INTO variables 
(category_id, variable_name, variable_code, description, unit_of_measure, data_type, is_aggregate)
VALUES
(
    (SELECT category_id FROM variable_categories WHERE category_name = 'Transfusiones'),
    'Nueva Variable',
    'NEW_VAR',
    'Descripción de la nueva variable',
    'unidades',
    'numeric',
    FALSE
);
```

**Paso 2**: Insertar datos para esa variable

```sql
INSERT INTO measurements 
(hospital_id, department_id, variable_id, month_id, gender_id, year, measurement_value, is_calculated)
VALUES
-- Los datos se insertarán normalmente con la nueva variable_id
```

### Cómo agregar una nueva categoría de variables

```sql
INSERT INTO variable_categories (category_name, description)
VALUES ('Nueva Categoría', 'Descripción de la categoría');

-- Luego agregar variables en esa categoría
INSERT INTO variables (category_id, variable_name, variable_code, ...)
VALUES (...);
```

### Cómo agregar un nuevo hospital

```sql
INSERT INTO hospitals (hospital_name, hospital_type, location)
VALUES ('Nuevo Hospital', 'Tipo I', 'Ubicación');

-- Agregar departamentos para ese hospital
INSERT INTO departments (hospital_id, department_name, subdepartment_name)
VALUES ((SELECT hospital_id FROM hospitals WHERE hospital_name = 'Nuevo Hospital'), 'Departamento', 'Subdepartamento');
```

---

## 🔧 Mantenimiento

### Función de Validación: `validate_totals()`

Verifica que los totales sean la suma correcta de masculino + femenino.

```sql
SELECT * FROM validate_totals();
```

**Resultado**: Muestra registros donde el total no coincide con la suma de masculino + femenino.

### Actualizar un dato existente

```sql
UPDATE measurements
SET measurement_value = 95,
    updated_at = CURRENT_TIMESTAMP
WHERE measurement_id = 1;
```

### Eliminar datos de un mes específico

```sql
DELETE FROM measurements
WHERE month_id = (SELECT month_id FROM months WHERE abbreviation = 'ENE')
AND year = 2026;
```

### Ver estructura de tablas

```sql
-- Ver todas las tablas
\dt

-- Ver estructura de una tabla
\d measurements

-- Ver índices
\di

-- Ver vistas
\dv
```

---

## 💡 Mejores Prácticas

1. **Usar IDs en lugar de nombres**: Las queries son más rápidas con IDs.

```sql
-- ❌ Lento
SELECT * FROM measurements WHERE hospital_id IN (SELECT hospital_id FROM hospitals WHERE hospital_name = '...');

-- ✅ Rápido
SELECT * FROM measurements WHERE hospital_id = 1;
```

2. **Usar vistas para reportes**: Mantienen la consulta en un solo lugar.

```sql
SELECT * FROM v_measurements_detailed;
```

3. **Validar datos antes de insertar**: Asegúrate de que total = masculino + femenino.

4. **Usar transacciones para inserciones en lote**:

```sql
BEGIN;
INSERT INTO measurements (...) VALUES (...);
INSERT INTO measurements (...) VALUES (...);
COMMIT;
```

5. **Hacer backup periódico** de la base de datos.

---

## 📞 Soporte y Troubleshooting

### Error: "Duplicate key value violates unique constraint"
- Significa que el mismo dato ya existe (hospital, departamento, variable, mes, género, año)
- Solución: Actualiza el registro existente en lugar de insertarlo nuevamente

### Error: "Foreign key constraint violation"
- Significa que estás intentando referenciar un ID que no existe
- Solución: Verifica que el ID exista en la tabla referenciada

### Consulta lenta
- Verifica que estés usando los índices disponibles
- Prueba con `EXPLAIN ANALYZE` antes de la consulta

```sql
EXPLAIN ANALYZE
SELECT * FROM measurements WHERE hospital_id = 1 AND year = 2026;
```

---

**Última actualización**: 2026  
**Versión**: 1.0  
**Compatible con**: PostgreSQL 12+
