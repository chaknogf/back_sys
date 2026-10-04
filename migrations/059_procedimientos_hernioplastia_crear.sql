-- ============================================================
-- 059_procedimientos_hernioplastia_crear.sql
-- Crea el procedimiento "Hernioplastia" (HERP) en el catálogo
-- maestro y actualiza "Herniorrafia" (HERM) con descripción
-- clínica.
--
-- Son procedimientos distintos:
--   HERM "Herniorrafia"  → sutura directa de tejidos (sin malla)
--   HERP "Hernioplastia" → reparación con malla protésica
--
-- Ambos se mantienen como registros independientes.
-- ============================================================

BEGIN;

-- Actualizar HERM con descripción clínica
UPDATE catalogo_procedimientos
SET descripcion = 'Reparación quirúrgica de hernia mediante sutura directa de tejidos.'
WHERE id = 108;

-- Crear HERP si no existe
INSERT INTO catalogo_procedimientos
    (abreviatura, nombre, descripcion, anestesia, especialidad_ref, activo)
SELECT
    'HERP',
    'Hernioplastia',
    'Reparación quirúrgica de hernia con colocación de malla protésica.',
    1,
    NULL,
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM catalogo_procedimientos WHERE abreviatura = 'HERP'
);

COMMIT;