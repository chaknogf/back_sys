-- ============================================================
-- 061_procedimientos_ajuste_injerto.sql
-- Corrección: el ganador del grupo de injertos debe ser TCIP
-- (Toma y Colocación de Injerto de Piel) y no CI genérico.
--
-- Acción:
--   1. Restaurar TCIP como nombre canónico más descriptivo.
--   2. Renombrar CI (id 205) → TCIP.
-- ============================================================

BEGIN;

UPDATE catalogo_procedimientos
SET nombre = 'Toma y Colocación de Injerto de Piel',
    abreviatura = 'TCIP',
    descripcion = 'Toma de injerto cutáneo del paciente o donante y colocación en zona receptora.'
WHERE id = 205;

COMMIT;