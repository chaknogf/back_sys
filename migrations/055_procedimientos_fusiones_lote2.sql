-- ============================================================
-- 055_procedimientos_fusiones_lote2.sql
-- Fusiona los pares con similitud >= 80% en el catálogo maestro.
--
-- Bloque 1 (pares 1-6): duplicados tipográficos / plurales
--   1. RETVD + RV          → Retiro de Vendaje
--   2. RETY  + RY          → Retiro de Yeso
--   3. LYD   + LD          → Lavado y Debridamiento
--   4. HISP  + HI          → Hisopado
--   5. RMASA + DDS         → Resección de Masa
--   6. ARTC  + ART         → Artrocentesis
--
-- Bloque 2: familia "Osteosíntesis" → todas las variantes
-- (genéricas + anatómicas) se fusionan en un solo registro
-- "Osteosíntesis" (OST), dado que el usuario quiere un único
-- procedimiento canónico.
--
-- Bloque 3: familia "Procedimiento con Anestesia"
--   - ANES (id 85) y PANES (id 200) → uno solo.
--
-- Bloque 4: typos de catéter central subclavio
--   - CCCS (id 88) + CCS (id 106) → uno solo.
--
-- Bloque 5: cuerpo extraño
--   - CEXT (id 97) + ECE (id 100) → uno solo.
--
-- Bloque 6: "Cambio De Membranas" / "Cambio De Artrotomia" /
-- "Cambio De Vas" — no son Osteosíntesis, se conservan
-- independientes.
-- ============================================================

BEGIN;

-- ──────────────────────────
-- Bloque 1: pares 1-6
-- ──────────────────────────
DO $$
DECLARE
    pares INT[][] := ARRAY[
        -- ganador, perdedor
        ARRAY[220, 20],   -- RV absorbe RETVD
        ARRAY[219, 80],   -- RY absorbe RETY
        ARRAY[233, 14],   -- LD absorbe LYD
        ARRAY[130, 76],   -- HI absorbe HISP
        ARRAY[121, 142],  -- RMASA absorbe DDS (typo)
        ARRAY[104, 32]    -- ART absorbe ARTC
    ];
    par INT[];
    ganador INT;
    perdedor INT;
    cnt INT;
BEGIN
    FOREACH par SLICE 1 IN ARRAY pares LOOP
        ganador := par[1];
        perdedor := par[2];
        UPDATE proce_medicos
        SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'Bloque1: % absorbido por % (% refs)',
            perdedor, ganador, cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

UPDATE catalogo_procedimientos SET descripcion = 'Retiro de vendaje aplicado al paciente.' WHERE id = 220;
UPDATE catalogo_procedimientos SET descripcion = 'Retiro de yeso aplicado al paciente.' WHERE id = 219;
UPDATE catalogo_procedimientos SET descripcion = 'Lavado quirúrgico y retiro de tejido desvitalizado.' WHERE id = 233;
UPDATE catalogo_procedimientos SET descripcion = 'Toma de muestra con hisopo para cultivo o análisis.' WHERE id = 130;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de una masa tumoral.' WHERE id = 121;
UPDATE catalogo_procedimientos SET descripcion = 'Punción y aspiración de líquido articular con fines diagnósticos o terapéuticos.' WHERE id = 104;

-- ──────────────────────────
-- Bloque 2: Osteosíntesis (todas)
-- Crea "Osteosíntesis" (OST) si no existe y absorbe el resto.
-- ──────────────────────────

DO $$
DECLARE
    ganador_id INT;
    perdedor INT;
    cnt INT;
BEGIN
    -- Buscar o crear el ganador "Osteosíntesis"
    SELECT id INTO ganador_id FROM catalogo_procedimientos WHERE abreviatura = 'OST';
    IF ganador_id IS NULL THEN
        INSERT INTO catalogo_procedimientos (abreviatura, nombre, descripcion, anestesia, especialidad_ref, activo)
        VALUES ('OST', 'Osteosíntesis', 'Fijación quirúrgica de hueso fracturado mediante clavos, placas, tornillos o fijadores externos.', 1, NULL, TRUE)
        RETURNING id INTO ganador_id;
        RAISE NOTICE 'OST ganador creado con id %', ganador_id;
    END IF;

    -- Absorber todas las demás variantes
    FOR perdedor IN
        SELECT id FROM catalogo_procedimientos
        WHERE (nombre ILIKE '%osteosintesis%'
            OR nombre ILIKE '%osteosintesus%'
            OR nombre ILIKE '%osteosinteis%'
            OR abreviatura IN ('OSTS','OSTEO','OSTT','ODT','ODC','OSTR','OTDA','FXH-FXT'))
          AND id <> ganador_id
    LOOP
        UPDATE proce_medicos
        SET id_catalogo_procedimiento = ganador_id
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'Osteosíntesis: % absorbido por % (% refs)', perdedor, ganador_id, cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

UPDATE catalogo_procedimientos
SET descripcion = 'Fijación quirúrgica de hueso fracturado mediante clavos, placas, tornillos o fijadores externos.',
    nombre = 'Osteosíntesis'
WHERE abreviatura = 'OST';

-- ──────────────────────────
-- Bloque 3: Anestesia
-- ──────────────────────────
DO $$
DECLARE
    ganador_id INT := 85;  -- ANES "Procedimiento con Anestesia"
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_catalogo_procedimiento = ganador_id
    WHERE id_catalogo_procedimiento = 200;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'Anestesia: PANES (200) absorbido por ANES (85) (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = 200;
END $$;

UPDATE catalogo_procedimientos
SET descripcion = 'Procedimiento clínico realizado bajo anestesia.'
WHERE id = 85;

-- ──────────────────────────
-- Bloque 4: Catéter Central Subclavio
-- ──────────────────────────
DO $$
DECLARE
    ganador_id INT := 88;   -- CCCS (primera abreviatura creada)
    cnt INT;
BEGIN
    UPDATE catalogo_procedimientos SET nombre = 'Colocación de Catéter Central Subclavio', abreviatura = 'CCCS' WHERE id = 88;
    UPDATE proce_medicos
    SET id_catalogo_procedimiento = ganador_id
    WHERE id_catalogo_procedimiento = 106;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'CCS absorbido por CCCS (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = 106;
END $$;

UPDATE catalogo_procedimientos
SET descripcion = 'Inserción de catéter venoso central por vía subclavia.'
WHERE id = 88;

-- ──────────────────────────
-- Bloque 5: Cuerpo Extraño
-- ──────────────────────────
DO $$
DECLARE
    ganador_id INT := 97;   -- CEXT
    cnt INT;
BEGIN
    UPDATE catalogo_procedimientos SET nombre = 'Extracción de Cuerpo Extraño', abreviatura = 'CEXT' WHERE id = 97;
    UPDATE proce_medicos
    SET id_catalogo_procedimiento = ganador_id
    WHERE id_catalogo_procedimiento = 100;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'ECE absorbido por CEXT (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = 100;
END $$;

UPDATE catalogo_procedimientos
SET descripcion = 'Remoción quirúrgica de un cuerpo extraño.'
WHERE id = 97;

COMMIT;