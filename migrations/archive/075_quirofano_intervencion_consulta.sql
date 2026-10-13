-- ============================================================
-- 075_quirofano_intervencion_consulta.sql
--
-- Permite ligar una intervención quirúrgica a la consulta de
-- hospitalización concreta que la originó. Antes solo se guardaba
-- `paciente_id`/`expediente`, así que era imposible saber qué consulta
-- ya tenía una intervención registrada (el listado de quirófano quiere
-- marcar esos pacientes con un indicador).
--
-- Agrega `intervenciones_quirurgicas.consulta_id` como FK a
-- `consultas(id)`. Es ADITIVA e IDEMPOTENTE (se puede aplicar N veces).
--
-- Continúa el rango consolidado en 032 (031→073) y 074.
-- ============================================================

BEGIN;

-- 1) Columna (aditiva)
ALTER TABLE intervenciones_quirurgicas
    ADD COLUMN IF NOT EXISTS consulta_id integer;

-- 2) FK a consultas (idempotente vía catálogo de constraints)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_intervenciones_quirurgicas_consulta'
    ) THEN
        ALTER TABLE intervenciones_quirurgicas
            ADD CONSTRAINT fk_intervenciones_quirurgicas_consulta
            FOREIGN KEY (consulta_id)
            REFERENCES consultas(id)
            ON DELETE SET NULL;
    END IF;
END$$;

-- 3) Índice para filtrar por consulta (indicador del listado)
CREATE INDEX IF NOT EXISTS idx_interv_consulta
    ON intervenciones_quirurgicas(consulta_id);

COMMIT;
