-- ============================================================
-- 038_procedimientos_regularizacion_abreviatura.sql
-- Cambia la abreviatura del procedimiento id 163 (Regularización)
-- de "RDD" → "REG".
--
-- Justificación:
--   El nombre del procedimiento es ahora genérico
--   ("Regularización"), por lo que la abreviatura también debe
--   reflejar la acción clínica (REG = Regularización), no la zona
--   intervenida (que se registra aparte vía `area_cuerpo_intervenida`).
-- ============================================================

BEGIN;

UPDATE procedimientos
SET abreviatura = 'REG'
WHERE id = 163
  AND abreviatura <> 'REG';

COMMIT;