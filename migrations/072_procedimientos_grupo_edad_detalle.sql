-- ============================================================
-- 072_procedimientos_grupo_edad_detalle.sql
-- Reemplaza la edad exacta y el desglose por grupo único (grupo_edad)
-- por un desglose estructurado por grupo de edad y sexo en JSONB.
--
-- Columnas eliminadas: edad, unidad_edad, grupo_edad
-- Columna nueva: grupo_edad_detalle JSONB ({"NEO": {"m":2,"f":1}, ...})
-- Cantidad se conserva como total del desglose (se recalcula en aplicación).
-- ============================================================

BEGIN;

ALTER TABLE proce_medicos ADD COLUMN IF NOT EXISTS grupo_edad_detalle JSONB;

-- Respaldo: si existen datos con el modelo antiguo, convertir cada fila
-- a un desglose de un solo grupo (sexo M/F). Se omiten filas sin datos.
UPDATE proce_medicos
SET grupo_edad_detalle = jsonb_build_object(
        grupo_edad,
        CASE
            WHEN sexo = 'F' THEN jsonb_build_object('m', 0, 'f', GREATEST(COALESCE(cantidad, 0), 0))
            WHEN sexo = 'M' THEN jsonb_build_object('m', GREATEST(COALESCE(cantidad, 0), 0), 'f', 0)
            ELSE jsonb_build_object('m', GREATEST(COALESCE(cantidad, 0), 0), 'f', 0)
        END
    )
WHERE grupo_edad IS NOT NULL
  AND grupo_edad IN ('NEO','LAC','PRI','SEG','ADO','ADU','ADM');

-- Eliminar columnas redundantes
ALTER TABLE proce_medicos
    DROP COLUMN IF EXISTS edad,
    DROP COLUMN IF EXISTS unidad_edad,
    DROP COLUMN IF EXISTS grupo_edad;

-- Eliminar constraint de sexo (solo aplica a registros históricos, pero ya no es obligatorio)
ALTER TABLE proce_medicos
    DROP CONSTRAINT IF EXISTS proce_medicos_sexo_check;

COMMENT ON COLUMN proce_medicos.grupo_edad_detalle IS
    'Desglose de cantidades por grupo etario IMCI/OMS y sexo: {"NEO":{"m":2,"f":1}}.';

COMMIT;
