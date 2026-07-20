-- Migration: Add indexes for SIGSA-3 association pipeline
-- Acelera /sigsa3/asociar-todo y queries de listado frecuentes

-- Trigram GIN: acelera ILIKE '%pattern%' en Paso 2 (nombre_paciente CONTAINS nombre_completo)
CREATE INDEX IF NOT EXISTS ix_sigsa3_nombre_trgm ON sigsa3 USING GIN (nombre_paciente gin_trgm_ops);

-- Sigsa3: columnas usadas en JOINs de asociación y filtros de listado
CREATE INDEX IF NOT EXISTS ix_sigsa3_nombre_paciente ON sigsa3(nombre_paciente);
CREATE INDEX IF NOT EXISTS ix_sigsa3_no_historia_clinica ON sigsa3(no_historia_clinica);
CREATE INDEX IF NOT EXISTS ix_sigsa3_fecha_consulta ON sigsa3(fecha_consulta);

-- Compuestos usados en los merges de asociar_paciente_y_consulta
CREATE INDEX IF NOT EXISTS ix_sigsa3_paciente_fecha ON sigsa3(paciente_id, fecha_consulta);
CREATE INDEX IF NOT EXISTS ix_sigsa3_nhc_fecha ON sigsa3(no_historia_clinica, fecha_consulta);

-- Consultas: compuesto para merge por documento + fecha (paso 5)
CREATE INDEX IF NOT EXISTS idx_consulta_documento_fecha ON consultas(documento, fecha_consulta);
