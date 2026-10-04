-- ============================================================
-- 042_proce_medicos_area_cuerpo.sql
-- Conecta cada `proce_medicos` (procedimiento realizado) con
-- el área del cuerpo intervenida (catálogo
-- `area_cuerpo_intervenida`). Opcional, FK nullable.
--
-- Justificación clínica:
--   "Osteosíntesis de radio" no es igual a "Osteosíntesis de
--   cúbito". Registrar el área intervenida (radio, cúbito,
--   cadera, dedo, etc.) es fundamental para estadísticas y
--   auditoría clínica.
-- ============================================================

BEGIN;

ALTER TABLE public.proce_medicos
    ADD COLUMN IF NOT EXISTS id_area_cuerpo_intervenida INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'proce_medicos_id_area_cuerpo_intervenida_fkey'
    ) THEN
        ALTER TABLE public.proce_medicos
        ADD CONSTRAINT proce_medicos_id_area_cuerpo_intervenida_fkey
        FOREIGN KEY (id_area_cuerpo_intervenida)
        REFERENCES public.area_cuerpo_intervenida(id)
        ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_pm_area_cuerpo
    ON public.proce_medicos(id_area_cuerpo_intervenida);

-- Backfill: para los procedimientos que ya tienen área(s)
-- asignada(s) en `procedimientos_area_cuerpo`, propagamos
-- la PRIMERA al registro histórico de proce_medicos.
UPDATE public.proce_medicos pm
SET id_area_cuerpo_intervenida = sub.id_area_cuerpo
FROM (
    SELECT DISTINCT ON (pac.id_procedimiento)
        pac.id_procedimiento,
        pac.id_area_cuerpo
    FROM public.procedimientos_area_cuerpo pac
    ORDER BY pac.id_procedimiento, pac.id_area_cuerpo
) sub
WHERE pm.id_catalogo_procedimiento IS NOT NULL
  AND pm.id_area_cuerpo_intervenida IS NULL
  AND pm.id_catalogo_procedimiento = sub.id_procedimiento;

COMMIT;

-- Verificación
SELECT
    COUNT(*) FILTER (WHERE id_area_cuerpo_intervenida IS NOT NULL) AS con_area,
    COUNT(*) FILTER (WHERE id_area_cuerpo_intervenida IS NULL)     AS sin_area,
    COUNT(*) AS total
FROM public.proce_medicos;