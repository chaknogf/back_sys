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
WHERE id = 29;

-- Colocación de Tubo Intercostal (pleurotomía de emergencia)
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Tubo Intercostal',
    abreviatura = 'CTI',
    descripcion = 'Pleurotomía cerrada o tubo de tórax para neumotórax, hemotórax o derrame pleural.'
WHERE id = 93;

-- Colocación de Barra Denis Browne (pediatría, pie equinovaro)
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Barra Denis Browne',
    abreviatura = 'CBDB',
    descripcion = 'Dispositivo ortopédico pediátrico (barra metálica + botas) para corrección de pie equinovaro.'
WHERE id = 188;

-- Colocación de DIU (inserción, inversa a RDIU)
UPDATE catalogo_procedimientos
SET descripcion = 'Inserción de dispositivo intrauterino (DIU) como método anticonceptivo de larga duración.'
WHERE id = 55;

-- Colocación de Jadelle (planificación familiar, inversa a RJAD)
UPDATE catalogo_procedimientos
SET descripcion = 'Inserción de implante subdérmico anticonceptivo (Jadelle) en el brazo.'
WHERE id = 254;

-- Colocación de Sonda (orogástrica o Foley)
UPDATE catalogo_procedimientos
SET descripcion = 'Inserción de sonda orogástrica, vesical (Foley) o nasogástrica.'
WHERE id = 5;

-- Colocación de Membrana (membrana amniótica o biológica)
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Membrana',
    abreviatura = 'CDM',
    descripcion = 'Aplicación de membrana amniótica o biológica en cirugía oftálmica, maxilofacial o de herida crónica.'
WHERE id = 133;

-- Colocación de Surfactante (neonatología)
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Surfactante',
    abreviatura = 'CS',
    descripcion = 'Administración de surfactante pulmonar en neonatos prematuros (vía tubo endotraqueal).'
WHERE id = 103;

-- Colocación de Sutura de B-Lynch (ginecología de emergencia)
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Sutura de B-Lynch',
    abreviatura = 'COLB-LY',
    descripcion = 'Sutura uterina compresiva de emergencia para hemorragia masiva postparto.'
WHERE id = 105;

-- Toma y Colocación de Puntos Óseos (traumatología)
UPDATE catalogo_procedimientos
SET nombre = 'Toma y Colocación de Puntos Óseos',
    abreviatura = 'TCPO',
    descripcion = 'Fijación directa en hueso con alambres o suturas pesadas (cerclaje) en traumatología.'
WHERE id = 166;

COMMIT;