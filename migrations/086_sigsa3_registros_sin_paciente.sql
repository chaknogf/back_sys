-- 086_sigsa3_registros_sin_paciente.sql
-- Permite normalizar registros SIGSA-3 SIN paciente asociado y conserva los
-- valores crudos que no se pudieron normalizar.
--
-- Contexto: el `no_historia_clinica` de staging NO está en el mismo espacio de
-- identificadores que `pacientes.expediente` (formatos tipo '0237-2026-0044-15',
-- CUI en notación científica, etc.), así que la asociación falla para la mayoría
-- de registros. Antes, `normalizar()` solo migraba los que ya tenían paciente_id
-- (obligatorio). Ahora:
--   * `paciente_id` pasa a ser NULLABLE (migración sin paciente asociado).
--   * se agregan columnas crudas (nombre, nhc, sexo, edades, tipo_consulta,
--     cie10 crudo, personal_salud crudo) y `sin_asociar` para trazabilidad.
--
-- Idempotente: solo usa ALTER ... ADD COLUMN IF NOT EXISTS / DROP NOT NULL.

BEGIN;

-- paciente_id deja de ser obligatorio
ALTER TABLE sigsa3_registros
    ALTER COLUMN paciente_id DROP NOT NULL;

-- Datos crudos / fallback para registros no asociados
ALTER TABLE sigsa3_registros
    ADD COLUMN IF NOT EXISTS sin_asociar         BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS nombre_paciente     VARCHAR(150),
    ADD COLUMN IF NOT EXISTS no_historia_clinica VARCHAR(30),
    ADD COLUMN IF NOT EXISTS sexo                VARCHAR(1),
    ADD COLUMN IF NOT EXISTS edad_anios          INTEGER,
    ADD COLUMN IF NOT EXISTS edad_meses         INTEGER,
    ADD COLUMN IF NOT EXISTS edad_dias          INTEGER,
    ADD COLUMN IF NOT EXISTS tipo_consulta       VARCHAR(80),
    ADD COLUMN IF NOT EXISTS codigo_cie_10       VARCHAR(30),
    ADD COLUMN IF NOT EXISTS personal_salud      VARCHAR(100);

-- Índice para localizar rápido los normalizados que quedaron sin paciente
CREATE INDEX IF NOT EXISTS ix_sigsa3_reg_sin_asociar
    ON sigsa3_registros (sin_asociar)
    WHERE sin_asociar;

COMMIT;
