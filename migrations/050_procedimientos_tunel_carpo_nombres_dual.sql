-- ============================================================
-- 050_procedimientos_tunel_carpo_nombres_dual.sql
-- Mantiene UN SOLO procedimiento (id 38 / cat 37) pero con
-- nombre canónico dual que cubre ambas variantes:
--
--   Nombre: "Liberación de Túnel Carpiano"
--   Descripción: incluye "Descompresión del Nervio Mediano"
--
-- Esto deja claro que el procedimiento cubre ambos términos
-- clínicos sin crear duplicados.
-- ============================================================

BEGIN;

UPDATE procedimientos
SET nombre = 'Liberación de Túnel Carpiano',
    abreviatura = 'LTC',
    descripcion = 'Descompresión del Nervio Mediano. Apertura del retináculo flexor para liberar la presión sobre el nervio mediano a nivel del carpo.'
WHERE id = 38;

UPDATE catalogo_procedimientos
SET nombre = 'Liberación de Túnel Carpiano',
    abreviatura = 'LTC',
    descripcion = 'Descompresión del Nervio Mediano. Apertura del retináculo flexor para liberar la presión sobre el nervio mediano a nivel del carpo.'
WHERE id = 37;

COMMIT;