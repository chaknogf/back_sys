-- =====================================================================
-- Migration 029 — Personal de atención + Citaciones
-- ---------------------------------------------------------------------
-- 1) Renombra la tabla `medicos` → `personal_atencion` (ahí se registran
--    médicos y otro personal; el nombre lo refleja).
-- 2) Renombra TODAS las columnas FK `medico_id` → `personal_atencion_id`
--    que apuntan a esa tabla.
-- 3) Crea `citas_dias_inhabiles` (fechas sin agendar: feriados/asuetos,
--    controladas por el administrador).
-- 4) Agrega `citas.personal_atencion_id` (quién atiende la cita).
--
-- Aplicar en producción:
--   PGPASSWORD=secreto123 psql -h localhost -U admin -d hospital \
--     -v ON_ERROR_STOP=1 -f migrations/029_personal_atencion_citas.sql
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- 1) Tabla: medicos → personal_atencion
--    (las secuencias e índices se conservan con su nombre; Postgres los
--     mantiene funcionales al renombrar la tabla, y renombrar la secuencia
--     rompería el DEFAULT nextval() existente).
-- ---------------------------------------------------------------------
ALTER TABLE medicos RENAME TO personal_atencion;

-- ---------------------------------------------------------------------
-- 2) Columnas FK: medico_id → personal_atencion_id
-- ---------------------------------------------------------------------
ALTER TABLE personal_salud            RENAME COLUMN medico_id TO personal_atencion_id;
ALTER TABLE defunciones               RENAME COLUMN medico_id TO personal_atencion_id;
ALTER TABLE intervenciones_quirurgicas RENAME COLUMN medico_id TO personal_atencion_id;
ALTER TABLE sigsa3                    RENAME COLUMN medico_id TO personal_atencion_id;
ALTER TABLE sigsa3_registros          RENAME COLUMN medico_id TO personal_atencion_id;
ALTER TABLE constancia_nacimiento    RENAME COLUMN medico_id TO personal_atencion_id;

-- Renombres de constraints/índices conocidos (cosmético, no afecta integridad).
ALTER TABLE constancia_nacimiento
  RENAME CONSTRAINT fk_constancia_medico TO fk_constancia_personal_atencion;

-- ---------------------------------------------------------------------
-- 3) Días inhábiles para citas (feriados / asuetos oficiales)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS citas_dias_inhabiles (
  id         SERIAL PRIMARY KEY,
  fecha      DATE NOT NULL UNIQUE,
  motivo     VARCHAR(200),
  activo     BOOLEAN NOT NULL DEFAULT TRUE,
  created_by VARCHAR(20),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- 4) Cita: personal que atiende (referencia a personal_atencion)
-- ---------------------------------------------------------------------
ALTER TABLE citas
  ADD COLUMN IF NOT EXISTS personal_atencion_id INTEGER
    REFERENCES personal_atencion(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS ix_citas_personal_atencion
  ON citas(personal_atencion_id);

COMMIT;