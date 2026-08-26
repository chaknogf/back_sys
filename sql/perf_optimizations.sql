-- =============================================================
-- Optimizaciones de rendimiento para búsqueda de pacientes
-- Ejecutar contra la base de datos 'hospital'
-- =============================================================

-- 1. Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- 2. Función wrapper para unaccent (si no existe)
CREATE OR REPLACE FUNCTION f_unaccent(text)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT unaccent($1)
$$;

-- 3. Índice GIN trigram sobre la expresión que usa la búsqueda
--    Coincide exactamente con: unaccent(lower(nombre_completo))
--    Permite ILIKE con wildcards en ambos lados (%patrón%)
DROP INDEX IF EXISTS idx_paciente_nombre_trgm;
CREATE INDEX idx_paciente_nombre_trgm_expr
    ON pacientes
    USING gin (f_unaccent(lower(nombre_completo)) gin_trgm_ops);

-- 4. Índice parcial para búsquedas por estado (ya existe, verificar)
-- CREATE INDEX IF NOT EXISTS idx_paciente_estado ON pacientes(estado);

-- 5. Índice para expediente con ILIKE (evita seq scan en búsquedas mixtas)
CREATE INDEX IF NOT EXISTS idx_paciente_expediente_trgm
    ON pacientes
    USING gin (expediente gin_trgm_ops)
    WHERE expediente IS NOT NULL;

-- 6. Stats actualizadas para el query planner
ANALYZE pacientes;
