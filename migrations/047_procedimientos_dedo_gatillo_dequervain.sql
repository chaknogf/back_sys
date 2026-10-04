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