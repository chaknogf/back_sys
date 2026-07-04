-- Migration: Simplify SIGSA-3 table
-- Remove unnecessary fields, add medico_id and consulta_id

-- Add new columns
ALTER TABLE sigsa3 ADD COLUMN IF NOT EXISTS medico_id INTEGER REFERENCES medicos(id) ON DELETE SET NULL;
ALTER TABLE sigsa3 ADD COLUMN IF NOT EXISTS consulta_id INTEGER REFERENCES consultas(id) ON DELETE SET NULL;

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS ix_sigsa3_medico_id ON sigsa3(medico_id);
CREATE INDEX IF NOT EXISTS ix_sigsa3_consulta_id ON sigsa3(consulta_id);

-- Drop unnecessary columns
ALTER TABLE sigsa3 DROP COLUMN IF EXISTS pueblo;
ALTER TABLE sigsa3 DROP COLUMN IF EXISTS comunidad_linguistica;
ALTER TABLE sigsa3 DROP COLUMN IF EXISTS departamento_residencia;
ALTER TABLE sigsa3 DROP COLUMN IF EXISTS municipio_residencia;
ALTER TABLE sigsa3 DROP COLUMN IF EXISTS comunidad;
ALTER TABLE sigsa3 DROP COLUMN IF EXISTS direccion;
ALTER TABLE sigsa3 DROP COLUMN IF EXISTS descripcion_diagnostico_control;
ALTER TABLE sigsa3 DROP COLUMN IF EXISTS tipologia;
