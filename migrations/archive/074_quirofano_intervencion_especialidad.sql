-- ============================================================
-- 074_quirofano_intervencion_especialidad.sql
--
-- El formulario de Quirófano exige "Especialidad" (requerida) y la
-- usa para filtrar el catálogo de procedimientos, pero el dato no se
-- persistía en ningún lado: no había columna, ni campo en los schemas,
-- ni en el payload del frontend.
--
-- Esta migración normaliza el dato: agrega `especialidad_id` a
-- `intervenciones_quirurgicas` como FK a `especialidades(id)`.
-- Es ADITIVA e IDEMPOTENTE (se puede aplicar N veces sin efectos).
--
-- Resulta de continuación del rango consolidado en 032 (031→073).
-- ============================================================

BEGIN;

-- 1) Columna (aditiva)
ALTER TABLE intervenciones_quirurgicas
    ADD COLUMN IF NOT EXISTS especialidad_id integer;

-- 2) FK a especialidades (idempotente vía catálogo de constraints)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_intervenciones_quirurgicas_especialidad'
    ) THEN
        ALTER TABLE intervenciones_quirurgicas
            ADD CONSTRAINT fk_intervenciones_quirurgicas_especialidad
            FOREIGN KEY (especialidad_id)
            REFERENCES especialidades(id)
            ON DELETE SET NULL;
    END IF;
END$$;

-- 3) Índice para filtros/reportes por especialidad
CREATE INDEX IF NOT EXISTS idx_interv_especialidad
    ON intervenciones_quirurgicas(especialidad_id);

COMMIT;
