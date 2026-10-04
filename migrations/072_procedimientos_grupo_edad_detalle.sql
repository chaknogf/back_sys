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