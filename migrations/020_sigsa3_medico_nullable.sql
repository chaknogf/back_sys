-- Migration 020: hacer medico_id nullable en sigsa3_registros
-- Permite normalizar registros sin medico_id asociado.

BEGIN;

-- 1. Backfill: vincular personal_salud → medico donde sea posible
UPDATE sigsa3_registros r
SET medico_id = ps.medico_id
FROM personal_salud ps
WHERE r.medico_id IS NULL
  AND r.personal_salud_id = ps.id
  AND ps.medico_id IS NOT NULL;

-- 2. Permitir NULL en medico_id
ALTER TABLE sigsa3_registros
    ALTER COLUMN medico_id DROP NOT NULL;

COMMIT;
