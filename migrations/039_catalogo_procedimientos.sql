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
ON CONFLICT (nombre) DO NOTHING;

COMMIT;

-- Verificación
SELECT COUNT(*) AS total_catalogo FROM catalogo_procedimientos;