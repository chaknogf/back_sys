-- ============================================================
-- 072_procedimientos_grupos_edad.sql
-- Reemplaza la edad exacta (edad + unidad_edad) por el grupo etario
-- de clasificación IMCI/OMS en los registros de procedimientos.
--
-- El campo unidad_edad se introducía junto a edad en la versión
-- anterior del formulario; ambos se retiran porque la clasificación
-- etaria de las督导ías no admite valores exactos, solo tramos.
--
-- Códigos adoptados:
--   NEO  Neonato (0 a 28 días)
--   LAC  Lactante (>28 días a 12 meses)
--   PRI  Primera infancia (1 a <5 años)
--   SEG  Segunda infancia (>5 a 11 años)
--   ADO  Adolescente (12 a <18 años)
--   ADU  Adulto (18 a 59 años)
--   ADM  Adulto mayor (60 años o más)
--
-- Nota: las columnas eliminadas estaban vacías (0 registros con
-- edad informada), por lo que no se requiere migración de datos.
-- ============================================================

BEGIN;

ALTER TABLE proce_medicos
    ADD COLUMN IF NOT EXISTS grupo_edad VARCHAR(10);

-- Verificación previa: no debe haber información que perder
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM proce_medicos
        WHERE edad IS NOT NULL OR unidad_edad IS NOT NULL
    ) THEN
        RAISE EXCEPTION
            'proce_medicos contiene datos en edad/unidad_edad; migrarlos a grupo_edad antes de eliminar las columnas';
    END IF;
END $$;

ALTER TABLE proce_medicos
    DROP COLUMN IF EXISTS edad,
    DROP COLUMN IF EXISTS unidad_edad;

-- Restricción de dominio: solo los 7 grupos definidos
ALTER TABLE proce_medicos
    DROP CONSTRAINT IF EXISTS proce_medicos_grupo_edad_check;

ALTER TABLE proce_medicos
    ADD CONSTRAINT proce_medicos_grupo_edad_check
    CHECK (
        grupo_edad IS NULL
        OR grupo_edad IN ('NEO', 'LAC', 'PRI', 'SEG', 'ADO', 'ADU', 'ADM')
    );

COMMENT ON COLUMN proce_medicos.grupo_edad IS
    'Grupo etario IMCI/OMS: NEO, LAC, PRI, SEG, ADO, ADU, ADM';

COMMIT;