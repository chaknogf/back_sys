-- ============================================================
-- 034_procedimientos_punto4_limpieza.sql
-- Limpia el catálogo de procedimientos según el análisis del
-- punto 4 (siglas, typos y nombres genéricos de una sola
-- palabra). Antes de esta migración, debe haberse ejecutado
-- `032_procedimientos_deduplicar.sql`.
--
-- Decisiones:
--   - Typos/errores ortográficos → corrección in situ
--   - Siglas médicas ambiguas → expandir a descripción clara
--   - Nombres con "/" → quedarse con la forma canónica
--   - Abreviaturas en minúsculas → estandarizar a MAYÚSCULAS
--   - HSP/HISOPADOS → se fusionan (HISOPADOS absorbe HSP)
-- ============================================================

BEGIN;

-- =====================================================
-- 1) Corrección de typos/errores ortográficos
-- =====================================================
UPDATE procedimientos SET nombre = 'Granuloma'                WHERE id = 236;
-- Venodisección id 10 ya existe (canonica); id 109 se fusiona con el
DO $$
DECLARE
    ganador CONSTANT INT := 10;   -- VENO / Venodisección
    perdedor CONSTANT INT := 109; -- VENOD / Venoviseccion
    migrados INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS migrados = ROW_COUNT;
    RAISE NOTICE 'VENOD absorbido por VENO: % referencias migradas', migrados;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;
UPDATE procedimientos SET nombre = 'Espirometría'             WHERE id = 184;
-- Glucometrías (115) se fusiona con Glucometría (84)
DO $$
DECLARE
    ganador CONSTANT INT := 84;   -- GLUC / Glucometría
    perdedor CONSTANT INT := 115; -- GLUCO / Glucometrias
    migrados INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS migrados = ROW_COUNT;
    RAISE NOTICE 'GLUCO absorbido por GLUC: % referencias migradas', migrados;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;
UPDATE procedimientos SET nombre = 'Intraóseo'               WHERE id = 116;
-- Herniorrafia id 118 ya existe (HERR); id 42 (HERN) se fusiona con el
DO $$
DECLARE
    ganador CONSTANT INT := 118;  -- HERM / Herniorrafia
    perdedor CONSTANT INT := 42;  -- HERN / Herniorrafia/Hernioplastia
    migrados INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS migrados = ROW_COUNT;
    RAISE NOTICE 'HERN absorbido por HERM: % referencias migradas', migrados;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;

-- Regularización es genérico; como nombre suelto puede
-- significar "Regularización de miembro". Se deja más específico.
-- (No se modifica para no perder información si era usado por
-- alguna consulta específica; ver reporte.)

-- DIU en minúsculas → mayúsculas
UPDATE procedimientos SET nombre = 'DIU' WHERE id = 128;

-- =====================================================
-- 2) HSP / HISOPADOS: el id 245 (HISOPADOS/HSP) se fusiona
-- con el id 83 (HISP / Hisopado) que es el nombre canónico.
-- =====================================================
DO $$
DECLARE
    ganador CONSTANT INT := 83;
    perdedor CONSTANT INT := 245;
    migrados INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS migrados = ROW_COUNT;
    RAISE NOTICE 'HSP/HISOPados (id %) absorbido por Hisopado (id %): % referencias migradas',
        perdedor, ganador, migrados;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;

-- =====================================================
-- 3) Siglas médicas sin descripción → expandir
-- (mantener abreviatura y dar nombre descriptivo)
-- =====================================================
UPDATE procedimientos SET nombre = 'Aspiración Manual Endouterina'
    WHERE id = 48 AND nombre = 'AMEU';                       -- AMEU

UPDATE procedimientos SET nombre = 'Ecografía FAST'
    WHERE id = 71 AND nombre = 'FAST';                      -- FAST

UPDATE procedimientos SET nombre = 'Cardiotocografía (Non-Stress Test)'
    WHERE id = 103 AND lower(nombre) = 'nst';               -- Nst → NST

UPDATE procedimientos SET nombre = 'Tomografía de Coherencia Óptica'
    WHERE id = 107 AND lower(nombre) = 'oct';               -- Oct → OCT

-- BK = "Baker" parece un error ortográfico. Asumimos que es
-- "Quiste de Baker" (diagnóstico), no un procedimiento. Se
-- requiere confirmación: se renombra provisionalmente.
UPDATE procedimientos SET nombre = 'Quiste de Baker (Dx)'
    WHERE id = 139 AND lower(nombre) = 'baker';

-- =====================================================
-- 4) Estandarizar nombres en MAYÚSCULAS → a formato título
-- =====================================================
UPDATE procedimientos SET nombre = 'Vasectomía' WHERE id = 241;

-- =====================================================
-- 5) "Manipulación cerrada" sin zona (id 127, abreviatura MC)
-- es genérico. Se conserva con nombre más informativo.
-- =====================================================
UPDATE procedimientos SET nombre = 'Manipulación cerrada (general)' WHERE id = 127;

-- =====================================================
-- 6) "Manipulación cerrada de hombro" en minúsculas (id 254)
-- ya fue absorbido por id 125 en 032. Verificación.
-- =====================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM procedimientos WHERE id = 254) THEN
        UPDATE procedimientos
        SET nombre = 'Manipulación cerrada de hombro'
        WHERE id = 254;
    END IF;
END $$;

COMMIT;

-- =====================================================
-- Verificación final
-- =====================================================
SELECT id, abreviatura, nombre
FROM procedimientos
WHERE id IN (236, 109, 184, 115, 254, 125, 126, 127, 42, 116, 128, 173, 245, 48, 71, 103, 107, 139, 241, 83)
ORDER BY id;