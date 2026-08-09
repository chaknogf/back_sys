-- Optimización de /sigsa3/asociar-pacientes-masivo
--
-- Ejecutar una sola vez contra PostgreSQL antes de procesar lotes grandes.
-- Los índices existentes se conservan; estos cubren las filas pendientes y
-- las llaves usadas en los matches deterministas del pipeline.

-- Paso 2a: SIGSA pendiente por número de historia clínica → expediente.
CREATE INDEX IF NOT EXISTS ix_sigsa3_pendiente_nhc
    ON sigsa3 (no_historia_clinica)
    WHERE paciente_id IS NULL
      AND no_historia_clinica IS NOT NULL;

-- Paso 2b y paso 5: documento/historia clínica + fecha.
CREATE INDEX IF NOT EXISTS ix_sigsa3_pendiente_nhc_fecha
    ON sigsa3 (no_historia_clinica, fecha_consulta)
    WHERE paciente_id IS NULL
      AND no_historia_clinica IS NOT NULL
      AND fecha_consulta IS NOT NULL;

-- Localiza filas que aún requieren asociar consulta sin abarcar la tabla completa.
CREATE INDEX IF NOT EXISTS ix_sigsa3_pendiente_paciente_fecha
    ON sigsa3 (paciente_id, fecha_consulta)
    WHERE consulta_id IS NULL
      AND paciente_id IS NOT NULL
      AND fecha_consulta IS NOT NULL;

-- Paso 4–6: búsquedas de consultas por paciente y fecha.
CREATE INDEX IF NOT EXISTS ix_consultas_paciente_fecha_tipo
    ON consultas (paciente_id, fecha_consulta, tipo_consulta);
