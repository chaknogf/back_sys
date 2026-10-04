-- ============================================================
-- 036_procedimientos_regularizacion_fusionar_dedo.sql
-- Fusión final: id 167 (Regularización de Pulgar) y
-- id 173 (Regularización genérico) se absorben en id 163
-- (Regularización de Dedo).
--
-- Justificación clínica:
--   "Pulgar" anatómicamente es un dedo. En traumatología, una
--   regularización se realiza sobre una zona específica (casi
--   siempre dedo). Al usar solo "Dedo", se evitan ambigüedades
--   y se mantiene el registro histórico.
-- ============================================================

BEGIN;

DO $$
DECLARE
    ganador CONSTANT INT := 163;  -- RDD / Regularización de Dedo
    cnt INT;
BEGIN
    -- Absorber id 167 (Regularización de Pulgar)
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = 167;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'Pulgar (167) absorbido por Dedo (163): % referencias migradas', cnt;
    DELETE FROM procedimientos WHERE id = 167;

    -- Absorber id 173 (Regularización genérico)
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = 173;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'Genérico (173) absorbido por Dedo (163): % referencias migradas', cnt;
    DELETE FROM procedimientos WHERE id = 173;
END $$;

COMMIT;