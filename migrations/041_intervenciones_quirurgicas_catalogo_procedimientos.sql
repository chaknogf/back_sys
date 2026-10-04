-- ============================================================
-- 041_intervenciones_quirurgicas_catalogo_procedimientos.sql
-- Conecta `intervenciones_quirurgicas` (quirófano) al catálogo
-- maestro `catalogo_procedimientos`.
--
-- Las columnas `procedimiento_principal/2/3/4/5` son VARCHAR
-- (texto libre). Estrategia mixta:
--   1. Agregar columnas FK nuevas para los 5 slots:
--      procedimiento_principal_id ... procedimiento_5_id
--   2. Backfill: mapear por nombre a catalogo_procedimientos.
--   3. Mantener las columnas legacy VARCHAR (no se eliminan aún)
--      para no romper nada durante la transición.
-- ============================================================

BEGIN;

-- 1) Nuevas columnas FK (nullable)
ALTER TABLE public.intervenciones_quirurgicas
    ADD COLUMN IF NOT EXISTS procedimiento_principal_id INTEGER,
    ADD COLUMN IF NOT EXISTS procedimiento_2_id INTEGER,
    ADD COLUMN IF NOT EXISTS procedimiento_3_id INTEGER,
    ADD COLUMN IF NOT EXISTS procedimiento_4_id INTEGER,
    ADD COLUMN IF NOT EXISTS procedimiento_5_id INTEGER;

-- 2) FKs al catálogo maestro
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_principal_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_principal_id_fkey
        FOREIGN KEY (procedimiento_principal_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_2_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_2_id_fkey
        FOREIGN KEY (procedimiento_2_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_3_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_3_id_fkey
        FOREIGN KEY (procedimiento_3_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_4_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_4_id_fkey
        FOREIGN KEY (procedimiento_4_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_5_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_5_id_fkey
        FOREIGN KEY (procedimiento_5_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_iq_proc_principal ON public.intervenciones_quirurgicas(procedimiento_principal_id);
CREATE INDEX IF NOT EXISTS idx_iq_proc_2        ON public.intervenciones_quirurgicas(procedimiento_2_id);
CREATE INDEX IF NOT EXISTS idx_iq_proc_3        ON public.intervenciones_quirurgicas(procedimiento_3_id);
CREATE INDEX IF NOT EXISTS idx_iq_proc_4        ON public.intervenciones_quirurgicas(procedimiento_4_id);
CREATE INDEX IF NOT EXISTS idx_iq_proc_5        ON public.intervenciones_quirurgicas(procedimiento_5_id);

-- 3) Backfill: para cada slot, mapear texto -> id catálogo
UPDATE public.intervenciones_quirurgicas iq
SET procedimiento_principal_id = cp.id
FROM public.catalogo_procedimientos cp
WHERE iq.procedimiento_principal IS NOT NULL
  AND cp.nombre = iq.procedimiento_principal
  AND iq.procedimiento_principal_id IS NULL;

UPDATE public.intervenciones_quirurgicas iq
SET procedimiento_2_id = cp.id
FROM public.catalogo_procedimientos cp
WHERE iq.procedimiento_2 IS NOT NULL
  AND cp.nombre = iq.procedimiento_2
  AND iq.procedimiento_2_id IS NULL;

UPDATE public.intervenciones_quirurgicas iq
SET procedimiento_3_id = cp.id
FROM public.catalogo_procedimientos cp
WHERE iq.procedimiento_3 IS NOT NULL
  AND cp.nombre = iq.procedimiento_3
  AND iq.procedimiento_3_id IS NULL;

UPDATE public.intervenciones_quirurgicas iq
SET procedimiento_4_id = cp.id
FROM public.catalogo_procedimientos cp
WHERE iq.procedimiento_4 IS NOT NULL
  AND cp.nombre = iq.procedimiento_4
  AND iq.procedimiento_4_id IS NULL;

UPDATE public.intervenciones_quirurgicas iq
SET procedimiento_5_id = cp.id
FROM public.catalogo_procedimientos cp
WHERE iq.procedimiento_5 IS NOT NULL
  AND cp.nombre = iq.procedimiento_5
  AND iq.procedimiento_5_id IS NULL;

COMMIT;

-- Verificación
SELECT
  COUNT(*) FILTER (WHERE procedimiento_principal_id IS NOT NULL) AS p1,
  COUNT(*) FILTER (WHERE procedimiento_2_id       IS NOT NULL) AS p2,
  COUNT(*) FILTER (WHERE procedimiento_3_id       IS NOT NULL) AS p3,
  COUNT(*) FILTER (WHERE procedimiento_4_id       IS NOT NULL) AS p4,
  COUNT(*) FILTER (WHERE procedimiento_5_id       IS NOT NULL) AS p5,
  COUNT(*) AS total
FROM public.intervenciones_quirurgicas;