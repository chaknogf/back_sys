-- =============================================================
-- 019 - Recrear unaccent + f_unaccent tras pg_restore
-- Sin esta migración la búsqueda de pacientes (ilike + trigram)
-- falla después de restaurar la BD 'hospital'.
-- Ver: modules/pacientes/service.py:47, sql/recrear_unaccent.sql
-- =============================================================

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE OR REPLACE FUNCTION public.f_unaccent(text)
RETURNS text
LANGUAGE sql
IMMUTABLE
STRICT
PARALLEL SAFE
AS $$
    SELECT public.unaccent('public.unaccent', $1);
$$;

-- Mantener compatibilidad con código que usa f_unaccent sin schema
CREATE OR REPLACE FUNCTION f_unaccent(text)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT public.f_unaccent($1);
$$;

DROP INDEX IF EXISTS idx_paciente_nombre_trgm;
CREATE INDEX IF NOT EXISTS idx_paciente_nombre_trgm_expr
    ON pacientes USING gin (f_unaccent(lower(nombre_completo)) gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_pacientes_nombre_norm_trgm
    ON pacientes USING gin ((public.f_unaccent(lower(nombre_completo))) gin_trgm_ops);

ANALYZE pacientes;
