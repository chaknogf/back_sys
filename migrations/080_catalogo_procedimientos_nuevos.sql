-- ============================================================
-- 080_catalogo_procedimientos_nuevos.sql
-- Agrega 15 procedimientos faltantes al catálogo maestro
-- `catalogo_procedimientos`.
--
-- Origen: comparación de un listado externo (327 nombres únicos)
-- contra la tabla. 294 coincidían exactamente; 6 eran variantes
-- de un existente ((VAC) terapia de presión negativa ×3,
-- Aspiración manual endouterina, Extirpación de quistes y
-- lipomas, Endoscopía alta); 12 solapaban palabra con un
-- genérico ya existente (Biopsia, Gastrostomía, Curación,
-- Fototerapia, Colocación de Sonda, Paracentesis, Infiltración).
-- Quedan los 15 nombres sin equivalente en el catálogo.
--
-- Idempotente: ON CONFLICT DO NOTHING cubre los UNIQUE de
-- `nombre` y `abreviatura`. `especialidad_ref` y `abreviatura`
-- quedan NULL, igual que 196 y 281 filas actuales.
-- ============================================================

BEGIN;

INSERT INTO public.catalogo_procedimientos
    (nombre, especialidad_ref, activo)
VALUES
    ('Aféresis y plasmaféresis terapéuticas', NULL, TRUE),
    ('Aspirado y biopsia de médula ósea', NULL, TRUE),
    ('Colocación de catéteres venosos y reservorios', NULL, TRUE),
    ('Criocirugía', NULL, TRUE),
    ('Crioterapia', NULL, TRUE),
    ('Electrocoagulación y crioterapia', NULL, TRUE),
    ('Electrocuretaje', NULL, TRUE),
    ('Escisión de lesiones benignas y malignas', NULL, TRUE),
    ('Exanguinotransfusión y transfusión de componentes sanguíneos', NULL, TRUE),
    ('Frenectomía labial', NULL, TRUE),
    ('Frenectomía lingual', NULL, TRUE),
    ('Infusión de células progenitoras hematopoyéticas', NULL, TRUE),
    ('Pulpotomía y pulpectomía', NULL, TRUE),
    ('Punciones y drenajes terapéuticos', NULL, TRUE),
    ('Retiro de catéteres venosos y reservorios', NULL, TRUE)
ON CONFLICT DO NOTHING;

COMMIT;
