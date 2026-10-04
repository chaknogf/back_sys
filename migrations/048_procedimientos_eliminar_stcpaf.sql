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