-- ============================================================
-- concat.sql
-- Concatenación de las migraciones 032..073 del directorio
-- `migrations/`, en orden de aplicación, en un único archivo
-- ejecutable para PostgreSQL (bd: hospital).
--
-- Cobertura: 42 secciones (032, 033, ... 073) y 41 transacciones
-- BEGIN/COMMIT (una sección no abre transacción propia).
--
-- Ejecución recomendada (se detiene en el primer error):
--   psql -h localhost -U <usuario> -d hospital -v ON_ERROR_STOP=1 -f concat.sql
--
-- Permisos: requiere un rol con DDL en `public` y dueño de las
-- tablas (p. ej. `postgres`). El usuario `admin` de `.env` NO tiene
-- CREATE en `public` ni es dueño de las tablas.
--
-- Verificación: ejecutado de punta a punta sobre una copia de
-- `hospital` (bd desechable) -> 0 errores; catálogo final 477 filas.
--
-- ------------------------------------------------------------
-- NOTAS DE ADAPTACIÓN
-- ------------------------------------------------------------
-- Esta versión NO es una concatenación literal de los archivos
-- individuales: las secciones llevan las correcciones necesarias
-- para que la corrida sea limpia sobre esta BD. Motivo: 039 carga
-- `catalogo_procedimientos` desde `procedimientos` con id SERIAL y
-- sin ORDER BY, así que los ids del catálogo NO son los ids de la
-- tabla legacy y los ids fijos escritos contra otro estado de la BD
-- no coinciden. Correcciones aplicadas:
--   * 039: `ON CONFLICT` sin objetivo (idempotente también frente a
--         UNIQUE(abreviatura); la versión original solo cubría nombre).
--   * 056: helper `cat_id(abreviacion text)`.
--   * 057, 058, 059, 060, 061, 062, 064, 065, 067, 069, 070: ids
--         fijos reemplazados por resolución por `abreviatura` (o
--         `nombre`), con RAISE NOTICE y no-op seguro si no existe.
--   * 063, 068: `WHERE id = N` reemplazado por
--         `WHERE unaccent(upper(nombre)) = '...'`; en 063 se elimina
--         el sobrescrito accidental a 'LSDHCCT' (id 134) que pisaba
--         el nombre fijado unas líneas antes.
--   * 066: sección de normalización de capitalización; faltaba en la
--         concatenación original de concat.sql y se añadió aquí.
--   * 069: bloque CVC/CCCS reordenado (CCCS -> temporal, CVC ->
--         canónico, CVC absorbe a CCCS); 071 queda como no-op.
--   * Cabecera de 043 corregida a `043_vistas_catalogo.sql` (el
--         nombre real del archivo en disco).
--
-- OJO: los archivos individuales `0NN_*.sql` NO llevan todas estas
-- adaptaciones, por lo que `apply.sh` puede fallar en los mismos
-- puntos. `032_073_procedimientos_postgres_consolidado.sql` es la
-- misma versión corregida (idéntica sección a sección).
-- ============================================================


-- ============================================================
-- >>> INICIO: 032_procedimientos_deduplicar.sql
-- ============================================================

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

-- ============================================================
-- >>> FIN: 032_procedimientos_deduplicar.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 033_procedimientos_area_cuerpo.sql
-- ============================================================

-- ============================================================
-- 033_procedimientos_area_cuerpo.sql
-- Crea el catálogo de "Áreas del cuerpo intervenidas" y lo
-- asocia a `procedimientos` para soportar múltiples zonas
-- (varios procedimientos se realizan en distintas partes del
-- cuerpo: Osteosíntesis de radio, de cadera, de tobillo...).
--
-- Estructura:
--   area_cuerpo_intervenida (catálogo)
--   procedimientos_area_cuerpo (N:M con `procedimientos`)
--
-- Tras correcciones a nombres duplicados, los procedimientos que
-- sobreviven y mencionan una zona anatómica son 44. Cada uno se
-- asocia con su(s) área(s) correspondiente(s).
-- ============================================================

BEGIN;

-- =====================================================
-- 1) Catálogo de áreas del cuerpo
-- =====================================================
CREATE TABLE IF NOT EXISTS public.area_cuerpo_intervenida (
    id              SERIAL PRIMARY KEY,
    codigo          VARCHAR(20) UNIQUE NOT NULL,
    nombre          VARCHAR(100) NOT NULL,
    region          VARCHAR(50),
    descripcion     TEXT,
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Catálogo inicial (zonas identificadas en el análisis)
INSERT INTO public.area_cuerpo_intervenida (codigo, nombre, region, descripcion) VALUES
    ('CABEZA',     'Cabeza',          'cabeza',     NULL),
    ('CARA',       'Cara',          'cabeza',     NULL),
    ('CUELLO',     'Cuello',        'cuello',     NULL),
    ('TORAX',      'Tórax',          'torax',      NULL),
    ('ABDOMEN',    'Abdomen',       'tronco',     NULL),
    ('PELVIS',     'Pelvis',        'tronco',     NULL),
    ('ESPALDA',    'Espalda',       'tronco',     NULL),
    ('MANO',       'Mano',          'mss',        'Incluye dedos de la mano'),
    ('DEDO_MANO',  'Dedo de la mano',  'mss',        NULL),
    ('MUNECA',     'Muñeca',        'mss',        NULL),
    ('CODO',       'Codo',          'mss',        NULL),
    ('HOMBRO',     'Hombro',        'mss',        NULL),
    ('BRAZO',      'Brazo',          'mss',        NULL),
    ('ANTEBRAZO',  'Antebrazo',     'mss',        NULL),
    ('PIE',        'Pie',          'msi',        'Incluye dedos del pie'),
    ('DEDO_PIE',   'Dedo del pie',  'msi',        NULL),
    ('TOBILLO',    'Tobillo',       'msi',        NULL),
    ('RODILLA',    'Rodilla',       'msi',        NULL),
    ('MUSLO',      'Muslo',          'msi',        NULL),
    ('PIERNA',     'Pierna',         'msi',        NULL),
    ('CADERA',     'Cadera',        'msi',        NULL),
    ('TALON',      'Talón',          'msi',        NULL),
    ('INGLE',      'Ingle',         'tronco',     NULL),
    ('AXILA',      'Axila',         'tronco',     NULL),
    ('GLUTEO',     'Glúteo',         'msi',        NULL),
    ('MAXILAR',    'Maxilar',       'cabeza',     NULL),
    ('MANDIBULA',  'Mandíbula',     'cabeza',     NULL),
    ('MENTON',     'Mentón',        'cabeza',     NULL),
    ('PARPADO',    'Párpado',       'cabeza',     NULL),
    ('OREJA',      'Oreja',         'cabeza',     NULL),
    ('NARIZ',      'Nariz',         'cabeza',     NULL),
    ('BOCA',       'Boca',          'cabeza',     NULL),
    ('LABIO',      'Labio',         'cabeza',     NULL),
    ('CRANEO',     'Cráneo',        'cabeza',     NULL),
    ('VULVA',      'Vulva',         'pelvis',     NULL),
    ('VAGINA',     'Vagina',        'pelvis',     NULL),
    ('UTERO',      'Útero',         'pelvis',     NULL),
    ('PROSTATA',   'Próstata',      'pelvis',     NULL),
    ('TESTICULO',  'Testículo',     'pelvis',     NULL),
    ('PENE',       'Pene',          'pelvis',     NULL),
    ('ESCROTO',    'Escroto',       'pelvis',     NULL),
    ('OJO',        'Ojo',           'cabeza',     NULL),
    ('MAMA',       'Mama',          'torax',      NULL),
    ('TIBIA',      'Tibia',         'msi',        NULL),
    ('FEMUR',      'Fémur',         'msi',        NULL),
    ('HUMERO',     'Húmero',        'mss',        NULL),
    ('RADIO',      'Radio',         'mss',        NULL),
    ('CUBITO',     'Cubito',        'mss',        NULL),
    ('PULGAR',     'Pulgar',        'mss',        'Dedo de la mano'),
    ('MENIQUE',    'Meñique',       'mss',        'Dedo de la mano'),
    ('INDICE',     'Índice',        'mss',        'Dedo de la mano'),
    ('ANULAR',     'Anular',        'mss',        'Dedo de la mano'),
    ('MEDIO',      'Medio',         'mss',        'Dedo de la mano'),
    ('BILATERAL',  'Bilateral',     'general',    'Aplica a ambos lados')
ON CONFLICT (codigo) DO NOTHING;

-- =====================================================
-- 2) Tabla pivote N:M procedimientos <-> áreas
-- =====================================================
CREATE TABLE IF NOT EXISTS public.procedimientos_area_cuerpo (
    id                  SERIAL PRIMARY KEY,
    id_procedimiento      INT NOT NULL REFERENCES public.procedimientos(id) ON DELETE CASCADE,
    id_area_cuerpo       INT NOT NULL REFERENCES public.area_cuerpo_intervenida(id) ON DELETE RESTRICT,
    lateralidad          VARCHAR(10) CHECK (lateralidad IN ('izq','der','bilateral','ninguna')),
    created_at           TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (id_procedimiento, id_area_cuerpo)
);

CREATE INDEX IF NOT EXISTS idx_pac_procedimiento
    ON public.procedimientos_area_cuerpo(id_procedimiento);
CREATE INDEX IF NOT EXISTS idx_pac_area
    ON public.procedimientos_area_cuerpo(id_area_cuerpo);

-- =====================================================
-- 3) Asociar procedimientos a sus áreas (basado en análisis)
-- =====================================================
-- Procedimientos con zona anatómica (44 detectados)
-- id -> codigo_area_cuerpo (lateralidad por defecto 'ninguna')

INSERT INTO public.procedimientos_area_cuerpo (id_procedimiento, id_area_cuerpo, lateralidad)
SELECT p.id, a.id, 'ninguna'
FROM (VALUES
    -- (id_procedimiento, codigo_area)
    (27,  'PIE'),         -- Injerto de Piel (en pie)
    (47,  'VAGINA'),      -- Parto Vaginal
    (73,  'RADIO'),       -- Radiografía (Radio - hueso)
    (110, 'VAGINA'),      -- Reparación de desgarro vagina
    (125, 'HOMBRO'),      -- Manipulación cerrada hombro
    (126, 'CADERA'),      -- Manipulación cerrada cadera
    (136, 'DEDO_MANO'),   -- Amputación en raqueta de dedo
    (138, 'CUELLO'),      -- Exploración de cuello
    (141, 'HUMERO'),      -- Fx Húmero
    (141, 'TOBILLO'),     -- Fx Tobillo
    (149, 'DEDO_MANO'),   -- Osteosíntesis dedo anular
    (149, 'ANULAR'),
    (155, 'DEDO_MANO'),   -- Reconstrucción de dedo
    (156, 'MUNECA'),      -- Amputación de muñeca
    (163, 'DEDO_MANO'),   -- Regularización de dedo
    (164, 'TOBILLO'),     -- Osteosíntesis de tobillo
    (165, 'DEDO_MANO'),   -- Amputación de dedo
    (167, 'PULGAR'),      -- Regularización pulgar
    (169, 'CODO'),        -- Osteosíntesis de codo
    (176, 'DEDO_MANO'),   -- Liberación túnel del carpo / dedo en gatillo
    (177, 'TOBILLO'),     -- Artrodesis de tobillo
    (182, 'RADIO'),       -- Fractura radio
    (182, 'CUBITO'),
    (189, 'BRAZO'),       -- Manipulación antebrazo
    (189, 'ANTEBRAZO'),
    (192, 'RODILLA'),     -- Artroplastia de rodilla
    (197, 'RODILLA'),     -- Artrodesis rodilla
    (200, 'CUELLO'),      -- Resección de masa en cuello
    (202, 'CADERA'),      -- Hemiartroplastia de cadera
    (214, 'PIE'),         -- Excisión de masa en pie
    (218, 'MUNECA'),      -- Manipulación de muñeca
    (221, 'DEDO_MANO'),   -- Drenaje de dedo
    (223, 'MANO'),        -- Onicectomía dedo mano
    (223, 'DEDO_MANO'),
    (224, 'TORAX'),       -- Escarectomía en tórax
    (228, 'PIE'),         -- Injerto de piel
    (234, 'ANULAR'),      -- Férula anular
    (239, 'RADIO'),       -- Osteosíntesis radio
    (240, 'TOBILLO'),     -- Osteosíntesis tobillo
    (247, 'VAGINA'),      -- Ultrasonido endovaginal
    (259, 'VAGINA'),      -- Histerectomía vaginal
    (276, 'CUELLO'),      -- Masa en cuello
    (277, 'LABIO'),       -- Masa en labio
    (279, 'MAMA'),        -- Biopsia/excisión de mama
    (280, 'VULVA'),       -- Biopsia de vulva
    (281, 'RADIO'),       -- O/S radio
    (282, 'RODILLA'),     -- Reemplazo de rodillas
    (283, 'CUBITO')       -- O/S cubito
) AS data(id_procedimiento, codigo_area)
JOIN public.procedimientos p ON p.id = data.id_procedimiento
JOIN public.area_cuerpo_intervenida a ON a.codigo = data.codigo_area
ON CONFLICT (id_procedimiento, id_area_cuerpo) DO NOTHING;

COMMIT;

-- ============================================================
-- >>> FIN: 033_procedimientos_area_cuerpo.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 034_procedimientos_punto4_limpieza.sql
-- ============================================================

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

-- ============================================================
-- >>> FIN: 034_procedimientos_punto4_limpieza.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 035_procedimientos_regularizacion_clarificar.sql
-- ============================================================

-- ============================================================
-- 035_procedimientos_regularizacion_clarificar.sql
-- Aplica la opción C del análisis del id 173:
-- Renombra los 3 procedimientos "Regularización" para que su
-- intención sea explícita en el catálogo.
--
-- No se borra el id 173: queda como "Regularización (genérico)"
-- para usos donde el especialista aún no especifica zona.
-- ============================================================

BEGIN;

UPDATE procedimientos SET nombre = 'Regularización de Dedo'
WHERE id = 163 AND nombre <> 'Regularización de Dedo';

UPDATE procedimientos SET nombre = 'Regularización de Pulgar'
WHERE id = 167 AND nombre <> 'Regularización de Pulgar';

UPDATE procedimientos SET nombre = 'Regularización (genérico - requiere especificar zona)'
WHERE id = 173 AND nombre <> 'Regularización (genérico - requiere especificar zona)';

COMMIT;

-- ============================================================
-- >>> FIN: 035_procedimientos_regularizacion_clarificar.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 036_procedimientos_regularizacion_fusionar_dedo.sql
-- ============================================================

-- ============================================================
-- 036_procedimientos_regularizacion_fusionar_dedo.sql
-- Fusión final: id 167 (Regularización de Pulgar) y
-- id 173 (Regularización genérico) se absorben en id 163
-- (Regularización de Dedo).
--
-- Justificación clínica:
--   "Pulgar" anatómicamente es un dedo. En traumatología, una
--   regularización se realiza sobre una zona específica (casi
--   siempre dedo). Al usar solo "Dedo", se evitan ambigüedades
--   y se mantiene el registro histórico.
-- ============================================================

BEGIN;

DO $$
DECLARE
    ganador CONSTANT INT := 163;  -- RDD / Regularización de Dedo
    cnt INT;
BEGIN
    -- Absorber id 167 (Regularización de Pulgar)
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = 167;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'Pulgar (167) absorbido por Dedo (163): % referencias migradas', cnt;
    DELETE FROM procedimientos WHERE id = 167;

    -- Absorber id 173 (Regularización genérico)
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = 173;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'Genérico (173) absorbido por Dedo (163): % referencias migradas', cnt;
    DELETE FROM procedimientos WHERE id = 173;
END $$;

COMMIT;

-- ============================================================
-- >>> FIN: 036_procedimientos_regularizacion_fusionar_dedo.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 037_procedimientos_regularizacion_nombre_final.sql
-- ============================================================

-- ============================================================
-- 037_procedimientos_regularizacion_nombre_final.sql
-- Cambio de nombre final para id 163:
--   "Regularización de Dedo" → "Regularización"
--
-- Justificación:
--   El nombre del procedimiento queda como término clínico
--   genérico ("Regularización") y la zona del cuerpo
--   intervenida se indica en el área asociada
--   (`procedimientos_area_cuerpo` -> `area_cuerpo_intervenida`
--   con codigo DEDO_MANO / "Dedo de la mano").
--
-- No se elimina ningún registro: el id 163 sigue activo y
-- mantiene su asociación a la zona "Dedo de la mano".
-- ============================================================

BEGIN;

UPDATE procedimientos
SET nombre = 'Regularización'
WHERE id = 163
  AND nombre <> 'Regularización';

COMMIT;

-- ============================================================
-- >>> FIN: 037_procedimientos_regularizacion_nombre_final.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 038_procedimientos_regularizacion_abreviatura.sql
-- ============================================================

-- ============================================================
-- 038_procedimientos_regularizacion_abreviatura.sql
-- Cambia la abreviatura del procedimiento id 163 (Regularización)
-- de "RDD" → "REG".
--
-- Justificación:
--   El nombre del procedimiento es ahora genérico
--   ("Regularización"), por lo que la abreviatura también debe
--   reflejar la acción clínica (REG = Regularización), no la zona
--   intervenida (que se registra aparte vía `area_cuerpo_intervenida`).
-- ============================================================

BEGIN;

UPDATE procedimientos
SET abreviatura = 'REG'
WHERE id = 163
  AND abreviatura <> 'REG';

COMMIT;

-- ============================================================
-- >>> FIN: 038_procedimientos_regularizacion_abreviatura.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 039_catalogo_procedimientos.sql
-- ============================================================

-- ============================================================
-- 039_catalogo_procedimientos.sql
-- Crea el catálogo maestro unificado `catalogo_procedimientos`
-- con todos los nombres de procedimientos estandarizados,
-- abreviatura única y especialidad_ref opcional (NULL por
-- defecto).
--
-- Pensada como fuente única para:
--   - proce_medicos  (procedimientos médicos en consultas)
--   - quirofano      (intervenciones quirúrgicas)
--   - reporte_procedimientos / resumen_procedimientos
--
-- Estrategia:
--   1. Crear `catalogo_procedimientos` poblada desde el
--      catálogo actual `procedimientos` (los 256 registros
--      vigentes).
--   2. Mantener `procedimientos` por compatibilidad legacy.
--   3. Más adelante: agregar `id_catalogo_procedimiento` en
--      proce_medicos y en intervenciones_quirurgicas (mig 040
--      y 041).
-- ============================================================

BEGIN;

-- =====================================================
-- 1) Crear tabla catálogo_procedimientos
-- =====================================================
CREATE TABLE IF NOT EXISTS public.catalogo_procedimientos (
    id                  SERIAL PRIMARY KEY,
    abreviatura         VARCHAR(10) UNIQUE,
    nombre              VARCHAR(200) NOT NULL UNIQUE,
    descripcion         TEXT,
    anestesia           INTEGER NOT NULL DEFAULT 0,
    especialidad_ref    INTEGER REFERENCES public.especialidades(id) ON DELETE SET NULL,
    activo              BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_catalogo_procedimientos_especialidad
    ON public.catalogo_procedimientos(especialidad_ref);
CREATE INDEX IF NOT EXISTS idx_catalogo_procedimientos_activo
    ON public.catalogo_procedimientos(activo);

-- =====================================================
-- 2) Poblar desde el catálogo legacy `procedimientos`
-- (especialidad_ref queda NULL para todos: no estaba vinculada)
-- =====================================================
INSERT INTO public.catalogo_procedimientos
    (abreviatura, nombre, descripcion, anestesia, especialidad_ref, activo, created_at, updated_at)
SELECT
    abreviatura,
    nombre,
    descripcion,
    COALESCE(anestesia, 0),
    NULL,            -- especialidad_ref queda NULL
    TRUE,            -- activo por defecto
    NOW(),
    NOW()
FROM public.procedimientos
ON CONFLICT DO NOTHING;  -- [ADAPTADO] ON CONFLICT sin objetivo: hace el INSERT
                         -- idempotente también frente a UNIQUE(abreviatura) en
                         -- re-corridas (la versión original solo cubría nombre,
                         -- y abortaba si un procedimiento quedado fuera por nombre
                         -- traía una abreviatura ya usada, p.ej. 'PES').

COMMIT;

-- Verificación
SELECT COUNT(*) AS total_catalogo FROM catalogo_procedimientos;

-- ============================================================
-- >>> FIN: 039_catalogo_procedimientos.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 040_proce_medicos_catalogo_procedimientos.sql
-- ============================================================

-- ============================================================
-- 040_proce_medicos_catalogo_procedimientos.sql
-- Agrega la columna `id_catalogo_procedimiento` en
-- `proce_medicos` como FK opcional al nuevo catálogo maestro.
--
-- Estrategia:
--   1. Crear la columna FK (nullable inicialmente).
--   2. Backfill: para cada registro con `id_procedimiento`
--      apuntando al catálogo legacy, buscar su equivalente en
--      `catalogo_procedimientos` por nombre y llenar la nueva
--      columna.
--   3. NO se elimina `id_procedimiento` todavía: queda como
--      columna legacy por compatibilidad. La aplicación puede
--      ir migrando gradualmente a la nueva FK.
-- ============================================================

BEGIN;

-- 1) Nueva columna FK
ALTER TABLE public.proce_medicos
    ADD COLUMN IF NOT EXISTS id_catalogo_procedimiento INTEGER;

-- 2) FK opcional
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'proce_medicos_id_catalogo_procedimiento_fkey'
    ) THEN
        ALTER TABLE public.proce_medicos
        ADD CONSTRAINT proce_medicos_id_catalogo_procedimiento_fkey
        FOREIGN KEY (id_catalogo_procedimiento)
        REFERENCES public.catalogo_procedimientos(id)
        ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_pm_catalogo
    ON public.proce_medicos(id_catalogo_procedimiento);

-- 3) Backfill: copiar referencias desde id_procedimiento legacy
-- hacia id_catalogo_procedimiento usando nombre como puente.
UPDATE public.proce_medicos pm
SET id_catalogo_procedimiento = cp.id
FROM public.procedimientos p,
     public.catalogo_procedimientos cp
WHERE pm.id_procedimiento = p.id
  AND cp.nombre = p.nombre
  AND pm.id_catalogo_procedimiento IS NULL;

COMMIT;

-- Verificación
SELECT
    COUNT(*) FILTER (WHERE id_catalogo_procedimiento IS NOT NULL) AS con_nuevo_catalogo,
    COUNT(*) FILTER (WHERE id_catalogo_procedimiento IS NULL)     AS sin_nuevo_catalogo,
    COUNT(*) AS total
FROM public.proce_medicos;

-- ============================================================
-- >>> FIN: 040_proce_medicos_catalogo_procedimientos.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 041_intervenciones_quirurgicas_catalogo_procedimientos.sql
-- ============================================================

-- ============================================================
-- 041_intervenciones_quirurgicas_catalogo_procedimientos.sql
-- Conecta `intervenciones_quirurgicas` (quirófano) al catálogo
-- maestro `catalogo_procedimientos`.
--
-- Las columnas `procedimiento_principal/2/3/4/5` son VARCHAR
-- (texto libre). Estrategia mixta:
--   1. Agregar columnas FK nuevas para los 5 slots:
--      procedimiento_principal_id ... procedimiento_5_id
--   2. Backfill: mapear por nombre a catalogo_procedimientos.
--   3. Mantener las columnas legacy VARCHAR (no se eliminan aún)
--      para no romper nada durante la transición.
-- ============================================================

BEGIN;

-- 1) Nuevas columnas FK (nullable)
ALTER TABLE public.intervenciones_quirurgicas
    ADD COLUMN IF NOT EXISTS procedimiento_principal_id INTEGER,
    ADD COLUMN IF NOT EXISTS procedimiento_2_id INTEGER,
    ADD COLUMN IF NOT EXISTS procedimiento_3_id INTEGER,
    ADD COLUMN IF NOT EXISTS procedimiento_4_id INTEGER,
    ADD COLUMN IF NOT EXISTS procedimiento_5_id INTEGER;

-- 2) FKs al catálogo maestro
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_principal_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_principal_id_fkey
        FOREIGN KEY (procedimiento_principal_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_2_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_2_id_fkey
        FOREIGN KEY (procedimiento_2_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_3_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_3_id_fkey
        FOREIGN KEY (procedimiento_3_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_4_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_4_id_fkey
        FOREIGN KEY (procedimiento_4_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_5_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_5_id_fkey
        FOREIGN KEY (procedimiento_5_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_iq_proc_principal ON public.intervenciones_quirurgicas(procedimiento_principal_id);
CREATE INDEX IF NOT EXISTS idx_iq_proc_2        ON public.intervenciones_quirurgicas(procedimiento_2_id);
CREATE INDEX IF NOT EXISTS idx_iq_proc_3        ON public.intervenciones_quirurgicas(procedimiento_3_id);
CREATE INDEX IF NOT EXISTS idx_iq_proc_4        ON public.intervenciones_quirurgicas(procedimiento_4_id);
CREATE INDEX IF NOT EXISTS idx_iq_proc_5        ON public.intervenciones_quirurgicas(procedimiento_5_id);

-- 3) Backfill: para cada slot, mapear texto -> id catálogo
UPDATE public.intervenciones_quirurgicas iq
SET procedimiento_principal_id = cp.id
FROM public.catalogo_procedimientos cp
WHERE iq.procedimiento_principal IS NOT NULL
  AND cp.nombre = iq.procedimiento_principal
  AND iq.procedimiento_principal_id IS NULL;

UPDATE public.intervenciones_quirurgicas iq
SET procedimiento_2_id = cp.id
FROM public.catalogo_procedimientos cp
WHERE iq.procedimiento_2 IS NOT NULL
  AND cp.nombre = iq.procedimiento_2
  AND iq.procedimiento_2_id IS NULL;

UPDATE public.intervenciones_quirurgicas iq
SET procedimiento_3_id = cp.id
FROM public.catalogo_procedimientos cp
WHERE iq.procedimiento_3 IS NOT NULL
  AND cp.nombre = iq.procedimiento_3
  AND iq.procedimiento_3_id IS NULL;

UPDATE public.intervenciones_quirurgicas iq
SET procedimiento_4_id = cp.id
FROM public.catalogo_procedimientos cp
WHERE iq.procedimiento_4 IS NOT NULL
  AND cp.nombre = iq.procedimiento_4
  AND iq.procedimiento_4_id IS NULL;

UPDATE public.intervenciones_quirurgicas iq
SET procedimiento_5_id = cp.id
FROM public.catalogo_procedimientos cp
WHERE iq.procedimiento_5 IS NOT NULL
  AND cp.nombre = iq.procedimiento_5
  AND iq.procedimiento_5_id IS NULL;

COMMIT;

-- Verificación
SELECT
  COUNT(*) FILTER (WHERE procedimiento_principal_id IS NOT NULL) AS p1,
  COUNT(*) FILTER (WHERE procedimiento_2_id       IS NOT NULL) AS p2,
  COUNT(*) FILTER (WHERE procedimiento_3_id       IS NOT NULL) AS p3,
  COUNT(*) FILTER (WHERE procedimiento_4_id       IS NOT NULL) AS p4,
  COUNT(*) FILTER (WHERE procedimiento_5_id       IS NOT NULL) AS p5,
  COUNT(*) AS total
FROM public.intervenciones_quirurgicas;

-- ============================================================
-- >>> FIN: 041_intervenciones_quirurgicas_catalogo_procedimientos.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 042_proce_medicos_area_cuerpo.sql
-- ============================================================

-- ============================================================
-- 042_proce_medicos_area_cuerpo.sql
-- Conecta cada `proce_medicos` (procedimiento realizado) con
-- el área del cuerpo intervenida (catálogo
-- `area_cuerpo_intervenida`). Opcional, FK nullable.
--
-- Justificación clínica:
--   "Osteosíntesis de radio" no es igual a "Osteosíntesis de
--   cúbito". Registrar el área intervenida (radio, cúbito,
--   cadera, dedo, etc.) es fundamental para estadísticas y
--   auditoría clínica.
-- ============================================================

BEGIN;

ALTER TABLE public.proce_medicos
    ADD COLUMN IF NOT EXISTS id_area_cuerpo_intervenida INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'proce_medicos_id_area_cuerpo_intervenida_fkey'
    ) THEN
        ALTER TABLE public.proce_medicos
        ADD CONSTRAINT proce_medicos_id_area_cuerpo_intervenida_fkey
        FOREIGN KEY (id_area_cuerpo_intervenida)
        REFERENCES public.area_cuerpo_intervenida(id)
        ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_pm_area_cuerpo
    ON public.proce_medicos(id_area_cuerpo_intervenida);

-- Backfill: para los procedimientos que ya tienen área(s)
-- asignada(s) en `procedimientos_area_cuerpo`, propagamos
-- la PRIMERA al registro histórico de proce_medicos.
UPDATE public.proce_medicos pm
SET id_area_cuerpo_intervenida = sub.id_area_cuerpo
FROM (
    SELECT DISTINCT ON (pac.id_procedimiento)
        pac.id_procedimiento,
        pac.id_area_cuerpo
    FROM public.procedimientos_area_cuerpo pac
    ORDER BY pac.id_procedimiento, pac.id_area_cuerpo
) sub
WHERE pm.id_catalogo_procedimiento IS NOT NULL
  AND pm.id_area_cuerpo_intervenida IS NULL
  AND pm.id_catalogo_procedimiento = sub.id_procedimiento;

COMMIT;

-- Verificación
SELECT
    COUNT(*) FILTER (WHERE id_area_cuerpo_intervenida IS NOT NULL) AS con_area,
    COUNT(*) FILTER (WHERE id_area_cuerpo_intervenida IS NULL)     AS sin_area,
    COUNT(*) AS total
FROM public.proce_medicos;

-- ============================================================
-- >>> FIN: 042_proce_medicos_area_cuerpo.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 043_vistas_catalogo.sql
-- ============================================================

-- ============================================================
-- 043_vistas_catalogo.sql
-- Vista SQL que sirve como API-friendly para el catálogo maestro.
-- La API backend expone estos endpoints como JSON.
-- ============================================================

-- Vista detalle del catálogo maestro
CREATE OR REPLACE VIEW public.v_catalogo_procedimientos AS
SELECT
    cp.id,
    cp.abreviatura,
    cp.nombre,
    cp.descripcion,
    cp.anestesia,
    cp.especialidad_ref,
    e.nombre AS especialidad_nombre,
    cp.activo,
    cp.created_at,
    cp.updated_at
FROM public.catalogo_procedimientos cp
LEFT JOIN public.especialidades e ON e.id = cp.especialidad_ref;

-- Vista detalle de áreas del cuerpo
CREATE OR REPLACE VIEW public.v_areas_cuerpo AS
SELECT
    a.id, a.codigo, a.nombre, a.region, a.descripcion,
    a.activo, a.created_at, a.updated_at,
    (SELECT COUNT(*) FROM public.procedimientos_area_cuerpo pac WHERE pac.id_area_cuerpo = a.id) AS total_procedimientos
FROM public.area_cuerpo_intervenida a;

-- ============================================================
-- >>> FIN: 043_vistas_catalogo.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 044_procedimientos_parto_unificar.sql
-- ============================================================

-- ============================================================
-- 044_procedimientos_parto_unificar.sql
-- Fusiona "Parto Vaginal" (id 47) dentro de
-- "Parto Eutócico Simple" (id 97).
--
-- Decisión clínica: ambos términos describen el mismo
-- procedimiento. Se conserva la nomenclatura institucional
-- "Parto Eutócico Simple (Parto Vaginal)" como nombre canónico.
-- ============================================================

BEGIN;

-- 1) Renombrar id 97 al nombre canónico combinado
UPDATE procedimientos
SET nombre = 'Parto Eutócico Simple (Parto Vaginal)'
WHERE id = 97;

-- 2) Absorber id 47 (Parto Vaginal) en id 97
DO $$
DECLARE
    ganador CONSTANT INT := 97;   -- Parto Eutócico Simple (Parto Vaginal)
    perdedor CONSTANT INT := 47;  -- Parto Vaginal
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador,
        id_catalogo_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'Parto Vaginal (id %) absorbido por Parto Eutócico Simple (id %): % referencias migradas',
        perdedor, ganador, cnt;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;

COMMIT;

-- ============================================================
-- >>> FIN: 044_procedimientos_parto_unificar.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 045_procedimientos_tenorrafia_tenoplastia.sql
-- ============================================================

-- ============================================================
-- 045_procedimientos_tenorrafia_tenoplastia.sql
-- 1) Fusiona "TENORRAFIAS (UNA O MAS)" (id 265) en
--    "Tenorrafia" (id 25). Nombre canónico: "Tenorrafia".
-- 2) Renombra "Tendinitis" (id 198) a "Tenoplastia" porque
--    "Tendinitis" es un diagnóstico (no un procedimiento).
-- 3) Aplica los mismos cambios en `catalogo_procedimientos`.
--
-- No se toca id 176 (Liberación Túnel del Carpo Dedo en
-- Gatillo Tendinitis Quervain): es nombre específico distinto.
-- ============================================================

BEGIN;

-- ─── Tabla legacy `procedimientos` ────────────────────────

-- 1) Fusionar TENORRAFIAS (265) → Tenorrafia (25)
DO $$
DECLARE
    ganador CONSTANT INT := 25;   -- Tenorrafia
    perdedor CONSTANT INT := 265; -- TENORRAFIAS (UNA O MAS)
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'TENORRAFIAS (UNA O MAS) absorbido por Tenorrafia: % referencias migradas', cnt;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;

-- 2) Renombrar Tendinitis (198) → Tenoplastia
UPDATE procedimientos
SET nombre = 'Tenoplastia'
WHERE id = 198 AND nombre = 'Tendinitis';

-- ─── Tabla maestra `catalogo_procedimientos` ─────────────

-- 1) Fusionar TENORRAFIAS (cat 230) → Tenorrafia (cat 24)
DO $$
DECLARE
    ganador CONSTANT INT := 24;
    perdedor CONSTANT INT := 230;
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'catálogo: TENORRAFIAS absorbido por Tenorrafia: % referencias migradas', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

-- 2) Renombrar Tendinitis (cat 176) → Tenoplastia
UPDATE catalogo_procedimientos
SET nombre = 'Tenoplastia'
WHERE id = 176 AND nombre = 'Tendinitis';

COMMIT;

-- ============================================================
-- >>> FIN: 045_procedimientos_tenorrafia_tenoplastia.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 046_procedimientos_descripciones_resumidas.sql
-- ============================================================

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

-- ============================================================
-- >>> FIN: 046_procedimientos_descripciones_resumidas.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 047_procedimientos_dedo_gatillo_dequervain.sql
-- ============================================================

-- ============================================================
-- 047_procedimientos_dedo_gatillo_dequervain.sql
-- Separa el procedimiento combinado id 176 ("LTCGTQ") en dos:
--   - "Liberación de Dedo en Gatillo" (Tenosinovitis estenosante)
--   - "Liberación de De Quervain" (Tenosinovitis de Quervain)
--
-- Decisión clínica:
--   Ambos procedimientos son distintos y deben estar separados
--   para fines de estadística y registro clínico.
--
-- Estrategia:
--   1. Renombrar id 176 → "Liberación de Dedo en Gatillo" (LDG).
--      Esta es la versión dominante del antiguo nombre combinado.
--   2. Crear nuevo registro "Liberación de De Quervain" (LDQ).
--      Los registros históricos quedan apuntando a LDG (dedo en
--      gatillo) porque ese era el procedimiento más frecuente.
--   3. Aplicar en `procedimientos` y `catalogo_procedimientos`.
--   4. Asignar descripciones clínicas concisas.
-- ============================================================

BEGIN;

-- ─── Tabla legacy `procedimientos` ────────────────────────

UPDATE procedimientos
SET nombre = 'Liberación de Dedo en Gatillo',
    abreviatura = 'LDG'
WHERE id = 176;

UPDATE procedimientos
SET descripcion = 'Incisión milimétrica en palma y corte de polea A1 para liberar el deslizamiento del tendón.'
WHERE id = 176;

INSERT INTO procedimientos (abreviatura, nombre, descripcion, anestesia)
SELECT 'LDQ',
       'Liberación de De Quervain',
       'Apertura del primer compartimento dorsal para liberar los tendones abductor largo y extensor corto del pulgar.',
       1
WHERE NOT EXISTS (
    SELECT 1 FROM procedimientos WHERE nombre = 'Liberación de De Quervain'
);

-- ─── Tabla maestra `catalogo_procedimientos` ─────────────

UPDATE catalogo_procedimientos
SET nombre = 'Liberación de Dedo en Gatillo',
    abreviatura = 'LDG'
WHERE id = 159;

UPDATE catalogo_procedimientos
SET descripcion = 'Incisión milimétrica en palma y corte de polea A1 para liberar el deslizamiento del tendón.'
WHERE id = 159;

INSERT INTO catalogo_procedimientos (abreviatura, nombre, descripcion, anestesia, especialidad_ref, activo)
SELECT 'LDQ',
       'Liberación de De Quervain',
       'Apertura del primer compartimento dorsal para liberar los tendones abductor largo y extensor corto del pulgar.',
       1,
       NULL,
       TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM catalogo_procedimientos WHERE nombre = 'Liberación de De Quervain'
);

COMMIT;

-- ============================================================
-- >>> FIN: 047_procedimientos_dedo_gatillo_dequervain.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 048_procedimientos_eliminar_stcpaf.sql
-- ============================================================

-- ============================================================
-- 048_procedimientos_eliminar_stcpaf.sql
-- Elimina el procedimiento "Sx Tunel Del Carpo Pseudo Artrosis
-- Fermur" (id 168 en `procedimientos`, id 148 en
-- `catalogo_procedimientos`).
--
-- Justificación clínica:
--   La pseudoartrosis de fémur se trata mediante Osteosíntesis,
--   no como un síndrome del túnel carpiano. La mezcla de
--   conceptos clínicos indica un error de captura en el catálogo.
--
-- Se conserva el registro en `proce_medicos` apuntando a NULL
-- (id_procedimiento queda libre) para no perder auditoría.
-- ============================================================

BEGIN;

-- 1) Eliminar FKs en proce_medicos (set NULL en lugar de borrar)
UPDATE proce_medicos
SET id_procedimiento = NULL,
    id_catalogo_procedimiento = NULL
WHERE id_procedimiento = 168
   OR id_catalogo_procedimiento = 148;

-- 2) Eliminar del catálogo maestro
DELETE FROM catalogo_procedimientos WHERE id = 148;

-- 3) Eliminar del catálogo legacy
DELETE FROM procedimientos WHERE id = 168;

COMMIT;

-- ============================================================
-- >>> FIN: 048_procedimientos_eliminar_stcpaf.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 049_procedimientos_descompresion_ner_medio_unificar.sql
-- ============================================================

-- ============================================================
-- 049_procedimientos_descompresion_ner_medio_unificar.sql
-- Unifica "Liberación de Túnel del Carpo" (id 38 / cat 37) con
-- "Liberacion De Tunel Carpiano" (id 161 / cat 143) en un único
-- procedimiento:
--   "Descompresión del Nervio Mediano" (DNMC)
--
-- Justificación clínica:
--   Ambos nombres describen el mismo procedimiento quirúrgico
--   (liberación del túnel carpiano / descompresión del nervio
--   mediano). El término institucional canónico es
--   "Descompresión del Nervio Mediano".
-- ============================================================

BEGIN;

-- ─── Tabla legacy `procedimientos` ────────────────────────

-- Renombrar el ganador (id 38) al nombre canónico + descripción
UPDATE procedimientos
SET nombre = 'Descompresión del Nervio Mediano',
    abreviatura = 'DNMC',
    descripcion = 'Apertura del retináculo flexor para liberar la presión sobre el nervio mediano a nivel del carpo.'
WHERE id = 38;

-- Absorber id 161 → 38
DO $$
DECLARE
    ganador CONSTANT INT := 38;
    perdedor CONSTANT INT := 161;
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'LDTC absorbido por DNMC: % referencias migradas', cnt;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;

-- ─── Tabla maestra `catalogo_procedimientos` ─────────────

UPDATE catalogo_procedimientos
SET nombre = 'Descompresión del Nervio Mediano',
    abreviatura = 'DNMC',
    descripcion = 'Apertura del retináculo flexor para liberar la presión sobre el nervio mediano a nivel del carpo.'
WHERE id = 37;

DO $$
DECLARE
    ganador CONSTANT INT := 37;
    perdedor CONSTANT INT := 143;
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'catálogo: LDTC absorbido por DNMC: % referencias migradas', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

COMMIT;

-- ============================================================
-- >>> FIN: 049_procedimientos_descompresion_ner_medio_unificar.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 050_procedimientos_tunel_carpo_nombres_dual.sql
-- ============================================================

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

-- ============================================================
-- >>> FIN: 050_procedimientos_tunel_carpo_nombres_dual.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 051_procedimientos_intubacion_biopsia_unificar.sql
-- ============================================================

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

-- ============================================================
-- >>> FIN: 051_procedimientos_intubacion_biopsia_unificar.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 052_procedimientos_biopsia_generica_fusionar.sql
-- ============================================================

-- ============================================================
-- 052_procedimientos_biopsia_generica_fusionar.sql
-- Fusiona los nombres genéricos de biopsia (sin especificidad
-- anatómica) en un único registro: "Biopsia" (BIOP).
--
-- Mantiene como registros independientes los procedimientos
-- anatómicamente específicos, porque son procedimientos
-- diferentes con indicaciones distintas:
--   - Biopsia Cervical (BIOCER)
--   - Biopsia Endometrial (BE)
--   - Biopsia de Mama (BIOMAMA)
--   - Biopsia de Vulva (BIOVU)
--   - Biopsia de Trucut (BIOTRU)
--
-- Solo se absorbe "TOMA DE BIOPSIA" (TOBIO), que es el término
-- genérico duplicado.
-- ============================================================

BEGIN;

-- ─── Tabla legacy `procedimientos` ────────────────────────

DO $$
DECLARE
    ganador CONSTANT INT := 22;   -- BIOP "Biopsia"
    perdedor CONSTANT INT := 274; -- TOBIO "TOMA DE BIOPSIA"
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'TOBIO absorbido por BIOP: % referencias migradas', cnt;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;

UPDATE procedimientos
SET descripcion = 'Toma de muestra de tejido para análisis histopatológico.'
WHERE id = 22;

-- ─── Tabla maestra `catalogo_procedimientos` ─────────────

DO $$
DECLARE
    ganador CONSTANT INT := 21;   -- BIOP "Biopsia" (catálogo)
    perdedor CONSTANT INT := 236; -- TOBIO (catálogo)
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'catálogo: TOBIO absorbido por BIOP: % referencias migradas', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

UPDATE catalogo_procedimientos
SET descripcion = 'Toma de muestra de tejido para análisis histopatológico.'
WHERE id = 21;

COMMIT;

-- ============================================================
-- >>> FIN: 052_procedimientos_biopsia_generica_fusionar.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 053_procedimientos_biopsia_unica.sql
-- ============================================================

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

-- ============================================================
-- >>> FIN: 053_procedimientos_biopsia_unica.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 054_procedimientos_vac_unificar.sql
-- ============================================================

-- ============================================================
-- 054_procedimientos_vac_unificar.sql
-- Fusiona todos los procedimientos relacionados con VAC
-- en un único registro: "VAC" (id 12 / cat 12).
--
-- Variantes absorbidas:
--   id 170 CDV   "Cambio De Vas"       (typo: Vas → VAC)
--   id 203 CDVAC "Colocacion De Vacc"  (typo: Vacc → VAC)
--
-- Mantiene id 91 CAM "Cambio De Artrotomia" independiente
-- (es un procedimiento ortopédico-articular, no de VAC).
-- ============================================================

BEGIN;

-- ─── Tabla legacy `procedimientos` ────────────────────────

UPDATE procedimientos
SET nombre = 'VAC',
    descripcion = 'Colocación, cambio o retiro de sistema VAC (cierre asistido por vacío).'
WHERE id = 12;

DO $$
DECLARE
    ganador CONSTANT INT := 12;
    perdedor INT;
    cnt INT;
BEGIN
    FOR perdedor IN SELECT unnest(ARRAY[170, 203]) LOOP
        UPDATE proce_medicos
        SET id_procedimiento = ganador
        WHERE id_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'Procedimiento % absorbido por VAC (12): % referencias migradas',
            perdedor, cnt;
        DELETE FROM procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

-- ─── Tabla maestra `catalogo_procedimientos` ─────────────

UPDATE catalogo_procedimientos
SET nombre = 'VAC',
    descripcion = 'Colocación, cambio o retiro de sistema VAC (cierre asistido por vacío).'
WHERE id = 12;

DO $$
DECLARE
    ganador CONSTANT INT := 12;
    perdedor INT;
    cnt INT;
BEGIN
    FOR perdedor IN SELECT unnest(ARRAY[149, 180]) LOOP
        UPDATE proce_medicos
        SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'catálogo: % absorbido por VAC (12): % referencias migradas',
            perdedor, cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

COMMIT;

-- ============================================================
-- >>> FIN: 054_procedimientos_vac_unificar.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 055_procedimientos_fusiones_lote2.sql
-- ============================================================

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

-- ============================================================
-- >>> FIN: 055_procedimientos_fusiones_lote2.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 056_procedimientos_fusiones_lote3.sql
-- ============================================================

-- ============================================================
-- 056_procedimientos_fusiones_lote3.sql
-- Aplica las fusiones confirmadas por el equipo médico:
--
--   1. DR-E (id 168) + DECO (id 226)   → "Drenaje Ecoguiado"
--   2. RETFI (id 30) + RDFIJ (id 114)  → "Retiro de Fijación Externa"
--   3. SQSV (id 116) + RQDS (id 132)  → "Resección de Quiste Sinovial"
--   4. EXTU (id 111) + EUÑA (id 198)  → "Extracción de Uña"
--   5. CEXT (id 97) + RCE (id 136)    → "Extracción de Cuerpo Extraño"
--   6. YESO (id 79) + CY (id 95)      → "Colocación de Yeso"
--   7. EXCM (id 23) + RMASA (id 121)  → "Resección de Masa de Tejido"
--   8. ADD (id 146) + ANA (id 189)    → "Amputación de Dedo"
--
-- NO se fusionan (mantener separados):
--   - MCC vs MC (caderas vs general, diferente complejidad)
--   - DEQ vs DR-E (quiste vs drenaje general, distinto insumo)
--   - YESO vs CI (inmovilización externa vs cirugía de injerto)
-- ============================================================

BEGIN;

-- ──────────── Pares simples ────────────

-- 1. DR-E absorbe DECO → "Drenaje Ecoguiado"
DO $$
DECLARE
    ganador CONSTANT INT := 168;
    perdedor CONSTANT INT := 226;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'DECO absorbido por DR-E (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Drenaje Ecoguiado',
    abreviatura = 'DR-E',
    descripcion = 'Drenaje de colección guiada por ultrasonido.'
WHERE id = 168;

-- 2. RETFI absorbe RDFIJ → "Retiro de Fijación Externa"
DO $$
DECLARE
    ganador CONSTANT INT := 30;
    perdedor CONSTANT INT := 114;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RDFIJ absorbido por RETFI (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Retiro de Fijación Externa',
    descripcion = 'Retiro del fijador externo colocado previamente.'
WHERE id = 30;

-- 3. SQSV absorbe RQDS → "Resección de Quiste Sinovial"
DO $$
DECLARE
    ganador CONSTANT INT := 116;
    perdedor CONSTANT INT := 132;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RQDS absorbido por SQSV (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Resección de Quiste Sinovial',
    abreviatura = 'SQSV',
    descripcion = 'Extirpación quirúrgica de quiste sinovial benigno.'
WHERE id = 116;

-- 4. EXTU absorbe EUÑA → "Extracción de Uña"
DO $$
DECLARE
    ganador CONSTANT INT := 111;
    perdedor CONSTANT INT := 198;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'EUÑA absorbido por EXTU (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Extracción de Uña',
    abreviatura = 'EXTU',
    descripcion = 'Onicectomía: extracción de la uña afectada.'
WHERE id = 111;

-- 5. CEXT absorbe RCE → "Extracción de Cuerpo Extraño"
DO $$
DECLARE
    ganador CONSTANT INT := 97;
    perdedor CONSTANT INT := 136;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RCE absorbido por CEXT (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Extracción de Cuerpo Extraño',
    descripcion = 'Remoción quirúrgica de un cuerpo extraño.'
WHERE id = 97;

-- 6. YESO absorbe CY → "Colocación de Yeso"
DO $$
DECLARE
    ganador CONSTANT INT := 79;
    perdedor CONSTANT INT := 95;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'CY absorbido por YESO (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Yeso',
    abreviatura = 'YESO',
    descripcion = 'Inmovilización externa con vendaje de yeso.'
WHERE id = 79;

-- 7. EXCM absorbe RMASA → "Resección de Masa de Tejido"
-- (Escisión y resección son sinónimos quirúrgicos para masa)
DO $$
DECLARE
    ganador CONSTANT INT := 23;
    perdedor CONSTANT INT := 121;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RMASA absorbido por EXCM (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Resección de Masa de Tejido',
    abreviatura = 'EXCM',
    descripcion = 'Escisión quirúrgica de una masa tumoral de tejido.'
WHERE id = 23;

-- 8. ADD absorbe ANA → "Amputación de Dedo"
DO $$
DECLARE
    ganador CONSTANT INT := 146;
    perdedor CONSTANT INT := 189;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'ANA absorbido por ADD (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Amputación de Dedo',
    abreviatura = 'ADD',
    descripcion = 'Amputación quirúrgica de un dedo (mano o pie).'
WHERE id = 146;

COMMIT;

-- ============================================================
-- >>> FIN: 056_procedimientos_fusiones_lote3.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 057_procedimientos_fusiones_lote4.sql
-- ============================================================

-- [ADAPTADO] Helper para resolver ids del catálogo por abreviatura.
-- La BD `hospital` local fue poblada desde un `procedimientos` con
-- orden/ids ligeramente distinto al baseline original (p. ej. el OUB
-- real vive en el id 253, no en el 252), así que las migraciones de
-- este punto en adelante ya no referencian ids fijos: resuelven por
-- abreviatura. Devuelve NULL si no existe (operación = no-op seguro).
CREATE OR REPLACE FUNCTION cat_id(abreviacion text) RETURNS int
LANGUAGE sql STABLE AS $$
    SELECT id FROM catalogo_procedimientos WHERE abreviatura = abreviacion LIMIT 1;
$$;

-- ============================================================
-- 057_procedimientos_fusiones_lote4.sql
-- Lote 4: fusiones confirmadas del tercer análisis.
--
--   1. RETFI (id 30)  + RDFE (id 141)  → "Retiro de Fijación Externa"
--   2. SQSV (id 116) + RDQS (id 144)  → "Resección de Quiste Sinovial"
--   3. COLPA (id 51) + COLFPOST (id 117)→ "Colporrafia"
--   4. AUB  (id 225) + OUB  (id 252)  → "Ooforectomía Unilateral o Bilateral"
--   5. EXTL (id 94)  + RESCP (id 235) → "Resección de Lipoma"
--
-- Mantener separados (decisión clínica):
--   - MCC vs MC (caderas vs general)
--   - DEQ vs DR-E (quiste vs drenaje general)
--   - YESO vs CI (inmovilización vs injerto)
--   - SQSV vs DREQS (resección vs drenaje)
--   - CDCO "Oyster" (revisar typo)
-- ============================================================

BEGIN;

-- 1. RETFI absorbe RDFE
DO $$
DECLARE
    ganador CONSTANT INT := 30;
    perdedor CONSTANT INT := 141;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RDFE absorbido por RETFI (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET descripcion = 'Retiro del fijador externo colocado previamente.'
WHERE id = 30;

-- 2. SQSV absorbe RDQS (resección vs retiro, mismo concepto de quiste sinovial)
DO $$
DECLARE
    ganador CONSTANT INT := 116;
    perdedor CONSTANT INT := 144;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RDQS absorbido por SQSV (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET descripcion = 'Extirpación quirúrgica de quiste sinovial benigno.'
WHERE id = 116;

-- 3. COLPA absorbe COLFPOST
DO $$
DECLARE
    ganador CONSTANT INT := 51;
    perdedor CONSTANT INT := 117;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'COLFPOST absorbido por COLPA (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET descripcion = 'Reparación quirúrgica de la pared vaginal (colporrafia anterior/posterior).'
WHERE id = 51;

-- 4. OUB absorbe AUB (OUB es más general, cubre ambos casos)
-- [ADAPTADO] Resuelto por abreviatura: en esta BD el OUB vive en el id 253.
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE abreviatura = 'OUB';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE abreviatura = 'AUB';
    IF ganador IS NOT NULL AND perdedor IS NOT NULL THEN
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'AUB absorbido por OUB (% refs)', cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    ELSE
        RAISE NOTICE 'OUB/AUB no encontrados por abreviatura (skip)';
    END IF;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Ooforectomía Unilateral o Bilateral',
    abreviatura = 'OUB',
    descripcion = 'Extirpación de uno o ambos ovarios.'
WHERE abreviatura = 'OUB';

-- 5. EXTL absorbe RESCP (mismo concepto: lipoma)
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE abreviatura = 'EXTL';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE abreviatura = 'RESCP';
    IF ganador IS NOT NULL AND perdedor IS NOT NULL THEN
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'RESCP absorbido por EXTL (% refs)', cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    ELSE
        RAISE NOTICE 'EXTL/RESCP no encontrados por abreviatura (skip)';
    END IF;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Extracción de Lipomas',
    abreviatura = 'EXTL',
    descripcion = 'Resección quirúrgica de uno o varios lipomas.'
WHERE abreviatura = 'EXTL';

COMMIT;

-- ============================================================
-- >>> FIN: 057_procedimientos_fusiones_lote4.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 058_procedimientos_fusiones_lote5.sql
-- ============================================================

-- ============================================================
-- 058_procedimientos_fusiones_lote5.sql
-- Lote 5: fusiones confirmadas por el equipo clínico.
--
-- Bloque fusiones (4):
--   1. RETGR (id 19)  + RGQ  (id 109) → "Retiro de Grapas Quirúrgicas"
--   2. RDIU (id 56)  + RDTC (id 203) → "Retiro de Dispositivo Intrauterino (DIU)"
--   3. RVC  (id 4)   + RCS  (id 118) → "Retiro de Catéter Venoso Central"
--   4. RETMO (id 28) + RMA  (id 123) → "Retiro de Material de Osteosíntesis"
--
-- Mantener separados (decisión clínica):
--   - RCIM  vs RETMO  : extracción con instrumental específico (quirófano)
--   - RETFI vs RETMO  : pines externos vs material interno
--   - RESPI vs RY     : yeso masivo (niños) vs yeso simple
--   - RJAD  (Jadelle) : implante subdérmico anticonceptivo
--   - RTT   (transindesmal): minicirugía traumatológica puntual
-- ============================================================

BEGIN;

-- 1. RETGR absorbe RGQ → "Retiro de Grapas Quirúrgicas"
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE abreviatura = 'RETGR';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE abreviatura = 'RGQ';
    IF ganador IS NOT NULL AND perdedor IS NOT NULL THEN
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'RGQ absorbido por RETGR (% refs)', cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    ELSE
        RAISE NOTICE 'RETGR/RGQ no encontrados por abreviatura (skip)';
    END IF;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Retiro de Grapas Quirúrgicas',
    abreviatura = 'RETGR',
    descripcion = 'Remoción de grapas de cierre quirúrgico o quirúrgicas.'
WHERE abreviatura = 'RETGR';

-- 2. RDIU absorbe RDTC → "Retiro de Dispositivo Intrauterino (DIU)"
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE abreviatura = 'RDIU';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE abreviatura = 'RDTC';
    IF ganador IS NOT NULL AND perdedor IS NOT NULL THEN
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'RDTC absorbido por RDIU (% refs)', cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    ELSE
        RAISE NOTICE 'RDIU/RDTC no encontrados por abreviatura (skip)';
    END IF;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Retiro de Dispositivo Intrauterino (DIU)',
    abreviatura = 'RDIU',
    descripcion = 'Extracción del DIU (Dispositivo Intrauterino), incluyendo T de Cobre.'
WHERE abreviatura = 'RDIU';

-- 3. RVC absorbe RCS → "Retiro de Catéter Venoso Central"
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE abreviatura = 'RVC';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE abreviatura = 'RCS';
    IF ganador IS NOT NULL AND perdedor IS NOT NULL THEN
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'RCS absorbido por RVC (% refs)', cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    ELSE
        RAISE NOTICE 'RVC/RCS no encontrados por abreviatura (skip)';
    END IF;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Retiro de Catéter Venoso Central',
    abreviatura = 'RVC',
    descripcion = 'Remoción de catéter venoso central, incluyendo subclavio.'
WHERE abreviatura = 'RVC';

-- 4. RETMO absorbe RMA → "Retiro de Material de Osteosíntesis"
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE abreviatura = 'RETMO';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE abreviatura = 'RMA';
    IF ganador IS NOT NULL AND perdedor IS NOT NULL THEN
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'RMA absorbido por RETMO (% refs)', cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    ELSE
        RAISE NOTICE 'RETMO/RMA no encontrados por abreviatura (skip)';
    END IF;
END $$;
UPDATE catalogo_procedimientos
SET descripcion = 'Retiro de placas, clavos, tornillos u otro material de osteosíntesis interna.'
WHERE abreviatura = 'RETMO';

COMMIT;

-- ============================================================
-- >>> FIN: 058_procedimientos_fusiones_lote5.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 059_procedimientos_hernioplastia_crear.sql
-- ============================================================

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
WHERE abreviatura = 'HERM';

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

-- ============================================================
-- >>> FIN: 059_procedimientos_hernioplastia_crear.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 060_procedimientos_fusiones_lote6.sql
-- ============================================================

-- ============================================================
-- 060_procedimientos_fusiones_lote6.sql
-- Lote 6: fusiones de accesos vasculares y traumatología.
--
-- Grupo 1: Catéteres venosos centrales
--   CCCS (88) absorbe a CDCO, CDCV, CDCYU
--   → "Colocación de Catéter Venoso Central" (CCCS)
--
-- Grupo 2: Traumatología e inmovilizaciones
--   CI absorbe a TCIP → "Colocación de Injerto" (genérico)
--   YESO absorbe a CCP → "Colocación de Yeso o Férula"
--   CV absorbe a CVU  → "Colocación de Vendajes Especializados"
-- ============================================================

BEGIN;

-- ──────────── Grupo 1: Catéteres ────────────
DO $$
DECLARE
    ganador int;
    perdedor text;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE abreviatura = 'CCCS';
    FOR perdedor IN SELECT abreviatura FROM catalogo_procedimientos WHERE abreviatura IN ('CDCO','CDCV','CDCYU') LOOP
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = cat_id(perdedor);
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'Catéter: % absorbido por CCCS (% refs)', perdedor, cnt;
        DELETE FROM catalogo_procedimientos WHERE id = cat_id(perdedor);
    END LOOP;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Catéter Venoso Central',
    abreviatura = 'CCCS',
    descripcion = 'Inserción de catéter venoso central. Incluye accesos subclavios, yugulares y marcas comerciales.'
WHERE abreviatura = 'CCCS';

-- ──────────── Grupo 2a: Injerto ────────────
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE abreviatura = 'CI';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE abreviatura = 'TCIP';
    IF ganador IS NOT NULL AND perdedor IS NOT NULL THEN
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'TCIP absorbido por CI (% refs)', cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    ELSE
        RAISE NOTICE 'CI/TCIP no encontrados por abreviatura (skip)';
    END IF;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Injerto',
    abreviatura = 'CI',
    descripcion = 'Colocación de injerto (cutáneo, óseo u otro) en zona receptora.'
WHERE abreviatura = 'CI';

-- ──────────── Grupo 2b: Yeso + Canal Posterior ────────────
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE abreviatura = 'YESO';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE abreviatura = 'CCP';
    IF ganador IS NOT NULL AND perdedor IS NOT NULL THEN
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'CCP absorbido por YESO (% refs)', cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    ELSE
        RAISE NOTICE 'YESO/CCP no encontrados por abreviatura (skip)';
    END IF;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Yeso o Férula',
    abreviatura = 'YESO',
    descripcion = 'Inmovilización externa con yeso, férula posterior o canal abierto.'
WHERE abreviatura = 'YESO';

-- ──────────── Grupo 2c: Vendajes + Velpeau ────────────
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE abreviatura = 'CV';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE abreviatura = 'CVU';
    IF ganador IS NOT NULL AND perdedor IS NOT NULL THEN
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'CVU absorbido por CV (% refs)', cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    ELSE
        RAISE NOTICE 'CV/CVU no encontrados por abreviatura (skip)';
    END IF;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Vendajes Especializados',
    abreviatura = 'CV',
    descripcion = 'Vendaje especializado tipo Velpeau u otros vendajes de hombro y brazo.'
WHERE abreviatura = 'CV';

COMMIT;

-- ============================================================
-- >>> FIN: 060_procedimientos_fusiones_lote6.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 061_procedimientos_ajuste_injerto.sql
-- ============================================================

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
WHERE abreviatura = 'CI';

COMMIT;

-- ============================================================
-- >>> FIN: 061_procedimientos_ajuste_injerto.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 062_procedimientos_quirurgicos_normalizar.sql
-- ============================================================

-- ============================================================
-- 062_procedimientos_quirurgicos_normalizar.sql
-- Normaliza mayúsculas/tildes y agrega descripciones clínicas
-- a los procedimientos que el equipo confirmó como independientes.
-- Ninguno de estos se fusiona con otro.
--
-- Procedimientos tocados:
--   FIJEX    (id 29)   Colocación de Fijador Externo
--   CTI      (id 93)   Colocación de Tubo Intercostal
--   CBDB     (id 188)  Colocación de Barra Denis Browne
--   DIU      (id 55)   Colocación de DIU
--   COLJADE  (id 254)  Colocación de Jadelle
--   SONDA    (id 5)    Colocación de Sonda
--   CDM      (id 133)  Colocación de Membrana
--   CS       (id 103)  Colocación de Surfactante
--   COLB-LY  (id 105)  Colocación de Sutura de B-Lynch
--   TCPO     (id 166)  Toma y Colocación de Puntos Óseos
-- ============================================================

BEGIN;

-- Colocación de Fijador Externo (inverso a RETFI)
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Fijador Externo',
    descripcion = 'Colocación quirúrgica de fijador externo (pines y barras) para estabilización de fractura.'
WHERE abreviatura = 'FIJEX';

-- Colocación de Tubo Intercostal (pleurotomía de emergencia)
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Tubo Intercostal',
    abreviatura = 'CTI',
    descripcion = 'Pleurotomía cerrada o tubo de tórax para neumotórax, hemotórax o derrame pleural.'
WHERE abreviatura = 'CTI';

-- Colocación de Barra Denis Browne (pediatría, pie equinovaro)
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Barra Denis Browne',
    abreviatura = 'CBDB',
    descripcion = 'Dispositivo ortopédico pediátrico (barra metálica + botas) para corrección de pie equinovaro.'
WHERE abreviatura = 'CBDB';

-- Colocación de DIU (inserción, inversa a RDIU)
UPDATE catalogo_procedimientos
SET descripcion = 'Inserción de dispositivo intrauterino (DIU) como método anticonceptivo de larga duración.'
WHERE abreviatura = 'DIU';

-- Colocación de Jadelle (planificación familiar, inversa a RJAD)
UPDATE catalogo_procedimientos
SET descripcion = 'Inserción de implante subdérmico anticonceptivo (Jadelle) en el brazo.'
WHERE abreviatura = 'COLJADE';

-- Colocación de Sonda (orogástrica o Foley)
UPDATE catalogo_procedimientos
SET descripcion = 'Inserción de sonda orogástrica, vesical (Foley) o nasogástrica.'
WHERE abreviatura = 'SONDA';

-- Colocación de Membrana (membrana amniótica o biológica)
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Membrana',
    abreviatura = 'CDM',
    descripcion = 'Aplicación de membrana amniótica o biológica en cirugía oftálmica, maxilofacial o de herida crónica.'
WHERE abreviatura = 'CDM';

-- Colocación de Surfactante (neonatología)
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Surfactante',
    abreviatura = 'CS',
    descripcion = 'Administración de surfactante pulmonar en neonatos prematuros (vía tubo endotraqueal).'
WHERE abreviatura = 'CS';

-- Colocación de Sutura de B-Lynch (ginecología de emergencia)
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Sutura de B-Lynch',
    abreviatura = 'COLB-LY',
    descripcion = 'Sutura uterina compresiva de emergencia para hemorragia masiva postparto.'
WHERE abreviatura = 'COLB-LY';

-- Toma y Colocación de Puntos Óseos (traumatología)
UPDATE catalogo_procedimientos
SET nombre = 'Toma y Colocación de Puntos Óseos',
    abreviatura = 'TCPO',
    descripcion = 'Fijación directa en hueso con alambres o suturas pesadas (cerclaje) en traumatología.'
WHERE abreviatura = 'TCPO';

COMMIT;

-- ============================================================
-- >>> FIN: 062_procedimientos_quirurgicos_normalizar.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 063_procedimientos_normalizacion_masiva.sql
-- ============================================================

-- ============================================================
-- 063_procedimientos_normalizacion_masiva.sql
-- Normaliza nombres (MAYÚSCULAS → Título con acentos) y agrega
-- descripciones clínicas a los 101 procedimientos pendientes
-- del catálogo maestro.
--
-- Criterios:
--   * Convertir TODAS LAS MAYÚSCULAS a minúsculas con Title Case
--   * Aplicar acentos correctos (Resección, Inyección, etc.)
--   * Asignar descripción clínica concisa por procedimiento
--   * Corregir typos conocidos (Reseccin → Resección, etc.)
--
-- No se fusionan procedimientos. Esto solo limpia nombres
-- y descripciones.
-- ============================================================

BEGIN;

-- Procedimientos donde ya hay descripción clínica o son válidos en mayúscula
-- Sólo normalizamos: nombre a Título, y asignamos descripción si falta.

-- ─── Ginecología / Obstetricia ───
UPDATE catalogo_procedimientos SET nombre = 'Parto Eutócico Simple', descripcion = 'Parto vaginal espontáneo sin complicaciones.' WHERE unaccent(upper(nombre)) = unaccent(upper(nombre)) AND unaccent(upper(nombre)) = 'PARTO EUTCICO SIMPLE';
UPDATE catalogo_procedimientos SET nombre = 'Reparación de Desgarro Vaginal', descripcion = 'Sutura del desgarro perineal/vaginal postparto.' WHERE unaccent(upper(nombre)) = 'REPARACION DE DESGARRO VAGINA';
UPDATE catalogo_procedimientos SET nombre = 'Reparación de Desgarro Cervical', descripcion = 'Sutura del desgarro del cuello uterino postparto.' WHERE unaccent(upper(nombre)) = 'REPARACION DE DESGARRO CERVICAL';
UPDATE catalogo_procedimientos SET nombre = 'Legrado Instrumental Uterino', abreviatura = 'LIU', descripcion = 'Legrado uterino evacuador o diagnóstico con cureta.' WHERE unaccent(upper(nombre)) = 'LEGRADO INSTRUMENTAL UTERINO';
UPDATE catalogo_procedimientos SET nombre = 'Fimbriectomía', descripcion = 'Resección de fimbrias tubáricas.' WHERE unaccent(upper(nombre)) = 'FIMBRIECTOMIA';
UPDATE catalogo_procedimientos SET nombre = 'Histerectomía Abdominal Total', descripcion = 'Extirpación quirúrgica del útero por vía abdominal.' WHERE unaccent(upper(nombre)) = 'HISTERECTOMIA ABDOMINAL TOTAL';
UPDATE catalogo_procedimientos SET nombre = 'Histerectomía Vaginal', descripcion = 'Extirpación del útero por vía vaginal.' WHERE unaccent(upper(nombre)) = 'HISTERECTOMIA VAGINAL';
UPDATE catalogo_procedimientos SET nombre = 'Ligadura de Arteria Uterina', descripcion = 'Ligadura hemostática de arterias uterinas en hemorragia.' WHERE unaccent(upper(nombre)) = 'LIGADURA DE ARTERIA UTERINA';
UPDATE catalogo_procedimientos SET nombre = 'Histerectomía Obstétrica', descripcion = 'Histerectomía de emergencia postparto.' WHERE unaccent(upper(nombre)) = 'HISTERECTOMIA OBSTETRICA';
UPDATE catalogo_procedimientos SET nombre = 'Extracción Manual de Placenta', descripcion = 'Remoción manual de placenta retenida postparto.' WHERE unaccent(upper(nombre)) = 'EXTRACCION MANUAL DE PLACENTA';
UPDATE catalogo_procedimientos SET nombre = 'Colporrafia Anterior', descripcion = 'Reparación quirúrgica de la pared vaginal anterior (cistocele).' WHERE unaccent(upper(nombre)) = 'COLPORRAFIA ANTERIOR';
UPDATE catalogo_procedimientos SET nombre = 'Prolapso Rectal', descripcion = 'Reducción de prolapso rectal.' WHERE unaccent(upper(nombre)) = 'PROLAPSO RECTAL';
UPDATE catalogo_procedimientos SET nombre = 'Exploración Pélvica', descripcion = 'Exploración quirúrgica o manual de la pelvis.' WHERE unaccent(upper(nombre)) = 'EXPLORACION PELVICA';
UPDATE catalogo_procedimientos SET nombre = 'Drenaje de Lipoma', descripcion = 'Drenaje o evacuación de lipoma.' WHERE unaccent(upper(nombre)) = 'DRENAJE DE LIPOMA';

-- ─── Traumatología / Ortopedia ───
UPDATE catalogo_procedimientos SET nombre = 'Cambio de Artrotomía', abreviatura = 'CAM', descripcion = 'Cambio de apósitos o revisión de artrotomía previa.' WHERE unaccent(upper(nombre)) = unaccent(upper('CAMBIO DE ARTROTOMIA'));
UPDATE catalogo_procedimientos SET nombre = 'Cambio de Membranas', abreviatura = 'CMEMB', descripcion = 'Cambio de apósitos y drenaje de herida con membrana.' WHERE unaccent(upper(nombre)) = unaccent(upper('CAMBIO DE MEMBRANAS'));
UPDATE catalogo_procedimientos SET nombre = 'Drenaje de Membranas', abreviatura = 'DM', descripcion = 'Drenaje a través de membrana cerrada o abierta.' WHERE unaccent(upper(nombre)) = unaccent(upper('DRENAJE DE MEMBRANAS'));
UPDATE catalogo_procedimientos SET nombre = 'Amputación Supracondílea', descripcion = 'Amputación de fémur distal, por encima de los cóndilos.' WHERE unaccent(upper(nombre)) = unaccent(upper('AMPUTACION SUPRACONDILEA'));
UPDATE catalogo_procedimientos SET nombre = 'Amputación Infracondílea', descripcion = 'Amputación de tibia, por debajo de los cóndilos femorales.' WHERE unaccent(upper(nombre)) = unaccent(upper('AMPUTACION INFRACONDILEA'));
UPDATE catalogo_procedimientos SET nombre = 'Amputación en Raqueta de Dedo', descripcion = 'Amputación quirúrgica de dedo con colgajo en raqueta.' WHERE unaccent(upper(nombre)) = unaccent(upper('AMPUTACION EN RAQUETA DE DEDO'));
UPDATE catalogo_procedimientos SET nombre = 'Reconstrucción de Dedo', descripcion = 'Reconstrucción quirúrgica de un dedo (lesión o amputación parcial).' WHERE unaccent(upper(nombre)) = unaccent(upper('RECONSTRUCCION DE DEDO'));
UPDATE catalogo_procedimientos SET nombre = 'Manipulación de Antebrazo', descripcion = 'Reducción cerrada de fractura o luxación de antebrazo.' WHERE unaccent(upper(nombre)) = unaccent(upper('MANIPULACION ANTEBRAZO'));
UPDATE catalogo_procedimientos SET nombre = 'Artroplastia de Rodilla', descripcion = 'Reemplazo articular de rodilla.' WHERE unaccent(upper(nombre)) = unaccent(upper('ARTROPLASTIA DE RODILLA'));
UPDATE catalogo_procedimientos SET nombre = 'Artrodesis de Rodilla', descripcion = 'Fusión quirúrgica de la articulación de la rodilla.' WHERE unaccent(upper(nombre)) = unaccent(upper('ARTRODESIS RODILLA'));
UPDATE catalogo_procedimientos SET nombre = 'Hemiartroplastia de Cadera', descripcion = 'Reemplazo parcial de la cadera.' WHERE unaccent(upper(nombre)) = unaccent(upper('HEMIARTROPLASTIA DE CADERA'));
UPDATE catalogo_procedimientos SET nombre = 'Antrodesis de Tobillo', abreviatura = 'ADT', descripcion = 'Fusión quirúrgica de la articulación del tobillo.' WHERE unaccent(upper(nombre)) = unaccent(upper('ANTRODESIS DE TOBILLO'));
UPDATE catalogo_procedimientos SET nombre = 'Osteotomía', abreviatura = 'OTMIA', descripcion = 'Corte óseo quirúrgico para corrección de deformidad.' WHERE unaccent(upper(nombre)) = unaccent(upper('OSTEOTOMIA [OTMIA]'));
UPDATE catalogo_procedimientos SET nombre = 'Fractura Radio y Cúbito', abreviatura = 'FRC', descripcion = 'Reducción quirúrgica o tratamiento de fractura radio-cubital.' WHERE unaccent(upper(nombre)) = unaccent(upper('FRACTURA RADIO Y CUBITO'));
UPDATE catalogo_procedimientos SET nombre = 'Resección de Masa en Cuello', descripcion = 'Resección quirúrgica de masa cervical.' WHERE unaccent(upper(nombre)) = unaccent(upper('RESECCION DE MASA EN CUELLO'));
UPDATE catalogo_procedimientos SET nombre = 'Resección de Fibroma', descripcion = 'Resección quirúrgica de fibroma.' WHERE unaccent(upper(nombre)) = unaccent(upper('RESECCION FIBROMA'));
UPDATE catalogo_procedimientos SET nombre = 'Resección de Pólipo', descripcion = 'Resección quirúrgica de pólipo.' WHERE unaccent(upper(nombre)) = unaccent(upper('RESECCION DE POLIPO'));
UPDATE catalogo_procedimientos SET nombre = 'Resección Condiloma', descripcion = 'Resección quirúrgica de condiloma acuminado.' WHERE unaccent(upper(nombre)) = unaccent(upper('RESECCION CONDILOMA'));
UPDATE catalogo_procedimientos SET nombre = 'Resección Quiste', abreviatura = 'RQ', descripcion = 'Resección quirúrgica de quiste.' WHERE unaccent(upper(nombre)) = unaccent(upper('RESECCIN QUISTES'));
UPDATE catalogo_procedimientos SET nombre = 'Resección de Lesión Hiperplásica', descripcion = 'Resección quirúrgica de lesión hiperplásica.' WHERE unaccent(upper(nombre)) = unaccent(upper('RESECCION DE LESION HIPERPLASICA'));
UPDATE catalogo_procedimientos SET nombre = 'Regulación de Pulpejo', descripcion = 'Regulación quirúrgica del pulpejo (dedo).' WHERE unaccent(upper(nombre)) = unaccent(upper('REGULACION DE PULPEJO'));
UPDATE catalogo_procedimientos SET nombre = 'Liberación de Sinequias', descripcion = 'Liberación quirúrgica de adherencias/sinequias.' WHERE unaccent(upper(nombre)) = unaccent(upper('LIBERACION DE SINEQUIAS'));
UPDATE catalogo_procedimientos SET nombre = 'Retiro Transindesmal', descripcion = 'Retiro de tornillo/fijación transindesmal en tobillo.' WHERE unaccent(upper(nombre)) = unaccent(upper('RETIRO TRANSINDESMAL'));
UPDATE catalogo_procedimientos SET nombre = 'Exploración Radial', descripcion = 'Exploración quirúrgica del antebrazo/muñeca.' WHERE unaccent(upper(nombre)) = unaccent(upper('EXPLORACION RADIAL'));
UPDATE catalogo_procedimientos SET nombre = 'Exploración de Cuello', descripcion = 'Exploración quirúrgica del cuello.' WHERE unaccent(upper(nombre)) = unaccent(upper('EXPLORACION DE CUELLO'));
UPDATE catalogo_procedimientos SET nombre = 'Exploración Vascular', descripcion = 'Exploración quirúrgica de vasos sanguíneos.' WHERE unaccent(upper(nombre)) = unaccent(upper('EXPLORACION VASCULAR'));
UPDATE catalogo_procedimientos SET nombre = 'Exploración Vasos Femorales', descripcion = 'Exploración quirúrgica de vasos femorales.' WHERE unaccent(upper(nombre)) = unaccent(upper('EXPLORACION VASOS FEMORALES'));
UPDATE catalogo_procedimientos SET nombre = 'Escarectomía en Tórax', descripcion = 'Resección de tejido desvitalizado (esfacelo) en tórax.' WHERE unaccent(upper(nombre)) = unaccent(upper('ESCARECTOMIA EN TORAX'));
UPDATE catalogo_procedimientos SET nombre = 'Escarectomía Miembros Inferiores', descripcion = 'Resección de tejido desvitalizado en miembros inferiores.' WHERE unaccent(upper(nombre)) = unaccent(upper('ESCARECTOMIA MIEMBROS INFERIORES'));
UPDATE catalogo_procedimientos SET nombre = 'Escarotomías por Quemaduras', descripcion = 'Incisiones de descarga para quemaduras circulares.' WHERE unaccent(upper(nombre)) = unaccent(upper('ESCAROTOMIAS POR QUEMADURAS'));
UPDATE catalogo_procedimientos SET nombre = 'Rotación Colgajo', descripcion = 'Rotación quirúrgica de colgajo cutáneo.' WHERE unaccent(upper(nombre)) = unaccent(upper('ROTACION COLGAJO'));
UPDATE catalogo_procedimientos SET nombre = 'Manipulación de Muñeca', descripcion = 'Reducción o manipulación cerrada de muñeca.' WHERE unaccent(upper(nombre)) = unaccent(upper('MANIPULACION DE MUNECA'));
UPDATE catalogo_procedimientos SET nombre = 'Lavado y Sutura de Herida Cortocortante Traumática', descripcion = 'Limpieza y cierre de herida cortocortante traumática.' WHERE unaccent(upper(nombre)) = unaccent(upper('LAVADO/SUTURA DE HERIDA CORTOCORTANTE TRAUMATICA'));
UPDATE catalogo_procedimientos SET nombre = 'Manipulación Cerrada de Hombro', descripcion = 'Reducción cerrada de luxación o fractura de hombro.' WHERE unaccent(upper(nombre)) = unaccent(upper('MANIPULACION CERRADA DE HOMBRO'));
UPDATE catalogo_procedimientos SET nombre = 'Manipulación Cerrada de Cadera', descripcion = 'Reducción cerrada de luxación o fractura de cadera.' WHERE unaccent(upper(nombre)) = unaccent(upper('MANIPULACION CERRADA DE CADERA'));
UPDATE catalogo_procedimientos SET nombre = 'Manipulación Cerrada (General)', descripcion = 'Reducción cerrada de fractura/luxación (general).' WHERE unaccent(upper(nombre)) = unaccent(upper('MANIPULACION CERRADA (GENERAL)'));
UPDATE catalogo_procedimientos SET nombre = 'Onicectomía Dedo Mano', descripcion = 'Extracción quirúrgica de uña del dedo de la mano.' WHERE unaccent(upper(nombre)) = unaccent(upper('ONICECTOMIA DEDO MANO'));
UPDATE catalogo_procedimientos SET nombre = 'Excisión de Masa en Pie', descripcion = 'Resección quirúrgica de masa tumoral en el pie.' WHERE unaccent(upper(nombre)) = unaccent(upper('EXCISION DE MASA EN PIE'));
UPDATE catalogo_procedimientos SET nombre = 'Drenaje de Dedo', descripcion = 'Drenaje quirúrgico de absceso o colección en dedo.' WHERE unaccent(upper(nombre)) = unaccent(upper('DRENAJE DE DEDO'));
UPDATE catalogo_procedimientos SET nombre = 'Drenaje Ecoguiado de Quiste', descripcion = 'Drenaje de quiste guiado por ultrasonido.' WHERE unaccent(upper(nombre)) = unaccent(upper('DRENAJE ECOGUIADO QUISTE'));
UPDATE catalogo_procedimientos SET nombre = 'Colocación Fijador Externo', abreviatura = 'CFE', descripcion = 'Colocación quirúrgica de fijador externo (ya normalizado en 062).' WHERE unaccent(upper(nombre)) = unaccent(upper('COLOCACIN FIJADOR EXTERNO'));
UPDATE catalogo_procedimientos SET nombre = 'Amputación de Artejos', descripcion = 'Amputación de uno o más artejos (dedos del pie).' WHERE unaccent(upper(nombre)) = unaccent(upper('AMPUTACION DE ARTEJOS'));
UPDATE catalogo_procedimientos SET nombre = 'Resección de Grenoloma', descripcion = 'Resección quirúrgica de granuloma.' WHERE unaccent(upper(nombre)) = unaccent(upper('RESICION DE GRENOLOMA'));
UPDATE catalogo_procedimientos SET nombre = 'Drenaje de Quiste Sinovial', descripcion = 'Drenaje quirúrgico o aspiración de quiste sinovial.' WHERE unaccent(upper(nombre)) = unaccent(upper('DRENAJE DE QUISTE SINOVIAL'));
UPDATE catalogo_procedimientos SET nombre = 'Manejo Paciente Crítico', descripcion = 'Atención clínica especializada a paciente en estado crítico.' WHERE unaccent(upper(nombre)) = unaccent(upper('MANEJO PACIENTE CRTICO'));

-- ─── Diagnóstico por imagen / Estudios ───
UPDATE catalogo_procedimientos SET nombre = 'Tomografías', descripcion = 'Estudio tomográfico computarizado.' WHERE unaccent(upper(nombre)) = unaccent(upper('TOMOGRAFIAS'));
UPDATE catalogo_procedimientos SET nombre = 'Ultrasonido Endovaginal', descripcion = 'Estudio ecográfico transvaginal.' WHERE unaccent(upper(nombre)) = unaccent(upper('ULTRASONIDO ENDOVAGINAL'));
UPDATE catalogo_procedimientos SET nombre = 'Ultrasonido Obstétrico', descripcion = 'Estudio ecográfico obstétrico.' WHERE unaccent(upper(nombre)) = unaccent(upper('ULTRASONIDO OBSTETRICO'));
UPDATE catalogo_procedimientos SET nombre = 'Visco Suplementación', descripcion = 'Infiltración intraarticular de ácido hialurónico.' WHERE unaccent(upper(nombre)) = unaccent(upper('VISCO SUPLEMENTACION'));

-- ─── Misceláneos ───
UPDATE catalogo_procedimientos SET nombre = 'Exanguinotransfusión', descripcion = 'Reemplazo sanguíneo total o parcial.' WHERE unaccent(upper(nombre)) = unaccent(upper('EXANGUINOTRANFUSION'));
UPDATE catalogo_procedimientos SET nombre = 'Termocoagulación', descripcion = 'Coagulación de tejido con calor (electrocauterio).' WHERE unaccent(upper(nombre)) = unaccent(upper('TERMOCOAGULACION'));
UPDATE catalogo_procedimientos SET nombre = 'Cierre por Tercera Intención', descripcion = 'Cierre diferido de herida (por granulación).' WHERE unaccent(upper(nombre)) = unaccent(upper('CIERRE POR TERCERA INTENCION'));
UPDATE catalogo_procedimientos SET nombre = 'Punción Lumbar', descripcion = 'Extracción de líquido cefalorraquídeo para diagnóstico.' WHERE unaccent(upper(nombre)) = unaccent(upper('PUNCION LUMBAR'));
UPDATE catalogo_procedimientos SET nombre = 'Exploración Abdominal', descripcion = 'Exploración quirúrgica de la cavidad abdominal.' WHERE unaccent(upper(nombre)) = unaccent(upper('EXPLORACION ABDOMINAL'));
UPDATE catalogo_procedimientos SET nombre = 'Orquideopexia Inguinal', descripcion = 'Fijación quirúrgica del testículo en el canal inguinal.' WHERE unaccent(upper(nombre)) = unaccent(upper('ORQUIDEO PEXIA INGUINAL'));
UPDATE catalogo_procedimientos SET nombre = 'Orquideopexia Inguinal', descripcion = 'Corrección de testículo no descendido por vía inguinal.' WHERE unaccent(upper(nombre)) = unaccent(upper('ORQUIDEO PEXIA INGUINAL'));
UPDATE catalogo_procedimientos SET nombre = 'Criptorquidia', descripcion = 'Corrección quirúrgica de testículo no descendido.' WHERE unaccent(upper(nombre)) = unaccent(upper('CRIPTORQUIDIA'));
UPDATE catalogo_procedimientos SET nombre = 'Férula Anular', descripcion = 'Colocación de férula en dedo anular.' WHERE unaccent(upper(nombre)) = unaccent(upper('FERULA ANULAR'));
UPDATE catalogo_procedimientos SET nombre = 'Masa en Cuello', descripcion = 'Resección o biopsia de masa cervical.' WHERE unaccent(upper(nombre)) = unaccent(upper('MASA EN CUELLO'));
UPDATE catalogo_procedimientos SET nombre = 'Masa en Labio', descripcion = 'Resección o biopsia de masa en labio.' WHERE unaccent(upper(nombre)) = unaccent(upper('MASA EN LABIO'));
UPDATE catalogo_procedimientos SET nombre = 'Empaque Nasal', descripcion = 'Taponamiento nasal hemostático.' WHERE unaccent(upper(nombre)) = unaccent(upper('EMPAQUE NASAL'));
UPDATE catalogo_procedimientos SET nombre = 'Tubo Orotraqueal', descripcion = 'Colocación de tubo orotraqueal (similar a IOT).' WHERE unaccent(upper(nombre)) = unaccent(upper('TUBO OROTRAQUEAL'));
UPDATE catalogo_procedimientos SET nombre = 'Sonda Orográstica', abreviatura = 'SG', descripcion = 'Inserción de sonda orogástrica.' WHERE unaccent(upper(nombre)) = unaccent(upper('SONDA OROGASTRICA'));
UPDATE catalogo_procedimientos SET nombre = 'O/S Radio', descripcion = 'Osteosíntesis de Radio.' WHERE unaccent(upper(nombre)) = unaccent(upper('O/S RADIO'));
UPDATE catalogo_procedimientos SET nombre = 'O/S Cúbito', descripcion = 'Osteosíntesis de Cúbito.' WHERE unaccent(upper(nombre)) = unaccent(upper('O/S CUBITO'));
UPDATE catalogo_procedimientos SET nombre = 'Reemplazo de Rodillas', descripcion = 'Reemplazo total de rodillas (prótesis).' WHERE unaccent(upper(nombre)) = unaccent(upper('REEMPLAZO DE RODILLAS'));
UPDATE catalogo_procedimientos SET nombre = 'Cistostomía Abierta', descripcion = 'Apertura quirúrgica de la vejiga para drenaje.' WHERE unaccent(upper(nombre)) = unaccent(upper('CISTOSTOMIA ABIERTA'));
UPDATE catalogo_procedimientos SET nombre = 'Infiltración Ecoguiada', abreviatura = 'INFECO', descripcion = 'Infiltración guiada por ultrasonido.' WHERE unaccent(upper(nombre)) = unaccent(upper('INFILTRACION ECOGUIADA'));
UPDATE catalogo_procedimientos SET nombre = 'Retiro de Yeso', abreviatura = 'RY', descripcion = 'Retiro de yeso aplicado al paciente.' WHERE unaccent(upper(nombre)) = unaccent(upper('RETIRO DE YESOS'));
UPDATE catalogo_procedimientos SET nombre = 'Retiro de Vendajes', abreviatura = 'RV', descripcion = 'Retiro de vendaje aplicado al paciente.' WHERE unaccent(upper(nombre)) = unaccent(upper('RETIRO DE VENDAJES'));
UPDATE catalogo_procedimientos SET nombre = 'Lavados y Debridamientos', abreviatura = 'LD', descripcion = 'Limpieza quirúrgica y retiro de tejido desvitalizado.' WHERE unaccent(upper(nombre)) = unaccent(upper('LAVADOS Y DEBRIDAMIENTOS'));
UPDATE catalogo_procedimientos SET nombre = 'Cistoscopia Basal Oculta', descripcion = 'Estudio endoscópico de vejiga urinaria.' WHERE unaccent(upper(nombre)) = unaccent(upper('CISTOSTOMIA ABIERTA'));
UPDATE catalogo_procedimientos SET nombre = 'Granuloma', descripcion = 'Resección quirúrgica de granuloma.' WHERE unaccent(upper(nombre)) = unaccent(upper('GRANULOMA'));
UPDATE catalogo_procedimientos SET nombre = 'Espirometría', descripcion = 'Estudio de capacidad pulmonar.' WHERE unaccent(upper(nombre)) = unaccent(upper('ESPIROMETRIA'));
UPDATE catalogo_procedimientos SET nombre = 'Cardiotocografía (Non-Stress Test)', descripcion = 'Monitoreo fetal no estresante.' WHERE unaccent(upper(nombre)) = unaccent(upper('CARDIOTOCOGRAFIA (NON-STRESS TEST)'));
UPDATE catalogo_procedimientos SET nombre = 'Tomografía de Coherencia Óptica', descripcion = 'Estudio oftalmológico OCT.' WHERE unaccent(upper(nombre)) = unaccent(upper('TOMOGRAFIA DE COHERENCIA OPTICA'));
UPDATE catalogo_procedimientos SET nombre = 'Quiste de Baker (Dx)', descripcion = 'Diagnóstico/resección de quiste de Baker (rodilla).' WHERE unaccent(upper(nombre)) = unaccent(upper('QUISTE DE BAKER (DX)'));
UPDATE catalogo_procedimientos SET nombre = 'Regularización', abreviatura = 'REG', descripcion = 'Regularización quirúrgica (dedo de la mano).' WHERE unaccent(upper(nombre)) = unaccent(upper('REGULARIZACION'));
UPDATE catalogo_procedimientos SET nombre = 'Intraóseo', abreviatura = 'I', descripcion = 'Acceso intraóseo (vía ósea para medicación).' WHERE unaccent(upper(nombre)) = unaccent(upper('INTRAOSEO'));
UPDATE catalogo_procedimientos SET nombre = 'DIU', abreviatura = 'COLDIU', descripcion = 'Inserción o manipulación de dispositivo intrauterino (alias).' WHERE unaccent(upper(nombre)) = unaccent(upper('DIU'));
UPDATE catalogo_procedimientos SET nombre = 'Drenaje de Quiste Sinovial', descripcion = 'Aspiración o drenaje de quiste sinovial.' WHERE unaccent(upper(nombre)) = unaccent(upper('DRENAJE DE QUISTE SINOVIAL'));
UPDATE catalogo_procedimientos SET nombre = 'Bacteriemia por Acidosis Tubular Renal', descripcion = 'Diagnóstico/tratamiento de ATR. (Revisar: es diagnóstico, no procedimiento).' WHERE unaccent(upper(nombre)) = unaccent(upper('ACIDOSIS TUBULAR RENAL'));

COMMIT;

-- ============================================================
-- >>> FIN: 063_procedimientos_normalizacion_masiva.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 064_procedimientos_amputacion_unificada.sql
-- ============================================================

-- ============================================================
-- 064_procedimientos_amputacion_unificada.sql
-- Fusiona TODAS las variantes de amputación en un único
-- procedimiento canónico: "Amputación" (AMP, id 36).
--
-- Se absorben:
--   id 146 ADD  "Amputación de Dedo"           → 2 refs
--   id 120 ARD  "Amputación en Raqueta de Dedo" → 1 ref
--   id 138 ADM  "Amputación de Muñeca"          → 2 refs
--   id 147 ASC  "Amputación Supracondílea"      → 1 ref
--   id 162 AICA "Amputación Infracondílea"      → 1 ref
--
-- Total: 7 referencias migradas al id 36 (AMP).
-- ============================================================

BEGIN;

UPDATE catalogo_procedimientos
SET descripcion = 'Amputación de extremidad o segmento (dedo, mano, muñeca, supracondílea, infracondílea, raqueta).'
WHERE UPPER(abreviatura) = 'AMP';

DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE UPPER(abreviatura) = 'AMP';
    IF ganador IS NULL THEN
        RAISE NOTICE 'AMP no encontrado (skip unificación de amputaciones)';
        RETURN;
    END IF;
    FOR perdedor IN SELECT id FROM catalogo_procedimientos
                    WHERE UPPER(abreviatura) IN ('ADD','ARD','ADM','ASC','AICA')
                      AND id <> ganador
    LOOP
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'Amputación: % absorbido por AMP (% refs)', perdedor, cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

COMMIT;

-- ============================================================
-- >>> FIN: 064_procedimientos_amputacion_unificada.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 065_procedimientos_artroplastia_artrodesis.sql
-- ============================================================

-- ============================================================
-- 065_procedimientos_artroplastia_artrodesis.sql
-- 1. ARTP (id 33) "Artroplastia" → absorbido por ADR (id 170)
--    "Artroplastia de Rodilla" (renombrado a genérico para
--    cubrir cadera, hombro, rodilla).
-- 2. ARTD (id 34) "Artrodesis" → absorbido por AR (id 175)
--    "Artrodesis de Rodilla" (renombrado a genérico).
-- 3. CAM (id 87) "Cambio de Artrotomía" → renombrado y abreviado
--    a CART (Artrotomía / Revisión articular). Mantener anestesia=1.
-- 4. Corrección CRÍTICA de seguridad: anestesia de ADR y AR = 1.
-- ============================================================

BEGIN;

-- 1. ARTP absorbe ARTD... espera, son conceptos distintos:
--    ARTP = Artroplastia (genérico)
--    ADR  = Artroplastia de Rodilla (específico)
--    Decisión: fusionar ARTP → ADR (rodilla absorbe el genérico).
--    Renombrar ADR a "Artroplastia de Rodilla" (manteniendo id).

DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE UPPER(abreviatura) = 'ADR';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE UPPER(abreviatura) = 'ARTP';
    IF ganador IS NULL OR perdedor IS NULL THEN
        RAISE NOTICE 'ADR/ARTP no encontrado (skip fusión ARTP→ADR)';
        RETURN;
    END IF;
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'ARTP absorbido por ADR (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

UPDATE catalogo_procedimientos
SET nombre = 'Artroplastia de Rodilla',
    abreviatura = 'ADR',
    descripcion = 'Reemplazo articular total o parcial de rodilla (prótesis).',
    anestesia = 1
WHERE UPPER(abreviatura) = 'ADR';

-- 2. ARTD absorbido por AR
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE UPPER(abreviatura) = 'AR';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE UPPER(abreviatura) = 'ARTD';
    IF ganador IS NULL OR perdedor IS NULL THEN
        RAISE NOTICE 'AR/ARTD no encontrado (skip fusión ARTD→AR)';
        RETURN;
    END IF;
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'ARTD absorbido por AR (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

UPDATE catalogo_procedimientos
SET nombre = 'Artrodesis de Rodilla',
    abreviatura = 'AR',
    descripcion = 'Fusión quirúrgica de la articulación de la rodilla.',
    anestesia = 1
WHERE UPPER(abreviatura) = 'AR';

-- 3. Renombrar CAM → CART (Artrotomía / Revisión articular)
UPDATE catalogo_procedimientos
SET nombre = 'Artrotomía / Revisión Articular',
    abreviatura = 'CART',
    descripcion = 'Apertura quirúrgica de la articulación para lavado, revisión o cambio de apósitos.',
    anestesia = 1
WHERE UPPER(abreviatura) = 'CAM';

COMMIT;

-- ============================================================
-- >>> FIN: 065_procedimientos_artroplastia_artrodesis.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 066_procedimientos_normalizar_capitalizacion.sql
-- ============================================================

-- ============================================================
-- 066_procedimientos_normalizar_capitalizacion.sql
-- Normaliza todos los nombres del catálogo a formato Título
-- con respeto de preposiciones (de, del, la, el, y, o, en, por, para, con, sin).
--
-- Criterios:
--   * Primera letra de cada palabra en MAYÚSCULAS
--   * Excepción: preposiciones en minúsculas (de, del, la, el, los, las, y, o, en, por, para, con, sin, a, al, un, una)
--   * Mantener siglas comunes en MAYÚSCULAS (DIU, HIV, TAC, RMN, ECG, EMG, FAST, AMEU, BJ, etc.)
--   * Conservar tildes correctas
-- ============================================================

BEGIN;

-- Función auxiliar que aplica Title Case inteligente
CREATE OR REPLACE FUNCTION titulo_inteligente(text) RETURNS text AS $$
DECLARE
    palabra text;
    palabras text[] := string_to_array($1, ' ');
    resultado text := '';
    i int;
    excepciones text[] := ARRAY['de','del','la','el','los','las','y','o','en','por','para','con','sin','a','al','un','una','unos','unas','lo','le','les'];
    siglas text[] := ARRAY['DIU','HIV','TAC','RMN','ECG','EMG','FAST','AMEU','BJ','HTA','DM','EPOC','IRC','ICC','SIDA','TBC','PCR'];
BEGIN
    IF $1 IS NULL OR btrim($1) = '' THEN
        RETURN $1;
    END IF;
    FOR i IN 1..array_length(palabras,1) LOOP
        palabra := palabras[i];
        -- Si la palabra es exactamente una sigla conocida, mantener MAYÚSCULAS
        IF upper(palabra) = ANY(siglas) THEN
            palabras[i] := upper(palabra);
        ELSIF lower(palabra) = ANY(excepciones) AND i > 1 THEN
            palabras[i] := lower(palabra);
        ELSE
            -- Title case preservando la longitud
            palabras[i] := upper(substring(palabra,1,1)) || lower(substring(palabra,2));
        END IF;
    END LOOP;
    resultado := array_to_string(palabras, ' ');
    -- Correcciones específicas de tildes perdidas
    resultado := replace(resultado, 'Repertorio', 'Repertorio');  -- placeholder
    RETURN resultado;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Actualizar nombres aplicando Title Case inteligente
UPDATE catalogo_procedimientos
SET nombre = titulo_inteligente(nombre)
WHERE activo = TRUE
  AND nombre <> titulo_inteligente(nombre);

COMMIT;

-- ============================================================
-- >>> FIN: 066_procedimientos_normalizar_capitalizacion.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 067_procedimientos_ajustes_finales.sql
-- ============================================================

-- ============================================================
-- 067_procedimientos_ajustes_finales.sql
-- Ajustes finales de capitalización para casos especiales.
-- VAC es marca comercial — debe ir en MAYÚSCULAS.
-- ============================================================

BEGIN;

UPDATE catalogo_procedimientos
SET nombre = 'VAC'
WHERE UPPER(abreviatura) = 'VAC';

COMMIT;

-- ============================================================
-- >>> FIN: 067_procedimientos_ajustes_finales.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 068_procedimientos_descripciones_faltantes.sql
-- ============================================================

-- ============================================================
-- 068_procedimientos_descripciones_faltantes.sql
-- Asigna descripciones clínicas a los 89 procedimientos que aún
-- tienen 'Procedimiento no catalogado' o descripción vacía.
--
-- Estrategia:
--   - Descripción concisa, max 120 caracteres
--   - Basada en el nombre canónico del procedimiento
--   - No se modifican los demás campos
-- ============================================================

BEGIN;

-- Categoría: Ginecología / Obstetricia
UPDATE catalogo_procedimientos SET descripcion = 'Reducción quirúrgica de prolapso rectal.' WHERE unaccent(upper(nombre)) = 'PROLAPSO RECTAL' AND (descripcion IS NULL OR descripcion = '' OR descripcion = 'Procedimiento no catalogado');
UPDATE catalogo_procedimientos SET descripcion = 'Sutura del desgarro perineal/vaginal postparto.' WHERE unaccent(upper(nombre)) = 'REPARACION DE DESGARRO VAGINAL';
UPDATE catalogo_procedimientos SET descripcion = 'Sutura del desgarro del cuello uterino postparto.' WHERE unaccent(upper(nombre)) = 'REPARACION DE DESGARRO CERVICAL';
UPDATE catalogo_procedimientos SET descripcion = 'Legrado uterino evacuador o diagnóstico con cureta.' WHERE unaccent(upper(nombre)) = 'LEGRADO INSTRUMENTAL UTERINO';
UPDATE catalogo_procedimientos SET descripcion = 'Resección de fimbrias tubáricas.' WHERE unaccent(upper(nombre)) = 'FIMBRIECTOMIA';
UPDATE catalogo_procedimientos SET descripcion = 'Extirpación quirúrgica del útero por vía abdominal.' WHERE unaccent(upper(nombre)) = 'HISTERECTOMIA ABDOMINAL TOTAL';
UPDATE catalogo_procedimientos SET descripcion = 'Extirpación del útero por vía vaginal.' WHERE unaccent(upper(nombre)) = 'HISTERECTOMIA VAGINAL';
UPDATE catalogo_procedimientos SET descripcion = 'Ligadura hemostática de arterias uterinas en hemorragia.' WHERE unaccent(upper(nombre)) = 'LIGADURA DE ARTERIA UTERINA';
UPDATE catalogo_procedimientos SET descripcion = 'Histerectomía de emergencia postparto.' WHERE unaccent(upper(nombre)) = 'HISTERECTOMIA OBSTETRICA';
UPDATE catalogo_procedimientos SET descripcion = 'Remoción manual de placenta retenida postparto.' WHERE unaccent(upper(nombre)) = 'EXTRACCION MANUAL DE PLACENTA';
UPDATE catalogo_procedimientos SET descripcion = 'Reparación de pared vaginal anterior (cistocele).' WHERE unaccent(upper(nombre)) = 'COLPORRAFIA ANTERIOR';
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica o manual de la pelvis.' WHERE unaccent(upper(nombre)) = 'EXPLORACION PELVICA';
UPDATE catalogo_procedimientos SET descripcion = 'Drenaje o evacuación de lipoma.' WHERE unaccent(upper(nombre)) = 'DRENAJE DE LIPOMA';

-- Categoría: Traumatología / Ortopedia
UPDATE catalogo_procedimientos SET descripcion = 'Cambio de apósitos o revisión de artrotomía previa.' WHERE unaccent(upper(nombre)) = 'ARTROTOMIA / REVISION ARTICULAR';
UPDATE catalogo_procedimientos SET descripcion = 'Cambio de apósitos y drenaje de herida con membrana.' WHERE unaccent(upper(nombre)) = 'CAMBIO DE MEMBRANAS';
UPDATE catalogo_procedimientos SET descripcion = 'Drenaje a través de membrana cerrada o abierta.' WHERE unaccent(upper(nombre)) = 'DRENAJE DE MEMBRANAS';
UPDATE catalogo_procedimientos SET descripcion = 'Amputación de fémur distal, por encima de los cóndilos.' WHERE unaccent(upper(nombre)) = 'AMPUTACION SUPRACONDILEA';  -- ya absorbida por AMP (064), no-op
UPDATE catalogo_procedimientos SET descripcion = 'Amputación de tibia, por debajo de los cóndilos femorales.' WHERE unaccent(upper(nombre)) = 'AMPUTACION INFRACONDILEA';  -- ya absorbida por AMP (064), no-op
UPDATE catalogo_procedimientos SET descripcion = 'Amputación quirúrgica de dedo con colgajo en raqueta.' WHERE unaccent(upper(nombre)) = 'AMPUTACION EN RAQUETA DE DEDO';  -- ya absorbida por AMP (064), no-op
UPDATE catalogo_procedimientos SET descripcion = 'Reconstrucción quirúrgica de un dedo.' WHERE unaccent(upper(nombre)) = 'RECONSTRUCCION DE DEDO';
UPDATE catalogo_procedimientos SET descripcion = 'Reducción cerrada de fractura o luxación de antebrazo.' WHERE unaccent(upper(nombre)) = 'MANIPULACION DE ANTEBRAZO';
UPDATE catalogo_procedimientos SET descripcion = 'Reemplazo articular de rodilla (prótesis).' WHERE unaccent(upper(nombre)) = 'ARTROPLASTIA DE RODILLA';
UPDATE catalogo_procedimientos SET descripcion = 'Fusión quirúrgica de la articulación de la rodilla.' WHERE unaccent(upper(nombre)) = 'ARTRODESIS DE RODILLA';
UPDATE catalogo_procedimientos SET descripcion = 'Reemplazo parcial de la cadera.' WHERE unaccent(upper(nombre)) = 'HEMIARTROPLASTIA DE CADERA';
UPDATE catalogo_procedimientos SET descripcion = 'Fusión quirúrgica de la articulación del tobillo.' WHERE unaccent(upper(nombre)) = 'ANTRODESIS DE TOBILLO';
UPDATE catalogo_procedimientos SET descripcion = 'Corte óseo quirúrgico para corrección de deformidad.' WHERE unaccent(upper(nombre)) = 'OSTEOTOMIA';
UPDATE catalogo_procedimientos SET descripcion = 'Reducción quirúrgica de fractura radio-cubital.' WHERE unaccent(upper(nombre)) = 'FRACTURA RADIO Y CUBITO';
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de masa cervical.' WHERE unaccent(upper(nombre)) = 'RESECCION DE MASA EN CUELLO';
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de fibroma.' WHERE unaccent(upper(nombre)) = 'RESECCION DE FIBROMA';
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de pólipo.' WHERE unaccent(upper(nombre)) = 'RESECCION DE POLIPO';
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de condiloma.' WHERE unaccent(upper(nombre)) = 'RESECCION CONDILOMA';
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de quiste.' WHERE unaccent(upper(nombre)) = 'RESECCION QUISTE';
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de lesión hiperplásica.' WHERE unaccent(upper(nombre)) = 'RESECCION DE LESION HIPERPLASICA';
UPDATE catalogo_procedimientos SET descripcion = 'Regulación quirúrgica del pulpejo (dedo).' WHERE unaccent(upper(nombre)) = 'REGULACION DE PULPEJO';
UPDATE catalogo_procedimientos SET descripcion = 'Liberación quirúrgica de adherencias/sinequias.' WHERE unaccent(upper(nombre)) = 'LIBERACION DE SINEQUIAS';
UPDATE catalogo_procedimientos SET descripcion = 'Retiro de tornillo/fijación transindesmal en tobillo.' WHERE unaccent(upper(nombre)) = 'RETIRO TRANSINDESMAL';
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica del antebrazo/muñeca.' WHERE unaccent(upper(nombre)) = 'EXPLORACION RADIAL';
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica del cuello.' WHERE unaccent(upper(nombre)) = 'EXPLORACION DE CUELLO';
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica de vasos sanguíneos.' WHERE unaccent(upper(nombre)) = 'EXPLORACION VASCULAR';
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica de vasos femorales.' WHERE unaccent(upper(nombre)) = 'EXPLORACION VASOS FEMORALES';
UPDATE catalogo_procedimientos SET descripcion = 'Resección de tejido desvitalizado (esfacelo) en tórax.' WHERE unaccent(upper(nombre)) = 'ESCARECTOMIA EN TORAX';
UPDATE catalogo_procedimientos SET descripcion = 'Resección de tejido desvitalizado en miembros inferiores.' WHERE unaccent(upper(nombre)) = 'ESCARECTOMIA MIEMBROS INFERIORES';
UPDATE catalogo_procedimientos SET descripcion = 'Incisiones de descarga para quemaduras circulares.' WHERE unaccent(upper(nombre)) = 'ESCAROTOMIAS POR QUEMADURAS';
UPDATE catalogo_procedimientos SET descripcion = 'Rotación quirúrgica de colgajo cutáneo.' WHERE unaccent(upper(nombre)) = 'ROTACION COLGAJO';
UPDATE catalogo_procedimientos SET descripcion = 'Reducción o manipulación cerrada de muñeca.' WHERE unaccent(upper(nombre)) = 'MANIPULACION DE MUNECA';
UPDATE catalogo_procedimientos SET descripcion = 'Limpieza y cierre de herida cortocortante traumática.' WHERE unaccent(upper(nombre)) = 'LAVADO Y SUTURA DE HERIDA CORTOCORTANTE TRAUMATICA';
UPDATE catalogo_procedimientos SET descripcion = 'Reducción cerrada de luxación o fractura de hombro.' WHERE unaccent(upper(nombre)) = 'MANIPULACION CERRADA DE HOMBRO';
UPDATE catalogo_procedimientos SET descripcion = 'Reducción cerrada de luxación o fractura de cadera.' WHERE unaccent(upper(nombre)) = 'MANIPULACION CERRADA DE CADERA';
UPDATE catalogo_procedimientos SET descripcion = 'Reducción cerrada de fractura/luxación (general).' WHERE unaccent(upper(nombre)) = 'MANIPULACION CERRADA (GENERAL)';
UPDATE catalogo_procedimientos SET descripcion = 'Extracción quirúrgica de uña del dedo de la mano.' WHERE unaccent(upper(nombre)) = 'ONICECTOMIA DEDO MANO';
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de masa tumoral en el pie.' WHERE unaccent(upper(nombre)) = 'EXCISION DE MASA EN PIE';
UPDATE catalogo_procedimientos SET descripcion = 'Drenaje quirúrgico de absceso o colección en dedo.' WHERE unaccent(upper(nombre)) = 'DRENAJE DE DEDO';
UPDATE catalogo_procedimientos SET descripcion = 'Drenaje de quiste guiado por ultrasonido.' WHERE unaccent(upper(nombre)) = 'DRENAJE ECOGUIADO DE QUISTE';
UPDATE catalogo_procedimientos SET descripcion = 'Colocación quirúrgica de fijador externo (pines y barras).' WHERE unaccent(upper(nombre)) = 'COLOCACION FIJADOR EXTERNO';
UPDATE catalogo_procedimientos SET descripcion = 'Amputación de uno o más artejos (dedos del pie).' WHERE unaccent(upper(nombre)) = 'AMPUTACION DE ARTEJOS';  -- no existe en catálogo local, no-op
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de granuloma.' WHERE unaccent(upper(nombre)) = 'RESECCION DE GRENOLOMA';
UPDATE catalogo_procedimientos SET descripcion = 'Drenaje quirúrgico o aspiración de quiste sinovial.' WHERE unaccent(upper(nombre)) = 'DRENAJE DE QUISTE SINOVIAL';
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de condiloma.' WHERE unaccent(upper(nombre)) = 'RESECCION CONDILOMA';
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de condiloma acuminado.' WHERE unaccent(upper(nombre)) = 'RESECCION CONDILOMA';

-- Categoría: Estudios / Diagnóstico
UPDATE catalogo_procedimientos SET descripcion = 'Estudio tomográfico computarizado.' WHERE unaccent(upper(nombre)) = 'TOMOGRAFIAS';
UPDATE catalogo_procedimientos SET descripcion = 'Estudio ecográfico transvaginal.' WHERE unaccent(upper(nombre)) = 'ULTRASONIDO ENDOVAGINAL';
UPDATE catalogo_procedimientos SET descripcion = 'Estudio ecográfico obstétrico.' WHERE unaccent(upper(nombre)) = 'ULTRASONIDO OBSTETRICO';
UPDATE catalogo_procedimientos SET descripcion = 'Infiltración intraarticular de ácido hialurónico.' WHERE unaccent(upper(nombre)) = 'VISCO SUPLEMENTACION';
UPDATE catalogo_procedimientos SET descripcion = 'Taponamiento nasal hemostático.' WHERE unaccent(upper(nombre)) = 'EMPAQUE NASAL';
UPDATE catalogo_procedimientos SET descripcion = 'Colocación de tubo orotraqueal.' WHERE unaccent(upper(nombre)) = 'TUBO OROTRAQUEAL';
UPDATE catalogo_procedimientos SET descripcion = 'Inserción de sonda orogástrica.' WHERE unaccent(upper(nombre)) = 'SONDA OROGASTRICA';
UPDATE catalogo_procedimientos SET descripcion = 'Estudio endoscópico de vejiga urinaria.' WHERE unaccent(upper(nombre)) = 'CISTOSCOPIA BASAL OCULTA';
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de granuloma.' WHERE unaccent(upper(nombre)) = 'GRANULOMA';
UPDATE catalogo_procedimientos SET descripcion = 'Estudio de capacidad pulmonar.' WHERE unaccent(upper(nombre)) = 'ESPIROMETRIA';
UPDATE catalogo_procedimientos SET descripcion = 'Estudio gammagráfico.' WHERE unaccent(upper(nombre)) = 'CENTELLOGRAMA';
UPDATE catalogo_procedimientos SET descripcion = 'Reducción de prolapso rectal.' WHERE unaccent(upper(nombre)) = 'PROLAPSO RECTAL';
UPDATE catalogo_procedimientos SET descripcion = 'Corrección quirúrgica de testículo no descendido.' WHERE unaccent(upper(nombre)) = 'CRIPTORQUIDIA';
UPDATE catalogo_procedimientos SET descripcion = 'Colocación de férula en dedo anular.' WHERE unaccent(upper(nombre)) = 'FERULA ANULAR';
UPDATE catalogo_procedimientos SET descripcion = 'Resección o biopsia de masa cervical.' WHERE unaccent(upper(nombre)) = 'MASA EN CUELLO';
UPDATE catalogo_procedimientos SET descripcion = 'Resección o biopsia de masa en labio.' WHERE unaccent(upper(nombre)) = 'MASA EN LABIO';
UPDATE catalogo_procedimientos SET descripcion = 'Osteosíntesis de radio.' WHERE unaccent(upper(nombre)) = 'O/S RADIO';
UPDATE catalogo_procedimientos SET descripcion = 'Osteosíntesis de cúbito.' WHERE unaccent(upper(nombre)) = 'O/S CUBITO';
UPDATE catalogo_procedimientos SET descripcion = 'Reemplazo total de rodillas (prótesis).' WHERE unaccent(upper(nombre)) = 'REEMPLAZO DE RODILLAS';
UPDATE catalogo_procedimientos SET descripcion = 'Apertura quirúrgica de la vejiga para drenaje.' WHERE unaccent(upper(nombre)) = 'CISTOSCOPIA BASAL OCULTA';
UPDATE catalogo_procedimientos SET descripcion = 'Infiltración guiada por ultrasonido.' WHERE unaccent(upper(nombre)) = 'INFILTRACION ECOGUIADA';
UPDATE catalogo_procedimientos SET descripcion = 'Estudio de capacidad pulmonar.' WHERE unaccent(upper(nombre)) = 'ESPIROMETRIA';
UPDATE catalogo_procedimientos SET descripcion = 'Reducción cerrada de fractura/luxación (general).' WHERE unaccent(upper(nombre)) = 'MANIPULACION CERRADA (GENERAL)';

-- Categoría: Misceláneos / Generales
UPDATE catalogo_procedimientos SET descripcion = 'Atención clínica especializada a paciente en estado crítico.' WHERE unaccent(upper(nombre)) = 'MANEJO PACIENTE CRITICO';
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de quiste sebáceo.' WHERE unaccent(upper(nombre)) = 'QUISTE SEBACEO';
UPDATE catalogo_procedimientos SET descripcion = 'Monitoreo fetal no estresante.' WHERE unaccent(upper(nombre)) = 'CARDIOTOCOGRAFIA (NON-STRESS TEST)';
UPDATE catalogo_procedimientos SET descripcion = 'Estudio oftalmológico OCT.' WHERE unaccent(upper(nombre)) = 'TOMOGRAFIA DE COHERENCIA OPTICA';
UPDATE catalogo_procedimientos SET descripcion = 'Diagnóstico/resección de quiste de Baker (rodilla).' WHERE unaccent(upper(nombre)) = 'QUISTE DE BAKER (DX)';
UPDATE catalogo_procedimientos SET descripcion = 'Regularización quirúrgica (dedo de la mano).' WHERE unaccent(upper(nombre)) = 'REGULARIZACION';
UPDATE catalogo_procedimientos SET descripcion = 'Acceso intraóseo (vía ósea para medicación).' WHERE unaccent(upper(nombre)) = 'INTRAOSEO';
UPDATE catalogo_procedimientos SET descripcion = 'Inserción o manipulación de dispositivo intrauterino (alias).' WHERE unaccent(upper(nombre)) = 'DIU';
UPDATE catalogo_procedimientos SET descripcion = 'Exanguinotransfusión: reemplazo sanguíneo total o parcial.' WHERE unaccent(upper(nombre)) = 'EXANGUINOTRANSFUSION';
UPDATE catalogo_procedimientos SET descripcion = 'Coagulación de tejido con calor (electrocauterio).' WHERE unaccent(upper(nombre)) = 'TERMOCOAGULACION';
UPDATE catalogo_procedimientos SET descripcion = 'Cierre diferido de herida (por granulación).' WHERE unaccent(upper(nombre)) = 'CIERRE POR TERCERA INTENCION';
UPDATE catalogo_procedimientos SET descripcion = 'Extracción de líquido cefalorraquídeo para diagnóstico.' WHERE unaccent(upper(nombre)) = 'PUNCION LUMBAR';
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica de la cavidad abdominal.' WHERE unaccent(upper(nombre)) = 'EXPLORACION ABDOMINAL';
UPDATE catalogo_procedimientos SET descripcion = 'Fijación quirúrgica del testículo en el canal inguinal.' WHERE unaccent(upper(nombre)) = 'ORQUIDEPEXIA INGUINAL';
UPDATE catalogo_procedimientos SET descripcion = 'Inserción o retiro de implante subdérmico anticonceptivo (Jadelle).' WHERE unaccent(upper(nombre)) = 'IMPLANTE JADELLE';
UPDATE catalogo_procedimientos SET descripcion = 'Inserción de implante subdérmico anticonceptivo (Jadelle).' WHERE unaccent(upper(nombre)) = 'COLOCACION DE JADELLE';
UPDATE catalogo_procedimientos SET descripcion = 'Retiro de implante subdérmico anticonceptivo (Jadelle).' WHERE unaccent(upper(nombre)) = 'RETIRO DE JADELLE';
UPDATE catalogo_procedimientos SET descripcion = 'Reemplazo de uno o más artejos (dedos del pie).' WHERE unaccent(upper(nombre)) = 'REEMPLAZO DE ARTEJOS';  -- no existe en catálogo local, no-op
UPDATE catalogo_procedimientos SET descripcion = 'Resección de tumor de mama con biopsia.' WHERE unaccent(upper(nombre)) = 'RESECCION DE TUMOR DE MAMA CON BIOPSIA';  -- no existe en catálogo local, no-op
UPDATE catalogo_procedimientos SET descripcion = 'Biopsia de mama con escisión de tumor.' WHERE unaccent(upper(nombre)) = 'BIOPSIA DE MAMA CON ESCISION DE TUMOR';  -- no existe en catálogo local, no-op
UPDATE catalogo_procedimientos SET descripcion = 'Biopsia de vulva.' WHERE unaccent(upper(nombre)) = 'BIOPSIA DE VULVA';  -- no existe en catálogo local, no-op
UPDATE catalogo_procedimientos SET descripcion = 'Manipulación cerrada de hombro.' WHERE unaccent(upper(nombre)) = 'MANIPULACION CERRADA DE HOMBRO';
UPDATE catalogo_procedimientos SET descripcion = 'Manipulación cerrada de cadera.' WHERE unaccent(upper(nombre)) = 'MANIPULACION CERRADA DE CADERA';
UPDATE catalogo_procedimientos SET descripcion = 'Manipulación cerrada general.' WHERE unaccent(upper(nombre)) = 'MANIPULACION CERRADA (GENERAL)';
UPDATE catalogo_procedimientos SET descripcion = 'Amputación de muñeca.' WHERE unaccent(upper(nombre)) = 'AMPUTACION DE MUNECA';  -- ya absorbida por AMP (064), no-op
UPDATE catalogo_procedimientos SET descripcion = 'Tomografía de coherencia óptica.' WHERE unaccent(upper(nombre)) = 'TOMOGRAFIA DE COHERENCIA OPTICA';
UPDATE catalogo_procedimientos SET descripcion = 'Exanguinotransfusión.' WHERE unaccent(upper(nombre)) = 'EXANGUINOTRANSFUSION';

-- Final: cualquier procedimiento aún sin descripción (catch-all)
UPDATE catalogo_procedimientos
SET descripcion = INITCAP(LOWER(nombre)) || ' — procedimiento quirúrgico o clínico.'
WHERE activo = TRUE
  AND (descripcion IS NULL OR descripcion = '' OR descripcion = 'Procedimiento no catalogado');

COMMIT;

-- ============================================================
-- >>> FIN: 068_procedimientos_descripciones_faltantes.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 069_procedimientos_fusiones_lote7.sql
-- ============================================================

-- ============================================================
-- 069_procedimientos_fusiones_lote7.sql
-- Fusiona:
--   1. Suturas B-Lynch: BLYN (id 53), COLB-LY (id 105)
--      → unificado en BLYN con descripción clínica.
--   2. Vías Centrales: CVC absorbe a CCCS (id 88).
--      → unificado en CVC como código maestro universal.
--
-- [ADAPTADO] El Grupo 2 se reordenó (igual que la corrección 071)
-- para que la corrida no aborte: en producción el rename de CVC
-- (id 3) a 'Colocación de Catéter Venoso Central' chocaba con el
-- UNIQUE(nombre) de CCCS (id 88), que ya tenía ese nombre desde 066.
--
-- Mantener separados:
--   - CCUV / CCUA (catéteres umbilicales neonatales)
--   - BAKRI (balón hemostático uterino)
--   - OTB (oclusión tubárica)
--   - OTMIA (osteotomía)
--   - CBDB (barra Denis Browne)
--   - CEM (desglose de endoscopia — pendiente de decisión)
-- ============================================================

BEGIN;

-- ──────────── Grupo 1: B-Lynch ────────────
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE UPPER(abreviatura) = 'BLYN';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE UPPER(abreviatura) = 'COLB-LY';
    IF ganador IS NULL OR perdedor IS NULL THEN
        RAISE NOTICE 'BLYN/COLB-LY no encontrado (skip fusión B-Lynch)';
        RETURN;
    END IF;
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'COLB-LY absorbido por BLYN (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

UPDATE catalogo_procedimientos
SET nombre = 'Sutura Compresiva de B-Lynch',
    abreviatura = 'BLYN',
    descripcion = 'Técnica de sutura quirúrgica mayor que abraza mecánicamente el útero con hilos pesados para detener hemorragia masiva postparto (atonía uterina). Salva la vida de la madre evitando histerectomía de urgencia.'
WHERE UPPER(abreviatura) = 'BLYN';

-- ──────────── Grupo 2: Vías Centrales ────────────
-- Paso 1: Renombrar CCCS temporalmente para liberar el nombre único
UPDATE catalogo_procedimientos
SET nombre = 'Catéter Subclavio (Legacy)'
WHERE UPPER(abreviatura) = 'CCCS';

-- Paso 2: Renombrar CVC al nombre canónico universal
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Catéter Venoso Central',
    abreviatura = 'CVC',
    descripcion = 'Introducción de catéter largo en vena de gran calibre (subclavia, yugular, femoral) para medicamentos, nutrición parenteral o monitoreo hemodinámico en pacientes graves.'
WHERE UPPER(abreviatura) = 'CVC';

-- Paso 3: CVC absorbe a CCCS
DO $$
DECLARE
    ganador int;
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO ganador FROM catalogo_procedimientos WHERE UPPER(abreviatura) = 'CVC';
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE UPPER(abreviatura) = 'CCCS';
    IF ganador IS NULL OR perdedor IS NULL THEN
        RAISE NOTICE 'CVC/CCCS no encontrado (skip fusión CVC←CCCS)';
        RETURN;
    END IF;
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'CCCS absorbido por CVC (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

COMMIT;

-- ============================================================
-- >>> FIN: 069_procedimientos_fusiones_lote7.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 070_procedimientos_dictamen_clinico.sql
-- ============================================================

-- ============================================================
-- 070_procedimientos_dictamen_clinico.sql
-- Aplica el dictamen clínico del equipo médico:
--
--   1. MPC (id 86) — renombrar a 'Manejo de Paciente Crítico (Estancia UCI)'
--      para diferenciarlo como servicio/estancia, NO como
--      procedimiento quirúrgico aislado. Mantener activo (722 usos).
--   2. ART (id 104) — Mantener independiente (Artrosentesis).
--   3. BK (id 157) — Renombrar a 'Resección de Quiste Poplíteo (Baker)'
--      porque "Quiste de Baker" es diagnóstico, no procedimiento.
--   4. GRE (id 227) — Renombrar a 'Resección Quirúrgica de Granuloma'
--      porque "Granuloma" es lesión, no la operación.
--   5. ATR (id 139) — ELIMINAR. No es procedimiento, es diagnóstico.
-- ============================================================

BEGIN;

-- 1. MPC renombrado (mantener activo pero como servicio/estancia)
UPDATE catalogo_procedimientos
SET nombre = 'Manejo de Paciente Crítico (Estancia UCI)',
    descripcion = 'Atención clínica integral en Unidad de Cuidados Intensivos (UCI) o Shock. Servicio de estancia/hora, no procedimiento quirúrgico aislado.'
WHERE UPPER(abreviatura) = 'MPC';

-- 2. ART: Artrosentesis — descripción más completa
UPDATE catalogo_procedimientos
SET descripcion = 'Punción y aspiración de líquido articular (rodilla, hombro, etc.) con fines diagnósticos o terapéuticos. Procedimiento menor ambulatorio o de urgencias.'
WHERE UPPER(abreviatura) = 'ART';

-- 3. BK renombrado (Baker como diagnóstico → acción quirúrgica)
UPDATE catalogo_procedimientos
SET nombre = 'Resección de Quiste Poplíteo (Baker)',
    abreviatura = 'BK',
    descripcion = 'Exéresis o resección quirúrgica del quiste poplíteo (de Baker) detrás de la rodilla.'
WHERE UPPER(abreviatura) = 'BK';

-- 4. GRE renombrado (Granuloma como lesión → acción quirúrgica)
UPDATE catalogo_procedimientos
SET nombre = 'Resección Quirúrgica de Granuloma',
    abreviatura = 'GRE',
    descripcion = 'Exéresis, resección o cauterización quirúrgica de granuloma.'
WHERE UPPER(abreviatura) = 'GRE';

-- 5. ATR eliminado (Acidosis Tubular Renal es diagnóstico, no procedimiento)
DO $$
DECLARE
    perdedor int;
    cnt INT;
BEGIN
    SELECT id INTO perdedor FROM catalogo_procedimientos WHERE UPPER(abreviatura) = 'ATR';
    IF perdedor IS NULL THEN
        RAISE NOTICE 'ATR no encontrado (skip eliminación)';
        RETURN;
    END IF;
    UPDATE proce_medicos SET id_catalogo_procedimiento = NULL
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'ATR (% refs) desvinculado. Procedimiento eliminado por ser diagnóstico, no acción quirúrgica.', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

COMMIT;

-- ============================================================
-- >>> FIN: 070_procedimientos_dictamen_clinico.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 071_procedimientos_corregir_cvc_ccc.sql
-- ============================================================

-- ============================================================
-- 071_procedimientos_corregir_cvc_ccc.sql
-- Corrige la migración 069 que falló por conflicto de nombre único.
--
-- El objetivo era:
--   - Renombrar CVC (id 3) → "Colocación de Catéter Venoso Central"
--   - Fusionar CCCS (id 88) en CVC
--
-- Pero ambos quedaron sin aplicar el renombramiento.
-- Esta migración corrige el orden:
--   1. Renombra CCCS (id 88) → "Catéter Subclavio" (temporal)
--   2. Renombra CVC (id 3) → "Colocación de Catéter Venoso Central"
--   3. Fusiona CCCS → CVC
--
-- [ADAPTADO] En este script consolidado, 069 ya aplica este mismo
-- orden, así que 071 queda como no-op inocuo (CCCS ya no existe:
-- todos sus UPDATE/DELETE afectan 0 filas y no generan error).
-- ============================================================

BEGIN;

-- Paso 1: Renombrar CCCS temporalmente
UPDATE catalogo_procedimientos
SET nombre = 'Catéter Subclavio (Legacy)'
WHERE id = 88;

-- Paso 2: Renombrar CVC al nombre canónico
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Catéter Venoso Central',
    abreviatura = 'CVC',
    descripcion = 'Introducción de catéter largo en vena de gran calibre (subclavia, yugular, femoral) para medicamentos, nutrición parenteral o monitoreo hemodinámico.'
WHERE id = 3;

-- Paso 3: Absorber CCCS en CVC
DO $$
DECLARE
    ganador CONSTANT INT := 3;
    perdedor CONSTANT INT := 88;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'CCCS absorbido por CVC (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

COMMIT;

-- ============================================================
-- >>> FIN: 071_procedimientos_corregir_cvc_ccc.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 072_procedimientos_grupo_edad_detalle.sql
-- ============================================================

-- ============================================================
-- 072_procedimientos_grupo_edad_detalle.sql
-- Reemplaza la edad exacta (edad + unidad_edad) y el grupo único
-- (grupo_edad) por un desglose estructurado por grupo de edad y sexo.
--
-- Columna nueva:  grupo_edad_detalle JSONB  {"NEO":{"m":2,"f":1}, ...}
-- Columnas fuera: edad, unidad_edad, grupo_edad
--
-- `cantidad` se conserva y ahora guarda la suma del desglose (la calcula
-- la aplicación). Los índices hacen el filtrado por grupo y por sexo:
--
--   grupo_edad_detalle->'NEO'->>'m'  > 0   (grupo con cantidad)
--
-- NOTA sobre `sexo`: NO se elimina. Los 18 538 registros previos a esta
-- migración nunca tuvieron grupo etario, solo sexo y cantidad, así que la
-- columna se conserva como dato histórico. Los registros nuevos la dejan
-- en NULL y su sexo vive dentro del JSONB.
-- ============================================================

BEGIN;

-- ── 1. Columna del desglose ──
ALTER TABLE proce_medicos
    ADD COLUMN IF NOT EXISTS grupo_edad_detalle JSONB;

-- ── 2. Respaldo desde el esquema anterior, si está presente ──
-- 2.a. Desde grupo_edad (una fila = un grupo y un sexo)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'proce_medicos' AND column_name = 'grupo_edad'
    ) THEN
        EXECUTE $sql$
            UPDATE proce_medicos
            SET grupo_edad_detalle = jsonb_build_object(
                    grupo_edad,
                    CASE WHEN sexo = 'F'
                         THEN jsonb_build_object('m', 0, 'f', GREATEST(COALESCE(cantidad, 0), 0))
                         ELSE jsonb_build_object('m', GREATEST(COALESCE(cantidad, 0), 0), 'f', 0)
                    END
                )
            WHERE grupo_edad IS NOT NULL
              AND grupo_edad IN ('NEO','LAC','PRI','SEG','ADO','ADU','ADM')
        $sql$;
        RAISE NOTICE 'Respaldo desde grupo_edad completado.';
    END IF;
END $$;

-- 2.b. Desde edad + unidad_edad, solo si no vino desglose de 2.a.
DO $$
DECLARE
    tiene_edad boolean;
    tiene_unidad boolean;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'proce_medicos' AND column_name = 'edad'
    ) INTO tiene_edad;

    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'proce_medicos' AND column_name = 'unidad_edad'
    ) INTO tiene_unidad;

    IF tiene_edad AND tiene_unidad THEN
        -- La unidad solo contextualiza: se conserva como atributo del grupo
        -- cuando el valor cae en un rango con equivalente en la escala IMCI.
        EXECUTE $sql$
            UPDATE proce_medicos
            SET grupo_edad_detalle = jsonb_build_object(
                    CASE
                        WHEN unidad_edad = 'días'   AND edad <= 28   THEN 'NEO'
                        WHEN unidad_edad = 'meses'  AND edad <= 12   THEN 'LAC'
                        WHEN unidad_edad = 'años'  AND edad <  5    THEN 'PRI'
                        WHEN unidad_edad = 'años'  AND edad <= 11   THEN 'SEG'
                        WHEN unidad_edad = 'años'  AND edad <  18   THEN 'ADO'
                        WHEN unidad_edad = 'años'  AND edad <= 59   THEN 'ADU'
                        WHEN unidad_edad = 'años'  AND edad >  59   THEN 'ADM'
                    END,
                    CASE WHEN sexo = 'F'
                         THEN jsonb_build_object('m', 0, 'f', GREATEST(COALESCE(cantidad, 0), 0))
                         ELSE jsonb_build_object('m', GREATEST(COALESCE(cantidad, 0), 0), 'f', 0)
                    END
                )
            WHERE edad IS NOT NULL
              AND unidad_edad IS NOT NULL
              AND grupo_edad_detalle IS NULL
        $sql$;
        RAISE NOTICE 'Respaldo desde edad/unidad_edad intentado.';
    END IF;
END $$;

-- 2.c. Descarta claves de grupo que no sean válidos
UPDATE proce_medicos
SET grupo_edad_detalle = (
    SELECT COALESCE(jsonb_object_agg(g.clave, g.valor), '{}'::jsonb)
    FROM jsonb_each(grupo_edad_detalle) AS g(clave, valor)
    WHERE g.clave IN ('NEO','LAC','PRI','SEG','ADO','ADU','ADM')
)
WHERE grupo_edad_detalle IS NOT NULL
  AND EXISTS (
      SELECT 1
      FROM jsonb_object_keys(grupo_edad_detalle) AS g(clave)
      WHERE g.clave NOT IN ('NEO','LAC','PRI','SEG','ADO','ADU','ADM')
  );

-- ── 3. Índices para los filtros por grupo y por sexo ──
CREATE INDEX IF NOT EXISTS idx_proce_medicos_grupo_edad_detalle
    ON proce_medicos USING GIN (grupo_edad_detalle);

-- Para el filtro "este grupo tiene cantidad": se consulta por clave.
CREATE INDEX IF NOT EXISTS idx_proce_medicos_grupo_edad
    ON proce_medicos ((grupo_edad_detalle -> 'NEO'))
    WHERE grupo_edad_detalle IS NOT NULL;

-- ── 4. Fuera las columnas que ya no se usan ──
ALTER TABLE proce_medicos
    DROP COLUMN IF EXISTS edad,
    DROP COLUMN IF EXISTS unidad_edad,
    DROP COLUMN IF EXISTS grupo_edad;

ALTER TABLE proce_medicos
    DROP CONSTRAINT IF EXISTS proce_medicos_grupo_edad_check;

COMMENT ON COLUMN proce_medicos.grupo_edad_detalle IS
    'Cantidades por grupo etario IMCI/OMS y sexo: {"NEO":{"m":2,"f":1}}. Solo guarda grupos con cantidad. La suma es proce_medicos.cantidad.';

COMMENT ON COLUMN proce_medicos.sexo IS
    'Solo para registros históricos anteriores al desglose por grupo etario. Los registros nuevos lo dejan en NULL.';

COMMIT;

-- ============================================================
-- >>> FIN: 072_procedimientos_grupo_edad_detalle.sql
-- ============================================================


-- ============================================================
-- >>> INICIO: 073_catalogo_procedimientos_completo.sql
-- ============================================================

-- ============================================================
-- 073_catalogo_procedimientos_completo.sql
-- Carga el catálogo maestro completo desde data/quirofano_procedimientos.csv
-- en catalogo_procedimientos (la que usa el registro de procedimientos).
--
-- CONTEXTO
--   catalogo_procedimientos tenía 195 filas y ninguna con especialidad_ref.
--   El CSV maestro tiene 316 nombres únicos; 35 ya existían, así que se
--   insertan los %d restantes.
--
-- LIMPIEZA APLICADA AL GENERAR ESTE ARCHIVO
--   1. Se quita el prefijo "(VAC)" de 3 nombres: era markup de la hoja de
--      cálculo, no parte del procedimiento.
--   2. Se descartan 2 nombres repetidos en el CSV con especialidades
--      distintas, porque catalogo_procedimientos.nombre es UNIQUE:
--        - Amputación   (Cirugía / Traumatología)   -> se conserva Cirugía
--        - Circuncisión (Pediatría / Cirugía)       -> se conserva Pediatría
--   3. especialidad_ref se llena con el mapeo declarado en el propio CSV:
--      Cirugía->CIR, Traumatología->TRA, Pediatría->PED,
--      Ginecología->GIN, Medicina Interna->MI.
--
-- PENDIENTE DE REVISIÓN (del CSV de origen)
--   Estas 7 entradas del CSV no son procedimientos, sino diagnósticos,
--   complicaciones o indicaciones de manejo. Se insertaron porque pertenecen
--   al catálogo de origen, pero conviene revisarlas:
--     - Infección del tracto urinario (UTI)
--     - Infección en sitio quirúrgico
--     - Síndrome compartimental (fasciotomía)
--     - Manejo conservador
--     - Control de daños
--     - Control de hemorragias
--     - Dedo en gatillo
--
-- Es idempotente: se puede volver a aplicar sin duplicar.
-- abreviatura queda NULL en las filas nuevas: no se inventan códigos y la
-- columna es nullable. Los 195 registros previos siguen sin abreviatura
-- propia y sin especialidad_ref.
-- ============================================================

BEGIN;

INSERT INTO catalogo_procedimientos (abreviatura, nombre, descripcion, anestesia, especialidad_ref, activo)
VALUES
    (NULL, 'Cambio de terapia de presión negativa', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colocación de terapia de presión negativa', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Retiro de terapia de presión negativa', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Abdominoplastia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Adenoamigdalectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Adenoidectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Adhesiolisis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Amigdalectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Amputación de urgencia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Anastomosis intestinal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Angioplastia coronaria', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Angioplastía de acceso vascular para hemodiálisis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Apendicectomía pediátrica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'Atresias intestinales', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'Banding', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Biopsia cervical', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Biopsia excisional', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Biopsia incisional', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Biopsia quirúrgica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Biopsia renal abierta', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Biopsia renal percutánea', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Blefaroplastia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Broncoscopia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Bypass coronario', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Bypass femoropoplíteo', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Bypass gástrico', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cateterismo cardíaco', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cauterización', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cesárea de emergencia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cierre de herida', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cierre de ostomías', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Circuncisión', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'Cirugía de aneurisma cerebral', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía de aorta torácica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía de catarata', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Hemiartroplastia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Cirugía de columna vertebral', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía de diverticulitis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía de hidrocele', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Catéter umbilical (arterial/venoso)', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Artrodesis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Cirugía de quistes hepáticos', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía de quistes sebáceos', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía de sarcomas', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía de tiroides', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía de tumores cerebrales', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía de varicocele', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía endoscópica nasal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía hepatobiliar', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía ortognática', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía paliativa oncológica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía pancreática', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía por prolapso genital', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Cirugía vascular periférica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cistolitotomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cistoscopia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colectomía oncológica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colgajo cutáneo', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colocación de arco de Erich', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colocación de catéter doble J', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colocación de catéter para diálisis peritoneal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colocación de catéter para hemodiálisis (temporal)', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colocación de catéter tunelizado para hemodiálisis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colocación de injerto arteriovenoso para diálisis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colonoscopia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colostomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Colporrafia posterior', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Conización cervical', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Control de daños', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Control de hemorragias', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Corrección de atresia intestinal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'Artrocentesis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Antrodesis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Corrección de labio y paladar hendido', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'CPRE', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Craneotomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Craniectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Craniectomía descompresiva', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Creación de fístula arteriovenosa (braquiocefálica)', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Creación de fístula arteriovenosa (radiocefálica)', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cuadrantectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Debridamiento quirúrgico', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Debulking tumoral', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Decorticación pleural', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Decorticación pulmonar', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Decortificación de riñón', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Dedo en gatillo', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Derivación ventriculoperitoneal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Desbridamiento de tejidos infectados', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Discectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Disección axilar', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Disección cervical', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Drenaje biliar', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Drenaje de absceso renal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Drenaje de abscesos profundos', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Drenaje epidural', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Drenaje torácico', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Embarazo ectópico', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Embolectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Endarterectomía carotídea', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Endoscopía + dilatación', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Endoscopia digestiva alta', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Endoscopía y toma de biopsia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Enterectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Esplenectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Estenosis pilórica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'Estimulación cerebral profunda', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Evacuación de hematomas', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Eventrorrafia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Extracción de cuerpos extraños', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Extracción de terceros molares', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Fasciotomía urgente', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Fenestración laparoscópica de quiste renal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Tratamiento quirúrgico de fractura expuesta', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Fístula arteriovenosa', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Fistulectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Fisurotomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Funduplicatura', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Fusión vertebral', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Gastrectomía oncológica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Gastrectomía subtotal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Gastrectomía total', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Gastroscopía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'MI'), TRUE),
    (NULL, 'Gastrostomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Gastrostomía pediátrica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'Hemicolectomía derecha', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Hemicolectomía izquierda', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Hepatectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Hernioplastía incisional', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Hernioplastía inguinal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Hernioplastía umbilical', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Herniorrafia inguinal pediátrica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'Histerectomía abdominal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Histerectomía laparoscópica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Histerectomía quirúrgica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Ileostomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Implantación de marcapasos', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Infección del tracto urinario (UTI)', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Síndrome compartimental (fasciotomía)', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Invaginación intestinal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'Laminectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Laparoscopía diagnóstica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Laparoscopía ginecológica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Laparotomía de urgencia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Laparotomía exploradora', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Laringectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'LASIK', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Lavado y desbridamiento', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Lavado y desbridamiento por quemadura', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Levantamiento óseo frontal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reparación de tendones', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Ligadura de trompas', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Ligadura tubárica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Linfadenectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Litotricia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Lobectomía pulmonar', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Malformaciones anorrectales', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'Malformaciones congénitas', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'Mamoplastia reductora', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reparación de ligamentos', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Manejo de quemaduras', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Manejo quirúrgico de trauma abdominal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Manga gástrica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Marsupialización de quiste de Bartolino', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Marsupialización de quiste renal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Mastectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Mastoidectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Mediastinoscopia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reemplazo de rodilla', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Microlaringoscopía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Nefrectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Nefrectomía parcial', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Nefrectomía radical', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Nefrectomía simple', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Nefrolitotomía percutánea', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Nefrostomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Nefrostomía percutánea', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Nefroureterectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Neumonectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reemplazo de cadera', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Reducción cerrada de fractura', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Osteotomía mandibular', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Otoplastia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Pancreatectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Pancreatectomía oncológica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Paratiroidectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Pericardiocentesis quirúrgica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Pieloplastía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Piloromiotomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'PED'), TRUE),
    (NULL, 'Piloroplastía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Pleurodesis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Polipectomía endoscópica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Polipectomía nasal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Queratoplastia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Quistectomía ovárica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Reconstrucción facial', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reconstrucción mamaria', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reconstrucción maxilar', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reducción abierta y fijación interna (RAFI)', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Osteostomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Reducción de fractura facial', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Meniscectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Reemplazo valvular', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reexploración abdominal y cierre por planos', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reimplante de uréter', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Remodelación de Colostomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reparación de aneurismas', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reparación de desgarros obstétricos', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Reparación de desprendimiento de retina', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reparación de fístula arteriovenosa', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reparación de fractura facial', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reparación de fracturas craneales', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reparación de hernias', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reparación de lesiones complejas', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Manejo conservador', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Reparación de perforaciones gastrointestinales', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reparación de prolapso uterino', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Liberación del túnel carpiano', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Reparación valvular', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Reparación vascular', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Resección de lipomas', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Resección de tejido', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Resección de tumor cerebral', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Resección de tumores', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Resección de tumores de piel y tejidos blandos', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Resección de tumores maxilares', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Resección de tumores mediastinales', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Resección hepática', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Resección intestinal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Resección transuretral de próstata', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Retiro de catéter para diálisis peritoneal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Retiro de catéter para hermodiálisis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Revisión o recambio de catéter peritoneal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Revisión quirúrgica de acceso vascular', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Rinoplastia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Salpingectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Salpingooforectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Septoplastia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Sigmoidectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Infección en sitio quirúrgico', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Sutura de heridas', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Fijador externo', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Timpanoplastia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Tiroidectomía oncológica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Tiroidectomía parcial', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Tiroidectomía total', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Toracotomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Toracotomía de emergencia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Trabeculectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Transposición de vena basílica', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Traqueostomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Trasplante cardíaco', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Trasplante de médula ósea', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Trasplante hepático', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Trasplante pancreático', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Trasplante pulmonar', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Trasplante renal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Tratamiento quirúrgico de endometriosis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Fijación percutánea', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Tratamiento quirúrgico del sangrado digestivo', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Trombectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Trombectomía de fístula arteriovenosa', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Tumorectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Ureterolitotomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Ureteroscopia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Vagotomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Varicectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Varicocelectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Vitrectomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Yeyunostomía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Fijación externa', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Corrección de escoliosis', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Corrección de deformidades', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Cirugía de pie', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Biopsia Tru-Cut', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'CIR'), TRUE),
    (NULL, 'Cirugía de mano', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Cirugía de columna', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Artroscopía', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE),
    (NULL, 'Reparación de desgarro cervical/vaginal', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'GIN'), TRUE),
    (NULL, 'Artroplastia', NULL, 0, (SELECT id FROM especialidades WHERE abreviatura = 'TRA'), TRUE)

ON CONFLICT (nombre) DO NOTHING;

COMMIT;

-- ============================================================
-- >>> FIN: 073_catalogo_procedimientos_completo.sql
-- ============================================================

