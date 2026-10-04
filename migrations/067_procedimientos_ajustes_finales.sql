-- ============================================================
-- 067_procedimientos_ajustes_finales.sql
-- Ajustes finales de capitalización para casos especiales.
-- VAC es marca comercial — debe ir en MAYÚSCULAS.
-- ============================================================

BEGIN;

UPDATE catalogo_procedimientos
SET nombre = 'VAC'
WHERE id = 12;

COMMIT;