-- Migración 076: Agrega columna datos_extra a intervenciones_quirurgicas
-- Permite registrar información adicional: circulante, medicos que apoyan, instrumentista, etc.

ALTER TABLE intervenciones_quirurgicas
ADD COLUMN datos_extra JSONB NULL;