-- 088_insumos_caracteristicas_cantidad_jsonb.sql
-- Parseo de campos crudos del catálogo de insumos:
--   insumos.caracteristicas (TEXT "Estado: X;  Grado: Y;  Uso: Z;") -> JSONB
--   presentaciones.cantidad_unidad (TEXT "250 Mililitro") -> NUMERIC + unidad

BEGIN;

-- 1) insumos: agregar columna JSONB para características parseadas
ALTER TABLE insumos
    ADD COLUMN IF NOT EXISTS caracteristicas_jsonb JSONB NOT NULL DEFAULT '{}'::jsonb;

-- Backfill básico: convierte "Estado: X;  Grado: Y;  Uso: Z;" a {"estado":..., "grado":..., "uso":...}
-- (heurística; el script de importación puede refinarlo).
UPDATE insumos
SET caracteristicas_jsonb = COALESCE(
    (
        SELECT jsonb_object_agg(lower(trim(m[1])), trim(m[2]))
        FROM regexp_matches(caracteristicas, '([^:;]+):\s*([^;]+)', 'g') AS m
    ),
    '{}'::jsonb
)
WHERE caracteristicas IS NOT NULL AND caracteristicas <> '';

CREATE INDEX IF NOT EXISTS idx_insumos_caracteristicas_jsonb
    ON insumos USING GIN (caracteristicas_jsonb);

-- 2) presentaciones: agregar valor numérico + unidad estandarizada
ALTER TABLE presentaciones
    ADD COLUMN IF NOT EXISTS cantidad_unidad_valor NUMERIC(14, 3),
    ADD COLUMN IF NOT EXISTS unidad_medida VARCHAR(30);

-- Backfill: extrae primer número y la unidad textual restante.
UPDATE presentaciones
SET
    cantidad_unidad_valor = NULLIF((regexp_match(cantidad_unidad, '([0-9]+(?:[.,][0-9]+)?)'))[1], '')::numeric,
    unidad_medida = NULLIF(trim(regexp_replace(cantidad_unidad, '^[0-9]+(?:[.,][0-9]+)?\s*', '')), '')
WHERE cantidad_unidad IS NOT NULL AND cantidad_unidad <> '';

CREATE INDEX IF NOT EXISTS idx_presentaciones_unidad_medida
    ON presentaciones (unidad_medida);

COMMIT;
