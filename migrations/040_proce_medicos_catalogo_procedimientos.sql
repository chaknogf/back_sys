-- ============================================================
-- 040_proce_medicos_catalogo_procedimientos.sql
-- Agrega la columna `id_catalogo_procedimiento` en
-- `proce_medicos` como FK opcional al nuevo catálogo maestro.
--
-- Estrategia:
--   1. Crear la columna FK (nullable inicialmente).
--   2. Backfill: para cada registro con `id_procedimiento`
--      apuntando al catálogo legacy, buscar su equivalente en
--      `catalogo_procedimientos` por nombre y llenar la nueva
--      columna.
--   3. NO se elimina `id_procedimiento` todavía: queda como
--      columna legacy por compatibilidad. La aplicación puede
--      ir migrando gradualmente a la nueva FK.
-- ============================================================

BEGIN;

-- 1) Nueva columna FK
ALTER TABLE public.proce_medicos
    ADD COLUMN IF NOT EXISTS id_catalogo_procedimiento INTEGER;

-- 2) FK opcional
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'proce_medicos_id_catalogo_procedimiento_fkey'
    ) THEN
        ALTER TABLE public.proce_medicos
        ADD CONSTRAINT proce_medicos_id_catalogo_procedimiento_fkey
        FOREIGN KEY (id_catalogo_procedimiento)
        REFERENCES public.catalogo_procedimientos(id)
        ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_pm_catalogo
    ON public.proce_medicos(id_catalogo_procedimiento);

-- 3) Backfill: copiar referencias desde id_procedimiento legacy
-- hacia id_catalogo_procedimiento usando nombre como puente.
UPDATE public.proce_medicos pm
SET id_catalogo_procedimiento = cp.id
FROM public.procedimientos p,
     public.catalogo_procedimientos cp
WHERE pm.id_procedimiento = p.id
  AND cp.nombre = p.nombre
  AND pm.id_catalogo_procedimiento IS NULL;

COMMIT;

-- Verificación
SELECT
    COUNT(*) FILTER (WHERE id_catalogo_procedimiento IS NOT NULL) AS con_nuevo_catalogo,
    COUNT(*) FILTER (WHERE id_catalogo_procedimiento IS NULL)     AS sin_nuevo_catalogo,
    COUNT(*) AS total
FROM public.proce_medicos;