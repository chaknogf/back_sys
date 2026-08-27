-- =============================================================
-- Recrear extensiones unaccent + pg_trgm tras pg_restore
-- La BD 'hospital' pierde CREATE EXTENSION al restaurar sin --extensions
-- Ejecutar: psql -d hospital -f sql/recrear_unaccent.sql
-- Usado por: modules/pacientes/service.py:47 (f_unaccent)
-- =============================================================

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Wrapper IMMUTABLE obligatorio: unaccent() es STABLE y no se puede indexar
-- El índice GIN debe coincidir exactamente con f_unaccent(lower(nombre_completo))
CREATE OR REPLACE FUNCTION public.f_unaccent(text)
RETURNS text
LANGUAGE sql
IMMUTABLE
STRICT
PARALLEL SAFE
AS $$
    SELECT public.unaccent('public.unaccent', $1);
$$;

-- Alternativa simple (compatible con sql/perf_optimizations.sql:11):
-- CREATE OR REPLACE FUNCTION f_unaccent(text) RETURNS text LANGUAGE sql IMMUTABLE AS $$ SELECT unaccent($1) $$;

DROP INDEX IF EXISTS idx_paciente_nombre_trgm;
CREATE INDEX IF NOT EXISTS idx_paciente_nombre_trgm_expr
    ON pacientes USING gin (f_unaccent(lower(nombre_completo)) gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_pacientes_nombre_norm_trgm
    ON pacientes USING gin ((public.f_unaccent(lower(nombre_completo))) gin_trgm_ops);

ANALYZE pacientes;

-- Verificación
-- SELECT * FROM pg_extension WHERE extname IN ('unaccent','pg_trgm');
-- SELECT proname, provolatile FROM pg_proc WHERE proname = 'f_unaccent';
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'pacientes' AND indexname LIKE '%trgm%';
