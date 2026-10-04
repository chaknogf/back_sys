-- ============================================================
-- 064_procedimientos_amputacion_unificada.sql
-- Fusiona TODAS las variantes de amputación en un único
-- procedimiento canónico: "Amputación" (AMP, id 36).
--
-- Se absorben:
--   id 146 ADD  "Amputación de Dedo"           → 2 refs
--   id 120 ARD  "Amputación en Raqueta de Dedo" → 1 ref
--   id 138 ADM  "Amputación de Muñeca"          → 2 refs
--   id 147 ASC  "Amputación Supracondílea"      → 1 ref
--   id 162 AICA "Amputación Infracondílea"      → 1 ref
--
-- Total: 7 referencias migradas al id 36 (AMP).
-- ============================================================

BEGIN;

UPDATE catalogo_procedimientos
SET descripcion = 'Amputación de extremidad o segmento (dedo, mano, muñeca, supracondílea, infracondílea, raqueta).'
WHERE id = 36;

DO $$
DECLARE
    ganador CONSTANT INT := 36;
    perdedor INT;
    cnt INT;
BEGIN
    FOR perdedor IN SELECT unnest(ARRAY[146, 120, 138, 147, 162]) LOOP
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'Amputación: % absorbido por AMP (% refs)', perdedor, cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

COMMIT;