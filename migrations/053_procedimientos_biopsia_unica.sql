-- ============================================================
-- 053_procedimientos_biopsia_unica.sql
-- Fusiona TODAS las variantes de biopsia en un único
-- procedimiento "Biopsia" (BIOP), porque el usuario quiere
-- que solo exista una entrada canónica.
--
-- Se absorben:
--   id 65  BIOCER  "Biopsia Cervical"
--   id 206 BE      "Biopsia Endometrial"
--   id 279 BIOMAMA "BIOPSIA Y ESCISIONDE TUMORES DE MAMA"
--   id 280 BIOVU   "BIOPSIA DE VULVA"
--   id 284 BIOTRU  "BIOPSIA DE TRUCUT"
--
-- Queda:
--   id 22  BIOP "Biopsia"
--
-- Lo mismo en `catalogo_procedimientos` (ganador = id 21).
-- Las FK de proce_medicos se reasignan al ganador.
-- La pérdida de granularidad anatómica se compensa porque los
-- registros históricos mantienen el campo
-- `especialidad`/`especialidad_id` que indica el contexto.
-- ============================================================

BEGIN;

-- ─── Tabla legacy `procedimientos` ────────────────────────

UPDATE procedimientos
SET nombre = 'Biopsia',
    descripcion = 'Toma de muestra de tejido para análisis histopatológico.'
WHERE id = 22;

DO $$
DECLARE
    ganador CONSTANT INT := 22;
    perdedor INT;
    cnt INT;
BEGIN
    FOR perdedor IN SELECT unnest(ARRAY[65, 206, 279, 280, 284]) LOOP
        UPDATE proce_medicos
        SET id_procedimiento = ganador
        WHERE id_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'Procedimiento % absorbido por BIOP (22): % referencias migradas',
            perdedor, cnt;
        DELETE FROM procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

-- ─── Tabla maestra `catalogo_procedimientos` ─────────────

UPDATE catalogo_procedimientos
SET nombre = 'Biopsia',
    descripcion = 'Toma de muestra de tejido para análisis histopatológico.'
WHERE id = 21;

DO $$
DECLARE
    ganador CONSTANT INT := 21;
    perdedor INT;
    cnt INT;
BEGIN
    FOR perdedor IN SELECT unnest(ARRAY[59, 182, 240, 241, 245]) LOOP
        UPDATE proce_medicos
        SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'catálogo: % absorbido por BIOP (21): % referencias migradas',
            perdedor, cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

COMMIT;