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