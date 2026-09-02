# 🔍 Guía de Consultas SQL - Base de Datos de Transfusiones

## 📚 Tabla de Contenidos

1. [Consultas Básicas](#consultas-básicas)
2. [Análisis por Variables](#análisis-por-variables)
3. [Análisis Temporal](#análisis-temporal)
4. [Comparativas](#comparativas)
5. [Reportes Avanzados](#reportes-avanzados)
6. [Validación de Datos](#validación-de-datos)
7. [Optimización](#optimización)

---

## 🔰 Consultas Básicas

### 1. Ver todos los datos con nombres legibles

```sql
SELECT * FROM v_measurements_detailed;
```

**Resultado**: Muestra todos los datos con nombres de hospital, departamento, variable, mes y género.

---

### 2. Obtener datos de un mes específico

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

---

### 3. Obtener datos de una variable específica

```sql
SELECT 
    mo.month_name,
    g.gender_name,
    m.measurement_value
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
JOIN months mo ON m.month_id = mo.month_id
WHERE v.variable_code = 'TRANS_EFE'
AND m.year = 2026
ORDER BY mo.month_number, g.gender_name;
```

---

## 📊 Análisis por Variables

### 1. Totales por variable (sin desagregación)

```sql
SELECT 
    v.variable_name,
    SUM(m.measurement_value) as total_anual
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
AND g.gender_name = 'Total'
GROUP BY v.variable_id, v.variable_name
ORDER BY total_anual DESC;
```

---

### 2. Promedios por variable

```sql
SELECT 
    v.variable_name,
    ROUND(AVG(m.measurement_value), 2) as promedio_mensual,
    MIN(m.measurement_value) as minimo,
    MAX(m.measurement_value) as maximo
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
AND g.gender_name = 'Total'
GROUP BY v.variable_id, v.variable_name
ORDER BY promedio_mensual DESC;
```

---

### 3. Porcentaje de contribución de cada variable

```sql
SELECT 
    v.variable_name,
    SUM(m.measurement_value) as total,
    ROUND(100.0 * SUM(m.measurement_value) / 
        (SELECT SUM(measurement_value) FROM measurements 
         WHERE gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Total')
         AND year = 2026), 2) as porcentaje
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
AND g.gender_name = 'Total'
GROUP BY v.variable_id, v.variable_name
ORDER BY porcentaje DESC;
```

---

### 4. Comparación masculino vs femenino

```sql
SELECT 
    v.variable_name,
    SUM(CASE WHEN g.gender_name = 'Masculino' THEN m.measurement_value ELSE 0 END) as total_masculino,
    SUM(CASE WHEN g.gender_name = 'Femenino' THEN m.measurement_value ELSE 0 END) as total_femenino,
    ROUND(100.0 * 
        SUM(CASE WHEN g.gender_name = 'Masculino' THEN m.measurement_value ELSE 0 END) /
        NULLIF(SUM(CASE WHEN g.gender_name = 'Femenino' THEN m.measurement_value ELSE 0 END), 0), 2) as proporcion_m_f
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
GROUP BY v.variable_id, v.variable_name
ORDER BY v.variable_name;
```

---

## 📅 Análisis Temporal

### 1. Tendencia mensual de una variable

```sql
SELECT 
    mo.month_number,
    mo.month_name,
    SUM(CASE WHEN g.gender_name = 'Total' THEN m.measurement_value ELSE 0 END) as total
FROM measurements m
JOIN months mo ON m.month_id = mo.month_id
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE v.variable_code = 'TRANS_EFE'
AND m.year = 2026
GROUP BY mo.month_number, mo.month_name
ORDER BY mo.month_number;
```

---

### 2. Evolución mes a mes (comparación con mes anterior)

```sql
WITH monthly_data AS (
    SELECT 
        mo.month_number,
        mo.month_name,
        v.variable_name,
        SUM(CASE WHEN g.gender_name = 'Total' THEN m.measurement_value ELSE 0 END) as total
    FROM measurements m
    JOIN months mo ON m.month_id = mo.month_id
    JOIN variables v ON m.variable_id = v.variable_id
    JOIN genders g ON m.gender_id = g.gender_id
    WHERE m.year = 2026
    GROUP BY mo.month_number, mo.month_name, v.variable_id, v.variable_name
)
SELECT 
    month_number,
    month_name,
    variable_name,
    total,
    LAG(total) OVER (PARTITION BY variable_name ORDER BY month_number) as mes_anterior,
    total - LAG(total) OVER (PARTITION BY variable_name ORDER BY month_number) as cambio_absoluto,
    ROUND(100.0 * (total - LAG(total) OVER (PARTITION BY variable_name ORDER BY month_number)) / 
          NULLIF(LAG(total) OVER (PARTITION BY variable_name ORDER BY month_number), 0), 2) as cambio_porcentual
FROM monthly_data
ORDER BY month_number, variable_name;
```

---

### 3. Meses con mayor actividad

```sql
SELECT 
    mo.month_name,
    SUM(m.measurement_value) as total_actividad
FROM measurements m
JOIN months mo ON m.month_id = mo.month_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
AND g.gender_name = 'Total'
GROUP BY mo.month_number, mo.month_name
ORDER BY total_actividad DESC;
```

---

### 4. Acumulado mensual (año hasta la fecha)

```sql
WITH monthly_totals AS (
    SELECT 
        mo.month_number,
        mo.month_name,
        SUM(m.measurement_value) as mes_total
    FROM measurements m
    JOIN months mo ON m.month_id = mo.month_id
    JOIN genders g ON m.gender_id = g.gender_id
    WHERE m.year = 2026
    AND g.gender_name = 'Total'
    GROUP BY mo.month_number, mo.month_name
)
SELECT 
    month_number,
    month_name,
    mes_total,
    SUM(mes_total) OVER (ORDER BY month_number) as acumulado_anual,
    ROUND(100.0 * mes_total / SUM(mes_total) OVER (), 2) as porcentaje_del_total
FROM monthly_totals
ORDER BY month_number;
```

---

## 📈 Comparativas

### 1. Comparar dos variables

```sql
SELECT 
    mo.month_name,
    MAX(CASE WHEN v.variable_code = 'TRANS_EFE' AND g.gender_name = 'Total' 
             THEN m.measurement_value END) as transfunciones,
    MAX(CASE WHEN v.variable_code = 'CEL_EMP' AND g.gender_name = 'Total' 
             THEN m.measurement_value END) as celulas_empacadas
FROM measurements m
JOIN months mo ON m.month_id = mo.month_id
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
GROUP BY mo.month_number, mo.month_name
ORDER BY mo.month_number;
```

---

### 2. Ratio entre variables

```sql
SELECT 
    mo.month_name,
    MAX(CASE WHEN v.variable_code = 'CEL_EMP' AND g.gender_name = 'Total' 
             THEN m.measurement_value END) as celulas_empacadas,
    MAX(CASE WHEN v.variable_code = 'TRANS_EFE' AND g.gender_name = 'Total' 
             THEN m.measurement_value END) as transfunciones,
    ROUND(100.0 * 
        MAX(CASE WHEN v.variable_code = 'CEL_EMP' AND g.gender_name = 'Total' 
                 THEN m.measurement_value END) /
        NULLIF(MAX(CASE WHEN v.variable_code = 'TRANS_EFE' AND g.gender_name = 'Total' 
                        THEN m.measurement_value END), 0), 2) as porcentaje_cel_vs_trans
FROM measurements m
JOIN months mo ON m.month_id = mo.month_id
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
GROUP BY mo.month_number, mo.month_name
ORDER BY mo.month_number;
```

---

## 📊 Reportes Avanzados

### 1. Tabla pivote: Variables vs Meses

```sql
SELECT 
    v.variable_name,
    MAX(CASE WHEN mo.abbreviation = 'ENE' THEN m.measurement_value END) as ENE,
    MAX(CASE WHEN mo.abbreviation = 'FEB' THEN m.measurement_value END) as FEB,
    MAX(CASE WHEN mo.abbreviation = 'MAR' THEN m.measurement_value END) as MAR,
    MAX(CASE WHEN mo.abbreviation = 'ABR' THEN m.measurement_value END) as ABR,
    MAX(CASE WHEN mo.abbreviation = 'MAY' THEN m.measurement_value END) as MAY,
    MAX(CASE WHEN mo.abbreviation = 'JUN' THEN m.measurement_value END) as JUN,
    MAX(CASE WHEN mo.abbreviation = 'JUL' THEN m.measurement_value END) as JUL,
    MAX(CASE WHEN mo.abbreviation = 'AGO' THEN m.measurement_value END) as AGO,
    MAX(CASE WHEN mo.abbreviation = 'SEP' THEN m.measurement_value END) as SEP,
    MAX(CASE WHEN mo.abbreviation = 'OCT' THEN m.measurement_value END) as OCT,
    MAX(CASE WHEN mo.abbreviation = 'NOV' THEN m.measurement_value END) as NOV,
    MAX(CASE WHEN mo.abbreviation = 'DIC' THEN m.measurement_value END) as DIC
FROM measurements m
JOIN variables v ON m.variable_id = v.variable_id
JOIN months mo ON m.month_id = mo.month_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
AND g.gender_name = 'Total'
GROUP BY v.variable_id, v.variable_name
ORDER BY v.variable_name;
```

---

### 2. Resumen executivo de 3 líneas

```sql
SELECT 
    (SELECT SUM(measurement_value) FROM measurements 
     WHERE gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Total')
     AND year = 2026) as total_transfusiones,
    
    (SELECT COUNT(DISTINCT month_id) FROM measurements WHERE year = 2026) as meses_con_datos,
    
    (SELECT ROUND(AVG(measurement_value), 2) FROM measurements 
     WHERE gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Total')
     AND year = 2026) as promedio_por_medicion;
```

---

### 3. Top 5: Meses con mayor actividad

```sql
SELECT 
    mo.month_name,
    SUM(m.measurement_value) as total_actividad,
    DENSE_RANK() OVER (ORDER BY SUM(m.measurement_value) DESC) as ranking
FROM measurements m
JOIN months mo ON m.month_id = mo.month_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
AND g.gender_name = 'Total'
GROUP BY mo.month_number, mo.month_name
ORDER BY total_actividad DESC
LIMIT 5;
```

---

### 4. Matriz: Género x Mes

```sql
SELECT 
    g.gender_name,
    MAX(CASE WHEN mo.abbreviation = 'ENE' THEN m.measurement_value END) as ENE,
    MAX(CASE WHEN mo.abbreviation = 'FEB' THEN m.measurement_value END) as FEB,
    MAX(CASE WHEN mo.abbreviation = 'MAR' THEN m.measurement_value END) as MAR,
    MAX(CASE WHEN mo.abbreviation = 'ABR' THEN m.measurement_value END) as ABR,
    MAX(CASE WHEN mo.abbreviation = 'MAY' THEN m.measurement_value END) as MAY,
    MAX(CASE WHEN mo.abbreviation = 'JUN' THEN m.measurement_value END) as JUN,
    MAX(CASE WHEN mo.abbreviation = 'JUL' THEN m.measurement_value END) as JUL
FROM measurements m
JOIN months mo ON m.month_id = mo.month_id
JOIN variables v ON m.variable_id = v.variable_id
JOIN genders g ON m.gender_id = g.gender_id
WHERE m.year = 2026
AND v.variable_code = 'TRANS_EFE'
GROUP BY g.gender_id, g.gender_name
ORDER BY CASE WHEN g.gender_name = 'Masculino' THEN 1 
             WHEN g.gender_name = 'Femenino' THEN 2 
             ELSE 3 END;
```

---

## ✅ Validación de Datos

### 1. Verificar totales incorrectos

```sql
SELECT 
    m1.measurement_id,
    v.variable_name,
    mo.month_name,
    m1.year,
    (SELECT measurement_value FROM measurements m 
     WHERE m.variable_id = m1.variable_id AND m.month_id = m1.month_id
     AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Masculino')) as masculino,
    (SELECT measurement_value FROM measurements m 
     WHERE m.variable_id = m1.variable_id AND m.month_id = m1.month_id
     AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Femenino')) as femenino,
    m1.measurement_value as total_registrado,
    COALESCE((SELECT measurement_value FROM measurements m 
     WHERE m.variable_id = m1.variable_id AND m.month_id = m1.month_id
     AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Masculino')), 0) +
    COALESCE((SELECT measurement_value FROM measurements m 
     WHERE m.variable_id = m1.variable_id AND m.month_id = m1.month_id
     AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Femenino')), 0) as total_calculado
FROM measurements m1
JOIN variables v ON m1.variable_id = v.variable_id
JOIN months mo ON m1.month_id = mo.month_id
JOIN genders g ON m1.gender_id = g.gender_id
WHERE g.gender_name = 'Total'
AND m1.measurement_value != 
    (COALESCE((SELECT measurement_value FROM measurements m 
     WHERE m.variable_id = m1.variable_id AND m.month_id = m1.month_id
     AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Masculino')), 0) +
    COALESCE((SELECT measurement_value FROM measurements m 
     WHERE m.variable_id = m1.variable_id AND m.month_id = m1.month_id
     AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Femenino')), 0))
ORDER BY v.variable_name, mo.month_number;
```

---

### 2. Encontrar datos faltantes

```sql
SELECT 
    v.variable_name,
    mo.month_name,
    g.gender_name
FROM variables v
CROSS JOIN months mo
CROSS JOIN genders g
WHERE NOT EXISTS (
    SELECT 1 FROM measurements m
    WHERE m.variable_id = v.variable_id
    AND m.month_id = mo.month_id
    AND m.gender_id = g.gender_id
    AND m.year = 2026
)
AND v.category_id = (SELECT category_id FROM variable_categories WHERE category_name = 'Transfusiones')
ORDER BY v.variable_name, mo.month_number, g.gender_name;
```

---

### 3. Duplicados

```sql
SELECT 
    hospital_id, department_id, variable_id, month_id, gender_id, year,
    COUNT(*) as cantidad_duplicados
FROM measurements
GROUP BY hospital_id, department_id, variable_id, month_id, gender_id, year
HAVING COUNT(*) > 1;
```

---

## 🚀 Optimización

### 1. Ver índices disponibles

```sql
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE tablename = 'measurements'
ORDER BY indexname;
```

---

### 2. Ver estadísticas de tabla

```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

### 3. Analizar performance de consulta

```sql
EXPLAIN ANALYZE
SELECT * FROM measurements 
WHERE hospital_id = 1 AND year = 2026
ORDER BY month_id;
```

---

### 4. Ver planes de ejecución

```sql
EXPLAIN (FORMAT JSON, ANALYZE)
SELECT * FROM v_monthly_summary 
WHERE year = 2026;
```

---

## 💾 Exportación de Datos

### 1. Exportar a CSV

```bash
psql -U postgres -d transfusiones \
  -c "COPY (SELECT * FROM v_measurements_detailed) TO STDOUT WITH CSV HEADER" \
  > datos_exportados.csv
```

---

### 2. Exportar a JSON

```bash
psql -U postgres -d transfusiones \
  -c "SELECT json_agg(row_to_json(t)) FROM (SELECT * FROM v_measurements_detailed) t;" \
  > datos_exportados.json
```

---

### 3. Exportar resumen anual

```bash
psql -U postgres -d transfusiones \
  -c "COPY (SELECT * FROM v_annual_summary WHERE year = 2026) TO STDOUT WITH CSV HEADER" \
  > resumen_anual_2026.csv
```

---

## 📝 Tips y Trucos

### Usar CASE para lógica condicional
```sql
CASE WHEN condición THEN valor1 ELSE valor2 END
```

### Usar COALESCE para valores nulos
```sql
COALESCE(columna, valor_default)
```

### Usar NULLIF para evitar divisiones por cero
```sql
valor1 / NULLIF(valor2, 0)
```

### Usar window functions para análisis avanzado
```sql
LAG(), LEAD(), ROW_NUMBER(), RANK(), DENSE_RANK() OVER (...)
```

### Usar PARTITION BY para agrupar dentro de window functions
```sql
SUM(valor) OVER (PARTITION BY variable ORDER BY mes)
```

---

**Última actualización**: 2026  
**Compatible con**: PostgreSQL 12+
