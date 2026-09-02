# 📑 ÍNDICE COMPLETO - Archivos Incluidos

## 🏥 Base de Datos Normalizada - Hospital General Tipo I de Tecpán Guatemala
### **652 Variables en 59 Categorías**

---

## 📋 TABLA DE CONTENIDOS

| Archivo | Tamaño | Tipo | Descripción |
|---------|--------|------|------------|
| [1. Scripts SQL de Estructura](#1-scripts-sql-de-estructura) | - | SQL | Crear la BD |
| [2. Scripts de Importación](#2-scripts-de-importación-de-datos) | - | Python | Importar datos |
| [3. Herramientas de Gestión](#3-herramientas-de-gestión) | - | SQL/Bash | Limpiar, validar |
| [4. Documentación](#4-documentación) | - | Markdown | Guías y referencias |
| [5. Datos de Referencia](#5-datos-de-referencia) | - | JSON/TXT | Información |

---

## 1. Scripts SQL de Estructura

### **database_schema.sql** (13 KB)
**Propósito:** Crear la estructura base de la base de datos
**Contenido:**
- 7 tablas normalizadas
- 4 vistas para reportes
- 9 índices de optimización
- 1 función de validación
- Datos estáticos (meses, géneros, hospital, departamento)

**Cuándo usar:**
```bash
# Ejecutar PRIMERO
psql -U postgres -d transfusiones -f database_schema.sql
```

**Qué hace:**
- Crea tabla `hospitals` (información de hospitales)
- Crea tabla `departments` (departamentos/áreas)
- Crea tabla `months` (12 meses del año)
- Crea tabla `genders` (Masculino, Femenino, Total)
- Crea tabla `variable_categories` (59 categorías)
- Crea tabla `variables` (estructura para 652 variables)
- Crea tabla `measurements` (tabla principal de datos)
- Crea vistas para reportes rápidos
- Crea índices para optimización

**Requisito previo:**
```bash
createdb -U postgres transfusiones
```

---

### **insert_all_variables.sql** (202 KB)
**Propósito:** Insertar TODAS las 652 variables en 59 categorías
**Contenido:**
- 59 INSERT para categorías
- 652 INSERT para variables

**Cuándo usar:**
```bash
# Ejecutar SEGUNDO (después de database_schema.sql)
psql -U postgres -d transfusiones -f insert_all_variables.sql
```

**Nota:** Este archivo es grande (202 KB) porque incluye 711 INSERT statements

---

## 2. Scripts de Importación de Datos

### **import_advanced.py** (22 KB)
**Propósito:** Script Python avanzado para importar datos desde Excel
**Características:**
- Importa todas las 652 variables automáticamente
- Detecta estructura del Excel automáticamente
- Maneja 3 géneros (Masculino, Femenino, Total)
- Valida integridad de datos
- Muestra resumen detallado
- Modo verbose/silencioso

**Uso:**
```bash
# Forma simple
python3 import_advanced.py 2026.xlsx

# Forma completa
python3 import_advanced.py 2026.xlsx \
    --host localhost \
    --user postgres \
    --password secret \
    --database transfusiones \
    --year 2026

# Modo silencioso
python3 import_advanced.py 2026.xlsx --quiet
```

**Requisitos:**
```bash
pip install pandas psycopg2-binary
```

**Qué hace:**
1. Lee archivo Excel
2. Extrae 59 categorías y 652 variables
3. Extrae filas de datos (12 meses)
4. Sincroniza categorías y variables con BD
5. Inserta ~23,472 registros por año
6. Valida integridad
7. Muestra resumen

---

### **import_data.py** (15 KB)
**Propósito:** Script Python simple (versión anterior, más básico)
**Nota:** Usar `import_advanced.py` que es más completo

---

## 3. Herramientas de Gestión

### **test_data.sql** (7.3 KB)
**Propósito:** Insertar datos de prueba para validar la estructura
**Contenido:**
- Datos de ejemplo para 3 variables
- Datos para 3 meses (ENE, FEB, MAR)
- Desagregación por género

**Cuándo usar:**
```bash
# Después de insertar las 652 variables
psql -U postgres -d transfusiones -f test_data.sql
```

**Qué hace:**
- Inserta ~30 registros de prueba
- Valida que la estructura funciona
- Genera reportes de verificación

**Uso típico:**
1. Crear BD: `database_schema.sql`
2. Insertar variables: `insert_all_variables.sql`
3. Insertar datos de prueba: `test_data.sql`
4. Ver datos: `SELECT * FROM v_measurements_detailed;`

---

### **validate_and_clean.sql** (9.9 KB)
**Propósito:** Herramientas para validar, limpiar y analizar datos
**Contenido:**
- 5 reportes detallados
- Validación de integridad
- Análisis de rendimiento
- Comandos de limpieza

**Cuándo usar:**
```bash
psql -U postgres -d transfusiones -f validate_and_clean.sql
```

**Reportes que genera:**
1. **Reporte 1:** Estructura (tablas, índices, vistas)
2. **Reporte 2:** Estadísticas (categorías, variables, registros)
3. **Reporte 3:** Validación (duplicados, totales incorrectos)
4. **Reporte 4:** Análisis (top categorías, distribución)
5. **Reporte 5:** Rendimiento (tamaño BD, índices)

**Comandos de limpieza incluidos (comentados):**
```sql
-- Limpiar todos los datos
DELETE FROM measurements;

-- Limpiar datos de un año
DELETE FROM measurements WHERE year = 2026;

-- Limpiar datos de un mes
DELETE FROM measurements WHERE month_id = ...;
```

---

### **install.sh** (6.5 KB)
**Propósito:** Script Bash para instalación automatizada completa
**Características:**
- Verifica PostgreSQL
- Crea base de datos
- Ejecuta scripts SQL
- Importa datos (opcional)
- Genera resumen

**Uso:**
```bash
# Dar permisos
chmod +x install.sh

# Ejecutar
./install.sh

# Con variables personalizadas
DB_NAME=mi_bd DB_USER=miusuario ./install.sh
```

**Variables de entorno:**
```bash
DB_HOST=localhost          # Host de PostgreSQL
DB_PORT=5432              # Puerto de PostgreSQL
DB_USER=postgres          # Usuario
DB_PASSWORD=postgres      # Contraseña
DB_NAME=transfusiones     # Nombre de la BD
EXCEL_FILE=2026.xlsx      # Archivo Excel a importar
```

**Pasos que realiza:**
1. Verifica PostgreSQL
2. Verifica conexión
3. Crea base de datos (con confirmación)
4. Ejecuta `database_schema.sql`
5. Ejecuta `insert_all_variables.sql`
6. Verifica instalación
7. Ofrece importar datos del Excel
8. Muestra resumen final

---

## 4. Documentación

### **README.md** (13 KB)
**Propósito:** Guía completa de inicio y uso
**Contenido:**
- Inicio rápido (3 pasos)
- Descripción de archivos
- Estructura de la BD
- Las 59 categorías
- Vistas disponibles
- Ejemplos de consultas
- Operaciones comunes
- Escalabilidad
- Solución de problemas

**Lectura:** 15-20 minutos

---

### **DATABASE_DOCUMENTATION.md** (20 KB)
**Propósito:** Referencia técnica completa de todas las tablas
**Contenido:**
- Descripción detallada de cada tabla
- Todas las columnas y tipos de datos
- Relaciones entre tablas
- Restricciones y validaciones
- Cómo insertar datos
- 20+ ejemplos de consultas
- Funciones disponibles
- Mantenimiento
- Mejores prácticas

**Lectura:** 30-40 minutos (consulta)

---

### **CONSULTAS_SQL.md** (16 KB)
**Propósito:** 30+ ejemplos de consultas SQL útiles
**Contenido:**
- Consultas básicas
- Análisis por variables
- Análisis temporal
- Comparativas
- Reportes avanzados
- Validación de datos
- Optimización
- Exportación de datos

**Lectura:** Consultar según necesidad

---

### **all_variables.txt** (26 KB)
**Propósito:** Listado legible de TODAS las 652 variables
**Contenido:**
```
1. Centro Transfuncional (9 variables)
2. Estudios de Laboratorio transmisibles y no transmisibles (13 variables)
3. Estudios de Laboratorio (14 variables)
... (59 categorías totales)
```

**Uso:** Referencia rápida de variables disponibles

---

### **all_variables.json** (25 KB)
**Propósito:** Listado estructurado de variables en formato JSON
**Formato:**
```json
{
  "total_subsections": 59,
  "total_variables": 652,
  "subsections": [
    {
      "name": "Centro Transfuncional",
      "num_variables": 9,
      "variables": [...]
    }
  ]
}
```

**Uso:** Programático (cargar en aplicaciones, APIs, etc.)

---

## 5. Datos de Referencia

### **all_variables.json** (25 KB)
Ver sección [4. Documentación](#4-documentación)

### **all_variables.txt** (26 KB)
Ver sección [4. Documentación](#4-documentación)

---

## 🚀 GUÍA RÁPIDA DE INSTALACIÓN

### Opción 1: Automatizada (Recomendado)
```bash
chmod +x install.sh
./install.sh
```

### Opción 2: Manual paso a paso
```bash
# Paso 1: Crear BD
createdb -U postgres transfusiones

# Paso 2: Crear estructura
psql -U postgres -d transfusiones -f database_schema.sql

# Paso 3: Insertar 652 variables
psql -U postgres -d transfusiones -f insert_all_variables.sql

# Paso 4: Insertar datos de prueba (opcional)
psql -U postgres -d transfusiones -f test_data.sql

# Paso 5: Importar datos desde Excel
python3 import_advanced.py 2026.xlsx

# Paso 6: Validar
psql -U postgres -d transfusiones -f validate_and_clean.sql
```

---

## 📊 ESTRUCTURA DE ARCHIVOS

```
├── SQL Scripts
│   ├── database_schema.sql              (Crear estructura)
│   ├── insert_all_variables.sql         (Insertar 652 variables)
│   ├── test_data.sql                    (Datos de prueba)
│   └── validate_and_clean.sql           (Validar y limpiar)
│
├── Python Scripts
│   ├── import_advanced.py               (Importar datos - Recomendado)
│   └── import_data.py                   (Importar datos - Básico)
│
├── Bash Scripts
│   └── install.sh                       (Instalación automatizada)
│
├── Documentación
│   ├── README.md                        (Guía general)
│   ├── DATABASE_DOCUMENTATION.md        (Referencia técnica)
│   ├── CONSULTAS_SQL.md                 (30+ ejemplos)
│   └── INDEX.md                         (Este archivo)
│
└── Datos de Referencia
    ├── all_variables.json               (Variables en JSON)
    └── all_variables.txt                (Variables en texto)
```

---

## 🎯 FLUJO DE TRABAJO TÍPICO

```
1. Instalación (primera vez)
   └─ install.sh → Crea BD y carga estructu

2. Importar datos
   └─ import_advanced.py 2026.xlsx → Importa 652 variables

3. Validar
   └─ validate_and_clean.sql → Genera reportes

4. Usar
   ├─ Consultas SQL directas
   ├─ Vistas predefinidas
   └─ Exportar a reportes
```

---

## 💾 TAMAÑO DE ARCHIVOS

| Archivo | Tamaño | Contenido |
|---------|--------|----------|
| database_schema.sql | 13 KB | 1 tabla + estructura |
| insert_all_variables.sql | 202 KB | 652 variables |
| import_advanced.py | 22 KB | Script Python |
| import_data.py | 15 KB | Script Python (básico) |
| install.sh | 6.5 KB | Script Bash |
| test_data.sql | 7.3 KB | 30 registros de prueba |
| validate_and_clean.sql | 9.9 KB | Herramientas de validación |
| README.md | 13 KB | Guía general |
| DATABASE_DOCUMENTATION.md | 20 KB | Referencia técnica |
| CONSULTAS_SQL.md | 16 KB | Ejemplos SQL |
| all_variables.json | 25 KB | Variables (JSON) |
| all_variables.txt | 26 KB | Variables (TXT) |
| **TOTAL** | **~370 KB** | Todos los archivos |

---

## ✅ CHECKLIST DE INSTALACIÓN

- [ ] PostgreSQL instalado
- [ ] Base de datos creada (`createdb transfusiones`)
- [ ] `database_schema.sql` ejecutado
- [ ] `insert_all_variables.sql` ejecutado (652 variables)
- [ ] Datos importados (opcional)
- [ ] `test_data.sql` ejecutado (verificación)
- [ ] `validate_and_clean.sql` ejecutado (validación)
- [ ] Vistas funcionando correctamente
- [ ] Conexión desde aplicación exitosa

---

## 🔧 SOLUCIÓN RÁPIDA DE PROBLEMAS

| Problema | Solución |
|----------|----------|
| "Database does not exist" | `createdb -U postgres transfusiones` |
| "Relation does not exist" | Ejecutar `database_schema.sql` primero |
| "Foreign key constraint" | Verificar IDs en tablas de referencia |
| Variables no aparecen | Ejecutar `insert_all_variables.sql` |
| Import muy lento | Normal con 652 variables, toma 2-5 min |
| Datos duplicados | Usar `ON CONFLICT` en INSERT |

---

## 📞 REFERENCIAS RÁPIDAS

### Conectarse a la BD
```bash
psql -U postgres -d transfusiones
```

### Ver estructura
```sql
SELECT * FROM v_variables_inventory;
```

### Ver datos
```sql
SELECT * FROM v_measurements_detailed LIMIT 10;
```

### Exportar a CSV
```bash
psql -U postgres -d transfusiones -c \
  "COPY (SELECT * FROM v_measurements_detailed) TO STDOUT WITH CSV HEADER" \
  > datos.csv
```

---

## 🎓 RECOMENDACIONES DE LECTURA

**Para comenzar:**
1. Lee `README.md` (5 min)
2. Ejecuta `install.sh` (5 min)
3. Lee ejemplos en `CONSULTAS_SQL.md` (15 min)

**Para profundizar:**
1. Lee `DATABASE_DOCUMENTATION.md` (30 min)
2. Experimenta con consultas SQL
3. Crea tus propias vistas

**Para administrar:**
1. Usa `validate_and_clean.sql` regularmente
2. Haz backups de la BD
3. Monitorea el tamaño de la BD

---

## 📊 CAPACIDAD DE LA BASE DE DATOS

| Métrica | Valor |
|---------|-------|
| **Categorías** | 59 |
| **Variables** | 652 |
| **Meses por año** | 12 |
| **Géneros** | 3 |
| **Registros por año** | 23,472 |
| **Registros en 5 años** | 117,360 |
| **Tamaño BD vacía** | ~10 MB |
| **Tamaño con 1 año** | ~50 MB |
| **Tamaño con 5 años** | ~250 MB |

---

## ✨ CARACTERÍSTICAS DESTACADAS

✅ **652 variables** en 59 categorías  
✅ **Normalizado** (sin redundancia)  
✅ **Escalable** (agrega variables sin cambiar estructura)  
✅ **Rápido** (9 índices optimizados)  
✅ **Seguro** (integridad referencial)  
✅ **Flexible** (múltiples hospitales)  
✅ **Reportable** (4 vistas predefinidas)  
✅ **Validable** (función de integridad)  

---

## 📅 FECHA Y VERSIÓN

- **Versión:** 2.0 (Completa)
- **Fecha:** 2026
- **Compatible con:** PostgreSQL 12+
- **Variables:** 652 en 59 categorías

---

**¡Tu base de datos está lista para usar! 🚀**

Para comenzar, lee `README.md` o ejecuta `install.sh`.

