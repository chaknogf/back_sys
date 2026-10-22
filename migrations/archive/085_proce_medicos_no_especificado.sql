-- 085_proce_medicos_no_especificado.sql
-- Procedimientos médicos: soporte explícito de la categoría "No especificado".
--
-- Contexto:
--   `proce_medicos` ya desagrega las cantidades por edad y sexo en columnas
--   (032_procedimientos_unificado.sql): nino_m/nino_f, adulto_m/adulto_f y
--   sin_edad_m/sin_edad_f. La categoría `sin_edad` recogía únicamente los
--   registros históricos migrados sin edad conocida.
--
-- Cambio funcional (API + frontend):
--   La captura ahora permite registrar la fila "No especificado" de forma
--   editable, y la validación de `ProceMedicoCreate` acepta un registro cuya
--   única cantidad provenga de `sin_edad_*`. Esto exige que:
--     1. las columnas `sin_edad_m`/`sin_edad_f` existan con DEFAULT 0 e
--        iguales restricciones de no-negatividad que el resto;
--     2. `cantidad` siga siendo >= 1 (el backend la recalcula sumando las seis
--        columnas y el CHECK `proce_medicos_cantidad_check` la protege).
--
-- Idempotente: sólo agrega lo que falte (`IF NOT EXISTS`). En la base actual es
-- un no-op; se incluye para dejar el esquema explícito y reproducible.

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Columnas del desglose sin edad (defensivo: ya existen vía 032)
-- ---------------------------------------------------------------------------
ALTER TABLE public.proce_medicos
    ADD COLUMN IF NOT EXISTS sin_edad_m integer NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS sin_edad_f integer NOT NULL DEFAULT 0;

-- ---------------------------------------------------------------------------
-- 2. No-negatividad del desglose (mismo criterio que el resto de categorías)
-- ---------------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'proce_medicos_sin_edad_m_check'
    ) THEN
        ALTER TABLE public.proce_medicos
            ADD CONSTRAINT proce_medicos_sin_edad_m_check CHECK (sin_edad_m >= 0);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'proce_medicos_sin_edad_f_check'
    ) THEN
        ALTER TABLE public.proce_medicos
            ADD CONSTRAINT proce_medicos_sin_edad_f_check CHECK (sin_edad_f >= 0);
    END IF;

    -- cantidad >= 1: el backend la recalcula con las seis columnas, así que un
    -- registro con sólo "No especificado" queda con cantidad >= 1 y es válido.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'proce_medicos_cantidad_check'
    ) THEN
        ALTER TABLE public.proce_medicos
            ADD CONSTRAINT proce_medicos_cantidad_check CHECK (cantidad >= 1);
    END IF;
END $$;

-- ---------------------------------------------------------------------------
-- 3. Índice parcial para reportes/consultas de la categoría sin edad
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_proce_medicos_sin_edad
    ON public.proce_medicos ((sin_edad_m + sin_edad_f))
    WHERE (sin_edad_m + sin_edad_f) > 0;

COMMIT;
