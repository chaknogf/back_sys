-- ============================================================
-- 046_procedimientos_descripciones_resumidas.sql
-- Agrega descripciones clínicas concisas al catálogo maestro
-- para los procedimientos del ámbito traumatológico.
--
-- Estilo: una sola línea, max ~120 caracteres.
-- ============================================================

BEGIN;

UPDATE catalogo_procedimientos
SET descripcion = 'Corte parcial o total del tendón para liberar tensión y permitir su regeneración.'
WHERE nombre = 'Tenotomía';

UPDATE catalogo_procedimientos
SET descripcion = 'Reconstrucción plástica del tendón desgastado por inflamación crónica.'
WHERE nombre = 'Tenoplastia';

COMMIT;