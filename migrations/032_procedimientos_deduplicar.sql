-- ============================================================
-- 032_procedimientos_deduplicar.sql
-- Desduplica procedimientos de la tabla `procedimientos`,
-- fusionando duplicados (21 grupos identificados en el análisis
-- de calidad de datos) y corrigiendo 10 typos ortográficos.
--
-- Estrategia:
--   1. Para cada grupo de duplicados, mantener el ID más bajo
--      como "ganador" y reasignar las referencias en
--      `proce_medicos.id_procedimiento` de los perdedores al ID
--      ganador.
--   2. Eliminar las filas perdedoras.
--   3. Para los typos, corregir el `nombre` in situ (mismo id).
--
-- Las relaciones actuales de `procedimientos` son solo a
-- `proce_medicos.id_procedimiento` (FK ON DELETE SET NULL), por
-- lo que no hay otras tablas que migrar.
-- ============================================================

BEGIN;

-- =====================================================
-- 1) TYPOS ORTOGRÁFICOS: corrección in situ
-- =====================================================
-- 5 variantes de "Manipulacin" → "Manipulación cerrada"
UPDATE procedimientos SET nombre = 'Manipulación cerrada de hombro' WHERE id = 125;
UPDATE procedimientos SET nombre = 'Manipulación cerrada de cadera' WHERE id = 126;
UPDATE procedimientos SET nombre = 'Manipulación cerrada'            WHERE id = 127;
UPDATE procedimientos SET nombre = 'Osteosíntesis de codo'          WHERE id = 169;
UPDATE procedimientos SET nombre = 'Legrado instrumental uterino'  WHERE id = 246;
UPDATE procedimientos SET nombre = 'Ultrasonido obstétrico'         WHERE id = 248;
UPDATE procedimientos SET nombre = 'Ooforectomía unilateral o bilateral' WHERE id = 261;

-- 3 variantes de "Jadelle" mal escrito
UPDATE procedimientos SET abreviatura = 'JADELLE', nombre = 'Implante Jadelle' WHERE id = 62;
UPDATE procedimientos SET nombre = 'Colocación de Jadelle' WHERE id = 271;
UPDATE procedimientos SET nombre = 'Retiro de Jadelle'    WHERE id = 278;

-- Bonus: tilde mal puesta (mcm = Manipulación cerrada de Hombro)
-- Se unifica con id 125 en el grupo de desduplicación más abajo

-- =====================================================
-- 2) DESDUPLICACIÓN: fusionar duplicados en un solo ID
-- Estrategia: para cada grupo, mantener el ID más bajo y
-- migrar las FK de los IDs más altos antes de borrarlos.
-- =====================================================

-- Helper: función que reasigna y borra.
DO $$
DECLARE
    -- (ganador, perdedor)
    pairs INT[][] := ARRAY[
        -- Grupo: Retiro de Canales (RETCN/RC/RCAN)
        ARRAY[17, 21],  -- 17 RETCN -> 21 RETCN? no, ganamos 17
        ARRAY[17, 185], -- RC -> RETCN
        ARRAY[17, 249], -- RCAN -> RETCN
        -- Grupo: Liberación Túnel del Carpo
        ARRAY[38, 204],
        ARRAY[38, 212],
        -- Grupo: Ultrasonido (USG/EV-UGC/UO)
        ARRAY[72, 130],
        ARRAY[72, 211],
        -- Grupo: Retiro de Puntos
        ARRAY[18, 250],
        -- Grupo: Retiro de Grapas
        ARRAY[19, 264],
        -- Grupo: Drenaje de Hematoma
        ARRAY[16, 201],
        -- Grupo: Tenotomía
        ARRAY[26, 213],
        -- Grupo: Osteosíntesis
        ARRAY[28, 256],
        -- Grupo: Artroplastia
        ARRAY[34, 178],
        -- Grupo: Colecistectomía
        ARRAY[40, 270],
        -- Grupo: Hemorroidectomía
        ARRAY[43, 134],
        -- Grupo: Postectomía
        ARRAY[69, 286],
        -- Grupo: Infiltración
        ARRAY[88, 267],
        -- Grupo: Cierre por Tercera Intención
        ARRAY[105, 191],
        -- Grupo: Herniorrafia
        ARRAY[118, 147],
        -- Grupo: Retiro de Espica
        ARRAY[122, 175],
        -- Grupo: Retiro de Material
        ARRAY[140, 174],
        -- Grupo: Retiro de Clavos
        ARRAY[145, 255],
        -- Grupo: Retiro de Fijador Externo
        ARRAY[159, 190],
        -- Grupo: Infiltración Ecoguiada
        ARRAY[253, 262],
        -- Grupo: "Manipulación cerrada de Hombro" (typo id 254 mcm)
        ARRAY[125, 254]
    ];
    pair INT[];
    ganador INT;
    perdedor INT;
    migrados INT;
    borrados INT := 0;
BEGIN
    FOREACH pair SLICE 1 IN ARRAY pairs LOOP
        ganador := pair[1];
        perdedor := pair[2];
        -- Migrar referencias en proce_medicos
        UPDATE proce_medicos
        SET id_procedimiento = ganador
        WHERE id_procedimiento = perdedor;
        GET DIAGNOSTICS migrados = ROW_COUNT;
        RAISE NOTICE 'Procedimiento % absorbido por % (% referencias migradas)',
            perdedor, ganador, migrados;
        -- Borrar el perdedor
        DELETE FROM procedimientos WHERE id = perdedor;
        GET DIAGNOSTICS borrados = ROW_COUNT;
    END LOOP;
    RAISE NOTICE 'Total procedimientos duplicados eliminados: %', array_length(pairs, 1);
END $$;

-- =====================================================
-- 3) Normalización opcional: nombres en MAYÚSCULAS → título
-- Solo si difieren del original (no rompe nada).
-- =====================================================
-- (Opcional - descomentar si se desea uniformidad visual)
-- UPDATE procedimientos
-- SET nombre = INITCAP(LOWER(nombre))
-- WHERE nombre = UPPER(nombre) AND nombre <> INITCAP(LOWER(nombre));

COMMIT;