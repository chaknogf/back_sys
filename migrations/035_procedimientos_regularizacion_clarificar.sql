-- ============================================================
-- 035_procedimientos_regularizacion_clarificar.sql
-- Aplica la opción C del análisis del id 173:
-- Renombra los 3 procedimientos "Regularización" para que su
-- intención sea explícita en el catálogo.
--
-- No se borra el id 173: queda como "Regularización (genérico)"
-- para usos donde el especialista aún no especifica zona.
-- ============================================================

BEGIN;

UPDATE procedimientos SET nombre = 'Regularización de Dedo'
WHERE id = 163 AND nombre <> 'Regularización de Dedo';

UPDATE procedimientos SET nombre = 'Regularización de Pulgar'
WHERE id = 167 AND nombre <> 'Regularización de Pulgar';

UPDATE procedimientos SET nombre = 'Regularización (genérico - requiere especificar zona)'
WHERE id = 173 AND nombre <> 'Regularización (genérico - requiere especificar zona)';

COMMIT;