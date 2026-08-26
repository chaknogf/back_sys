-- ============================================================
-- Índices para optimizar concurrencia y escalabilidad
-- Ejecutar: psql -d hospital -f scripts/indices_concurrencia.sql
-- ============================================================

BEGIN;

-- 1. Dashboard totales: COUNT(*) con filtro de fecha
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_consultas_fecha_tipo
    ON consultas (fecha_consulta, tipo_consulta)
    WHERE activo = TRUE;

-- 2. Dashboard totales: conteo de pacientes activos
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pacientes_estado
    ON pacientes (estado);

-- 3. Búsqueda de consultas: JOIN con pacientes por paciente_id
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_consultas_paciente_activo
    ON consultas (paciente_id)
    WHERE activo = TRUE;

-- 4. Búsqueda de consultas: filtro por expediente en consultas
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_consultas_expediente
    ON consultas (expediente)
    WHERE expediente IS NOT NULL;

-- 5. Búsqueda de pacientes: filtro por expediente
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pacientes_expediente
    ON pacientes (expediente)
    WHERE expediente IS NOT NULL AND expediente <> '';

-- 6. Procedimientos: agregación por fecha, especialidad, servicio
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_proce_medicos_fecha
    ON proce_medicos (fecha, especialidad, lugar_servicio);

-- 7. Procedimientos: JOIN con catálogo
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_proce_medicos_id_procedimiento
    ON proce_medicos (id_procedimiento);

-- 8. SIGSA-3: filtros frecuentes (fecha + tipo + especialidad)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sigsa3_fecha_tipo_esp
    ON sigsa3 (fecha_consulta, tipo_consulta, especialidad);

-- 9. GIN para búsqueda de texto completo en pacientes (nombre_completo)
--    (si no existe ya por el trigger trg_set_nombre_completo)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pacientes_nombre_completo_trgm
    ON pacientes USING gin (nombre_completo gin_trgm_ops);

-- 10. GIN para filtrar por JSONB (datos_extra)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pacientes_datos_extra_gin
    ON pacientes USING gin (datos_extra jsonb_path_ops);

-- 11. Consultas: filtro por último estado (admision, archivo, etc)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_consultas_ultimo_estado
    ON consultas (ultimo_estado)
    WHERE ultimo_estado IS NOT NULL;

-- 12. Censo camas: búsqueda por servicio + fecha
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_censo_camas_servicio_fecha
    ON censo_camas (servicio_id, fecha);

-- 13. GIN trigram para búsqueda CIE-10
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cie10_descripcion_trgm
    ON cie10_catalogo USING gin (descripcion gin_trgm_ops);

-- 14. Función IMMUTABLE de unaccent (unaccent() es STABLE y no se puede indexar).
--     Las queries de pacientes y consultas usan f_unaccent(lower(nombre_completo));
--     la expresión del índice debe coincidir exactamente para que el planner la use.
CREATE OR REPLACE FUNCTION public.f_unaccent(text)
RETURNS text
LANGUAGE sql
IMMUTABLE
STRICT
PARALLEL SAFE
AS $$
    SELECT public.unaccent('public.unaccent', $1);
$$;

-- 15. GIN trigram sobre el nombre normalizado (lower + unaccent)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pacientes_nombre_norm_trgm
    ON pacientes USING gin ((public.f_unaccent(lower(nombre_completo))) gin_trgm_ops);

ANALYZE pacientes;

COMMIT;

-- Verificar índices creados
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('consultas', 'pacientes', 'proce_medicos', 'sigsa3', 'censo_camas', 'nacimientos')
ORDER BY tablename, indexname;
