-- ============================================================
-- 037_procedimientos_regularizacion_nombre_final.sql
-- Cambio de nombre final para id 163:
--   "Regularización de Dedo" → "Regularización"
--
-- Justificación:
--   El nombre del procedimiento queda como término clínico
--   genérico ("Regularización") y la zona del cuerpo
--   intervenida se indica en el área asociada
--   (`procedimientos_area_cuerpo` -> `area_cuerpo_intervenida`
--   con codigo DEDO_MANO / "Dedo de la mano").
--
-- No se elimina ningún registro: el id 163 sigue activo y
-- mantiene su asociación a la zona "Dedo de la mano".
-- ============================================================

BEGIN;

UPDATE procedimientos
SET nombre = 'Regularización'
WHERE id = 163
  AND nombre <> 'Regularización';

COMMIT;