#!/bin/bash

# ============================================================================
# SCRIPT DE INSTALACIÓN RÁPIDA
# Base de Datos Normalizada - Hospital General Tipo I de Tecpán Guatemala
# ============================================================================

set -e  # Detener en primer error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "============================================================================"
echo "🏥 INSTALADOR RÁPIDO - BASE DE DATOS NORMALIZADA"
echo "Hospital General Tipo I de Tecpán Guatemala"
echo "============================================================================"
echo -e "${NC}"

# Variables de configuración
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_NAME=${DB_NAME:-transfusiones}
EXCEL_FILE=${EXCEL_FILE:-2026.xlsx}

echo -e "${YELLOW}📋 Configuración:${NC}"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   Usuario: $DB_USER"
echo "   Base de datos: $DB_NAME"
echo "   Archivo Excel: $EXCEL_FILE"
echo ""

# Paso 1: Verificar PostgreSQL
echo -e "${BLUE}1. Verificando PostgreSQL...${NC}"
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL no está instalado${NC}"
    echo "   Instálalo con: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi
echo -e "${GREEN}✅ PostgreSQL encontrado${NC}"

# Paso 2: Verificar conexión
echo -e "${BLUE}2. Verificando conexión...${NC}"
if ! PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -l &> /dev/null; then
    echo -e "${RED}❌ No se puede conectar a PostgreSQL${NC}"
    echo "   Verifica los datos de conexión"
    exit 1
fi
echo -e "${GREEN}✅ Conexión exitosa${NC}"

# Paso 3: Crear base de datos
echo -e "${BLUE}3. Creando base de datos '$DB_NAME'...${NC}"
if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo -e "${YELLOW}⚠️  Base de datos ya existe. ¿Deseas reemplazarla? (s/n)${NC}"
    read -r response
    if [[ $response == "s" ]]; then
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "DROP DATABASE $DB_NAME;" 2>/dev/null || true
        echo -e "${YELLOW}   Recreando base de datos...${NC}"
    else
        echo -e "${YELLOW}   Usando base de datos existente${NC}"
    fi
fi

if ! PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || true
fi
echo -e "${GREEN}✅ Base de datos '$DB_NAME' lista${NC}"

# Paso 4: Crear tablas y estructura
echo -e "${BLUE}4. Creando tablas y estructura...${NC}"
if [ -f "database_schema.sql" ]; then
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database_schema.sql > /dev/null 2>&1
    echo -e "${GREEN}✅ Tablas creadas${NC}"
else
    echo -e "${RED}❌ Archivo 'database_schema.sql' no encontrado${NC}"
    exit 1
fi

# Paso 5: Insertar variables
echo -e "${BLUE}5. Insertando 652 variables en 59 categorías...${NC}"
if [ -f "insert_all_variables.sql" ]; then
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f insert_all_variables.sql > /dev/null 2>&1
    echo -e "${GREEN}✅ Variables insertadas${NC}"
else
    echo -e "${YELLOW}⚠️  Archivo 'insert_all_variables.sql' no encontrado${NC}"
    echo "   Ejecuta manualmente: psql -U $DB_USER -d $DB_NAME -f insert_all_variables.sql"
fi

# Paso 6: Verificar instalación
echo -e "${BLUE}6. Verificando instalación...${NC}"
VAR_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tc "SELECT COUNT(*) FROM variables;" 2>/dev/null | tr -d ' ')
CAT_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tc "SELECT COUNT(*) FROM variable_categories;" 2>/dev/null | tr -d ' ')

if [ "$VAR_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Instalación verificada${NC}"
    echo "   Categorías: $CAT_COUNT"
    echo "   Variables: $VAR_COUNT"
else
    echo -e "${YELLOW}⚠️  Tablas creadas pero sin variables${NC}"
    echo "   Ejecuta: psql -U $DB_USER -d $DB_NAME -f insert_all_variables.sql"
fi

# Paso 7: Importar datos (opcional)
echo -e "${BLUE}7. Importar datos desde Excel${NC}"
if [ -f "$EXCEL_FILE" ]; then
    echo -e "${YELLOW}¿Deseas importar datos desde '$EXCEL_FILE'? (s/n)${NC}"
    read -r response
    if [[ $response == "s" ]]; then
        # Verificar Python
        if command -v python3 &> /dev/null; then
            echo "   Importando datos (esto puede tomar unos minutos)..."
            python3 import_advanced.py "$EXCEL_FILE" \
                --host $DB_HOST \
                --port $DB_PORT \
                --user $DB_USER \
                --password "$DB_PASSWORD" \
                --database $DB_NAME \
                --year 2026
            echo -e "${GREEN}✅ Importación completada${NC}"
        else
            echo -e "${YELLOW}⚠️  Python 3 no encontrado${NC}"
            echo "   Instálalo con: sudo apt-get install python3"
            echo "   Luego ejecuta: python3 import_advanced.py '$EXCEL_FILE'"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Archivo Excel no encontrado: $EXCEL_FILE${NC}"
    echo "   Coloca el archivo en el directorio actual"
fi

# Paso 8: Crear resumen
echo ""
echo -e "${GREEN}"
echo "============================================================================"
echo "✅ INSTALACIÓN COMPLETADA"
echo "============================================================================"
echo -e "${NC}"

echo -e "${YELLOW}Próximos pasos:${NC}"
echo ""
echo "1. Conectarte a la base de datos:"
echo -e "   ${BLUE}psql -U $DB_USER -d $DB_NAME${NC}"
echo ""
echo "2. Ver inventario de variables:"
echo -e "   ${BLUE}SELECT * FROM v_variables_inventory LIMIT 10;${NC}"
echo ""
echo "3. Ver datos importados:"
echo -e "   ${BLUE}SELECT * FROM v_measurements_detailed LIMIT 10;${NC}"
echo ""
echo "4. Crear un reporte mensual:"
echo -e "   ${BLUE}SELECT * FROM v_monthly_summary WHERE year = 2026 LIMIT 10;${NC}"
echo ""

echo -e "${YELLOW}Archivos de referencia:${NC}"
echo "   - DATABASE_DOCUMENTATION.md: Documentación completa"
echo "   - CONSULTAS_SQL.md: 30+ ejemplos de consultas"
echo "   - all_variables.txt: Listado de todas las 652 variables"
echo "   - README.md: Guía general"
echo ""

echo -e "${GREEN}¡Tu base de datos está lista para usar! 🚀${NC}"
echo ""
