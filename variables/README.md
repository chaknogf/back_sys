# 🏥 Base de Datos Normalizada - Hospital General Tipo I de Tecpán Guatemala

## 📊 **AHORA CON 652 VARIABLES EN 59 CATEGORÍAS**

Tu archivo Excel contiene un **sistema integral de información hospitalaria** con datos de:
- **Transfusiones sanguíneas** (9 variables)
- **Laboratorio** (múltiples especialidades)
- **Rayos X** (estudios convencionales, portátiles, etc.)
- **Procedimientos quirúrgicos** (26 variables)
- **Nacimientos y neonatología** (17 variables)
- **Consulta externa** (múltiples especialidades)
- **Hospitalizaciones** (ocupación de camas, egresos, etc.)
- **Mortalidad** (índices y categorías)
- **Y mucho más...**

---

## 📁 Archivos Incluidos

### 1. **database_schema.sql** (13 KB)
Script SQL principal que crea:
- 7 tablas normalizadas
- 59 categorías de variables
- 4 vistas para reportes
- 9 índices de optimización
- 1 función de validación

**Ejecutar primero:**
```bash
psql -U postgres -d transfusiones -f database_schema.sql
```

### 2. **insert_all_variables.sql** (202 KB)
Script que inserta TODAS las variables:
- 59 INSERT para categorías
- 652 INSERT para variables

**Ejecutar segundo:**
```bash
psql -U postgres -d transfusiones -f insert_all_variables.sql
```

### 3. **all_variables.json** (25 KB)
Archivo JSON con la estructura de todas las variables:
```json
{
  "total_subsections": 59,
  "total_variables": 652,
  "subsections": [
    {
      "name": "Centro Transfuncional",
      "num_variables": 9,
      "variables": ["Transfunciones Efectuadas", ...]
    },
    ...
  ]
}
```

### 4. **all_variables.txt** (26 KB)
Listado legible de todas las variables por categoría

### 5. **import_data.py** (15 KB)
Script Python para importar datos desde Excel

**Usar para importar datos:**
```bash
python3 import_data.py /ruta/al/2026.xlsx
```

### 6. **Documentación MD**
- **DATABASE_DOCUMENTATION.md**: Guía completa de tablas
- **CONSULTAS_SQL.md**: 30+ ejemplos de consultas
- **README.md**: Guía rápida de inicio

---

## 🚀 Inicio Rápido (3 Pasos)

### Paso 1: Crear Base de Datos en PostgreSQL
```bash
# Crear la BD
createdb -U postgres transfusiones

# Ejecutar el schema principal (crea 7 tablas)
psql -U postgres -d transfusiones -f database_schema.sql

# Ejecutar las 652 variables (IMPORTANTE)
psql -U postgres -d transfusiones -f insert_all_variables.sql
```

### Paso 2: Importar Datos desde Excel (Opcional)
```bash
# Instalar dependencias
pip install pandas psycopg2-binary

# Importar datos
python3 import_data.py /ruta/al/2026.xlsx \
    --host localhost \
    --user postgres \
    --password tu_contraseña \
    --database transfusiones \
    --year 2026
```

### Paso 3: Verificar Instalación
```bash
psql -U postgres -d transfusiones

-- Ver todas las categorías
SELECT * FROM v_variables_inventory;

-- Ver datos importados
SELECT * FROM v_measurements_detailed LIMIT 10;

-- Ver resumen mensual
SELECT * FROM v_monthly_summary LIMIT 10;
```

---

## 📊 Estructura de la Base de Datos

```
┌──────────────────────────────────────────────────────────────┐
│                      MEDICIONES (Principal)                   │
│  hospital_id, department_id, variable_id, month_id, gender_id│
│  year, measurement_value, is_calculated                       │
└──────────────────────────────────────────────────────────────┘
            ↓           ↓            ↓             ↓        ↓
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────┐ ┌────────┐
    │  HOSPITALS   │ │ DEPARTMENTS  │ │  VARIABLES   │ │MONTHS│ │GENDERS │
    │      ↑       │ │              │ │      ↑       │ └──────┘ └────────┘
    │      └─────→ │ │              │ │      │       │
    └──────────────┘ └──────────────┘ │      └────────────────┐
                                      │                       │
                            ┌─────────┴──────────────────────┐
                            │                                │
                    ┌───────▼──────────────┐
                    │ VARIABLE_CATEGORIES  │
                    │  (59 categorías)     │
                    └──────────────────────┘
```

---

## 📚 Las 59 Categorías de Variables

1. **Centro Transfuncional** (9 variables)
2. **Estudios de Laboratorio transmisibles y no transmisibles** (13 variables)
3. **Estudios de Laboratorio** (14 variables)
4. **Personas atendidas en laboratorio** (14 variables)
5. **Pruebas No reclamadas** (8 variables)
6. **Bacterología** (9 variables)
7. **Reactivos** (23 variables)
8. **Prueba de Laboratorio** (11 variables)
9. **Personas atendidas Rayos X** (11 variables)
10. **Estudios realizados por especialidad** (8 variables)
... y **49 más**

👉 **Ver listado completo**: `all_variables.txt`

---

## 🔍 Vistas Disponibles para Reportes

### 1. **v_measurements_detailed**
Todos los datos con nombres legibles
```sql
SELECT * FROM v_measurements_detailed LIMIT 10;
```

### 2. **v_monthly_summary**
Resumen mensual desagregado por género
```sql
SELECT * FROM v_monthly_summary WHERE year = 2026;
```

### 3. **v_annual_summary**
Totales anuales por variable
```sql
SELECT * FROM v_annual_summary WHERE year = 2026;
```

### 4. **v_variables_inventory**
Inventario de categorías y sus variables
```sql
SELECT * FROM v_variables_inventory;
```

---

## 💾 Ejemplos de Consultas

### Ver todas las variables de una categoría
```sql
SELECT v.variable_name, COUNT(m.measurement_id) as registros
FROM variables v
LEFT JOIN measurements m ON v.variable_id = m.variable_id
WHERE v.category_id = (SELECT category_id FROM variable_categories 
                       WHERE category_name = 'Centro Transfuncional')
GROUP BY v.variable_id, v.variable_name;
```

### Totales mensuales de transfusiones
```sql
SELECT 
    mo.month_name,
    v.variable_name,
    SUM(CASE WHEN g.gender_name = 'Total' THEN m.measurement_value ELSE 0 END) as total
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN months mo ON m.month_id = mo.month_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE v.category_id = (SELECT category_id FROM variable_categories WHERE category_name = 'Centro Transfuncional')
AND m.year = 2026
AND g.gender_name = 'Total'
GROUP BY mo.month_number, mo.month_name, v.variable_id, v.variable_name
ORDER BY mo.month_number, v.variable_name;
```

### Comparar especialidades en laboratorio
```sql
SELECT 
    v.variable_name,
    SUM(CASE WHEN g.gender_name = 'Total' THEN m.measurement_value ELSE 0 END) as total
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN variable_categories vc ON v.category_id = vc.category_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE vc.category_name LIKE '%Laboratorio%'
AND m.year = 2026
AND g.gender_name = 'Total'
GROUP BY v.variable_id, v.variable_name
ORDER BY total DESC;
```

### Validar integridad (total = masculino + femenino)
```sql
SELECT * FROM validate_measurement_totals(2026) 
WHERE es_valido = FALSE;
```

---

## 📈 Capacidad de la BD

| Métrica | Valor |
|---------|-------|
| **Variables** | 652 |
| **Categorías** | 59 |
| **Meses por año** | 12 |
| **Géneros** | 3 (M, F, T) |
| **Registros por año** | 652 × 12 × 3 = **23,472** |
| **Registros en 5 años** | **117,360** |
| **Tamaño BD vacía** | ~10 MB |
| **Tamaño con 1 año** | ~50 MB |
| **Tamaño con 5 años** | ~250 MB |

---

## 🛠️ Operaciones Comunes

### Insertar datos manualmente
```sql
INSERT INTO measurements 
(hospital_id, department_id, variable_id, month_id, gender_id, year, measurement_value)
VALUES
(
    (SELECT hospital_id FROM hospitals LIMIT 1),
    (SELECT department_id FROM departments LIMIT 1),
    (SELECT variable_id FROM variables WHERE variable_name = 'Transfunciones Efectuadas'),
    (SELECT month_id FROM months WHERE abbreviation = 'ENE'),
    (SELECT gender_id FROM genders WHERE gender_name = 'Masculino'),
    2026,
    34
);
```

### Agregar nueva variable
```sql
INSERT INTO variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type)
VALUES
(
    (SELECT category_id FROM variable_categories WHERE category_name = 'Centro Transfuncional'),
    'Nueva Variable',
    'NEW_VAR',
    'Descripción de la nueva variable',
    'unidades',
    'numeric'
);
```

### Agregar nuevo hospital
```sql
INSERT INTO hospitals (hospital_name, hospital_type, location)
VALUES ('Hospital Nuevo', 'Tipo I', 'Ubicación');

INSERT INTO departments (hospital_id, department_name, subdepartment_name)
VALUES 
(
    (SELECT hospital_id FROM hospitals WHERE hospital_name = 'Hospital Nuevo'),
    'Nombre Departamento',
    'Subdepartamento'
);
```

---

## 📊 Escalabilidad

### Agregar más años
Solo inserta nuevos registros con el año correspondiente:
```sql
INSERT INTO measurements (..., year, ...) VALUES (..., 2027, ...);
```

### Agregar múltiples hospitales
```sql
INSERT INTO hospitals (hospital_name, hospital_type, location)
VALUES 
('Hospital Tipo I - Zona 1', 'Tipo I', 'Ciudad'),
('Hospital Tipo II - Zona 2', 'Tipo II', 'Pueblo');
```

### Agregar nuevas categorías de variables
```sql
INSERT INTO variable_categories (category_name, description)
VALUES ('Nueva Categoría', 'Descripción');

-- Luego agregar variables a esa categoría
INSERT INTO variables (category_id, variable_name, ...)
VALUES (...);
```

---

## ✅ Checklist de Setup

- [ ] PostgreSQL instalado y corriendo
- [ ] Base de datos "transfusiones" creada
- [ ] `database_schema.sql` ejecutado ✨
- [ ] `insert_all_variables.sql` ejecutado (652 variables) ✨
- [ ] Datos importados desde Excel (opcional)
- [ ] Vistas funcionando
- [ ] Conexión desde aplicación exitosa

---

## 🔧 Solución de Problemas

### "relation 'variable_categories' does not exist"
Asegúrate de ejecutar `database_schema.sql` primero.

### "foreign key constraint violated"
Verifica que las categorías existan antes de insertar variables.

### Import lento
Es normal con 652 variables. Toma 2-5 minutos la primera vez.

### Datos duplicados
Usa `ON CONFLICT` en los INSERT:
```sql
INSERT INTO measurements (...) VALUES (...)
ON CONFLICT (hospital_id, department_id, variable_id, month_id, gender_id, year)
DO UPDATE SET measurement_value = EXCLUDED.measurement_value;
```

---

## 📞 Referencia Rápida

### Ver todas las categorías
```bash
psql -U postgres -d transfusiones -c "SELECT * FROM variable_categories;"
```

### Contar variables por categoría
```bash
psql -U postgres -d transfusiones -c "SELECT * FROM v_variables_inventory;"
```

### Ver datos de un mes
```bash
psql -U postgres -d transfusiones -c "
SELECT * FROM v_measurements_detailed 
WHERE month_name = 'Enero' AND year = 2026
LIMIT 10;"
```

### Exportar a CSV
```bash
psql -U postgres -d transfusiones -c \
"COPY (SELECT * FROM v_measurements_detailed) TO STDOUT WITH CSV HEADER" \
> datos_exportados.csv
```

---

## 📖 Documentación Completa

Para información detallada sobre cada tabla y columna:
👉 **Ver**: `DATABASE_DOCUMENTATION.md`

Para 30+ ejemplos de consultas SQL:
👉 **Ver**: `CONSULTAS_SQL.md`

Para listado de todas las variables:
👉 **Ver**: `all_variables.txt`

---

## 🎯 Próximos Pasos

1. ✅ Crear la BD con `database_schema.sql`
2. ✅ Insertar 652 variables con `insert_all_variables.sql`
3. ✅ Importar datos del Excel con `import_data.py`
4. 📊 Crear dashboards en Metabase, Power BI o Grafana
5. 📈 Automatizar reportes mensuales
6. 🔄 Integrar con sistemas de facturación/RIS

---

## 📊 Resumen

| Componente | Cantidad | Archivo |
|-----------|----------|---------|
| **Tablas** | 7 | database_schema.sql |
| **Categorías** | 59 | insert_all_variables.sql |
| **Variables** | 652 | insert_all_variables.sql |
| **Vistas** | 4 | database_schema.sql |
| **Índices** | 9 | database_schema.sql |
| **Funciones** | 1 | database_schema.sql |

---

## ✨ Ventajas de esta Estructura

✅ **Normalizada**: Sin redundancia  
✅ **Escalable**: Agrega variables sin cambiar la estructura  
✅ **Rápida**: 9 índices optimizados  
✅ **Flexible**: Múltiples hospitales, departamentos  
✅ **Segura**: Integridad referencial garantizada  
✅ **Reportable**: 4 vistas predefinidas  
✅ **Validable**: Función para verificar integridad  
✅ **Exportable**: A CSV, JSON, reportes  

---

**Versión**: 2.0 (Completo)  
**Fecha**: 2026  
**Compatible con**: PostgreSQL 12+  
**Total de Variables**: 652 en 59 categorías  

¡Tu base de datos está lista para usar! 🚀
