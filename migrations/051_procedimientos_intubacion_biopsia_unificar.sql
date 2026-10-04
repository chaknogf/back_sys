-- ============================================================
-- 051_procedimientos_intubacion_biopsia_unificar.sql
-- 1) Une los 3 procedimientos de intubación endotraqueal
--    (id 6 IOT, id 93 CTE, id 238 INTO) en un único registro:
--    "Intubación Endotraqueal" (IOT) con descripción clínica.
-- 2) Une los 2 de biopsia endometrial (id 206 BE y
--    id 219 BIOEND) en un único registro:
--    "Biopsia Endometrial" (BE) con descripción clínica.
--
-- Los procedimientos AMEU (Aspiración Manual Endouterina)
-- quedan tal cual: es un concepto distinto a la biopsia
-- endometrial, aunque a veces se confunden por el destino
-- de la muestra.
-- ============================================================

BEGIN;

-- ─── Tabla legacy `procedimientos` ────────────────────────

-- 1a) Renombrar ganador IOT y aplicar descripción clínica
UPDATE procedimientos
SET nombre = 'Intubación Endotraqueal',
    abreviatura = 'IOT',
    descripcion = 'Colocación de tubo endotraqueal u orotraqueal para asegurar la vía aérea.'
WHERE id = 6;

-- 1b) Absorber id 93 (CTE) y id 238 (INTO) en id 6
DO $$
DECLARE
    ganador CONSTANT INT := 6;
    perdedor INT;
    cnt INT;
BEGIN
    FOR perdedor IN SELECT unnest(ARRAY[93, 238]) LOOP
        UPDATE proce_medicos
        SET id_procedimiento = ganador
        WHERE id_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'Intubación: id % absorbido por 6: % referencias migradas',
            perdedor, cnt;
        DELETE FROM procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

-- 2a) Renombrar ganador BE (id 206) y aplicar descripción clínica
UPDATE procedimientos
SET nombre = 'Biopsia Endometrial',
    abreviatura = 'BE',
    descripcion = 'Toma de muestra de tejido interno del útero para análisis histopatológico.'
WHERE id = 206;

-- 2b) Absorber id 219 (BIOEND) en id 206
DO $$
DECLARE
    ganador CONSTANT INT := 206;
    perdedor CONSTANT INT := 219;
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'BIOEND absorbido por BE: % referencias migradas', cnt;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;

-- ─── Tabla maestra `catalogo_procedimientos` ─────────────

UPDATE catalogo_procedimientos
SET nombre = 'Intubación Endotraqueal',
    abreviatura = 'IOT',
    descripcion = 'Colocación de tubo endotraqueal u orotraqueal para asegurar la vía aérea.'
WHERE id = 6;

DO $$
DECLARE
    ganador CONSTANT INT := 6;
    perdedor INT;
    cnt INT;
BEGIN
    FOR perdedor IN SELECT unnest(ARRAY[89, 210]) LOOP
        UPDATE proce_medicos
        SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'catálogo Intubación: id % absorbido por 6: % referencias migradas',
            perdedor, cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

-- Biopsia Endometrial: ganador = id 182 (BE)
DO $$
DECLARE
    ganador CONSTANT INT := 182;
    perdedor CONSTANT INT := 192;
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'catálogo Biopsia: id % absorbido por 182: % referencias migradas',
        perdedor, cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

UPDATE catalogo_procedimientos
SET nombre = 'Biopsia Endometrial',
    abreviatura = 'BE',
    descripcion = 'Toma de muestra de tejido interno del útero para análisis histopatológico.'
WHERE id = 182;

COMMIT;