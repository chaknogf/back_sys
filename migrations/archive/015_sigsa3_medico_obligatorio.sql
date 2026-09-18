-- Migration 015: exigir medico_id en sigsa3_registros (aplicar DESPUÉS de 014)
-- La normalización ahora solo migra registros con paciente_id + medico_id.
-- Se sanean los registros previos con medico_id NULL y luego se impone NOT NULL.

BEGIN;

-- 1. Rellenar medico_id desde la tabla puente personal_salud.medico_id donde sea posible.
UPDATE sigsa3_registros r
SET medico_id = ps.medico_id
FROM personal_salud ps
WHERE r.medico_id IS NULL
  AND r.personal_salud_id = ps.id
  AND ps.medico_id IS NOT NULL;

-- 2. Eliminar los que aun no tengan medico_id (fueron migrados bajo la regla anterior,
--    que permitía solo personal_salud_id; ya no son válidos).
DELETE FROM sigsa3_registros
WHERE medico_id IS NULL;

-- 3. Imponer NOT NULL.
ALTER TABLE sigsa3_registros
    ALTER COLUMN medico_id SET NOT NULL;

COMMIT;