-- Migration: convertir colegiado a varchar(20) único + agregar pasaporte
-- Ejecutar después de cambiar el modelo Python

ALTER TABLE medicos ALTER COLUMN colegiado TYPE varchar(20);
ALTER TABLE medicos ADD CONSTRAINT medicos_colegiado_key UNIQUE (colegiado);
ALTER TABLE medicos ADD COLUMN IF NOT EXISTS pasaporte varchar(20);
CREATE INDEX IF NOT EXISTS idx_medicos_pasaporte ON medicos (pasaporte);
