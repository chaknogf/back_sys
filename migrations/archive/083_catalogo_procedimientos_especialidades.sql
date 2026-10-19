-- ============================================================
-- 083_catalogo_procedimientos_especialidades.sql
-- Habilita que un procedimiento del catálogo maestro se asocie a
-- VARIAS especialidades (relación N:M), en lugar de una sola
-- `especialidad_ref`.
--
-- Crea la tabla puente `catalogo_procedimientos_especialidades`
-- y migra las asignaciones existentes: cada `especialidad_ref`
-- no nula se convierte en una fila de la tabla puente.
--
-- Se conserva la columna `especialidad_ref` como referencia
-- principal (la primera de la lista) por compatibilidad con los
-- consumidores actuales.
--
-- Idempotente: CREATE ... IF NOT EXISTS e INSERT ... ON CONFLICT.
-- ============================================================

BEGIN;

CREATE TABLE IF NOT EXISTS public.catalogo_procedimientos_especialidades (
    id SERIAL PRIMARY KEY,
    id_catalogo_procedimiento INTEGER NOT NULL
        REFERENCES public.catalogo_procedimientos(id) ON DELETE CASCADE,
    id_especialidad INTEGER NOT NULL
        REFERENCES public.especialidades(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uq_cat_proc_esp UNIQUE (id_catalogo_procedimiento, id_especialidad)
);

CREATE INDEX IF NOT EXISTS idx_cat_proc_esp_proc
    ON public.catalogo_procedimientos_especialidades(id_catalogo_procedimiento);

CREATE INDEX IF NOT EXISTS idx_cat_proc_esp_esp
    ON public.catalogo_procedimientos_especialidades(id_especialidad);

-- Migrar asignaciones existentes (una por cada especialidad_ref no nula).
INSERT INTO public.catalogo_procedimientos_especialidades
    (id_catalogo_procedimiento, id_especialidad)
SELECT id, especialidad_ref
FROM public.catalogo_procedimientos
WHERE especialidad_ref IS NOT NULL
ON CONFLICT ON CONSTRAINT uq_cat_proc_esp DO NOTHING;

COMMIT;
