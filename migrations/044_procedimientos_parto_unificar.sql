-- ============================================================
-- 044_procedimientos_parto_unificar.sql
-- Fusiona "Parto Vaginal" (id 47) dentro de
-- "Parto Eutócico Simple" (id 97).
--
-- Decisión clínica: ambos términos describen el mismo
-- procedimiento. Se conserva la nomenclatura institucional
-- "Parto Eutócico Simple (Parto Vaginal)" como nombre canónico.
-- ============================================================

BEGIN;

-- 1) Renombrar id 97 al nombre canónico combinado
UPDATE procedimientos
SET nombre = 'Parto Eutócico Simple (Parto Vaginal)'
WHERE id = 97;

-- 2) Absorber id 47 (Parto Vaginal) en id 97
DO $$
DECLARE
    ganador CONSTANT INT := 97;   -- Parto Eutócico Simple (Parto Vaginal)
    perdedor CONSTANT INT := 47;  -- Parto Vaginal
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador,
        id_catalogo_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'Parto Vaginal (id %) absorbido por Parto Eutócico Simple (id %): % referencias migradas',
        perdedor, ganador, cnt;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;

COMMIT;