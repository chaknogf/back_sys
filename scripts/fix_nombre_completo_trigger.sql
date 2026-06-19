-- ============================================================
-- fix_nombre_completo_trigger.sql
-- Agrega "de " antes de apellido_casada en nombre_completo
-- Uso: psql -f fix_nombre_completo_trigger.sql
-- ============================================================

BEGIN;

-- 1. Reemplazar función trigger
CREATE OR REPLACE FUNCTION public.actualizar_nombre_completo()
RETURNS TRIGGER AS $$
DECLARE
  _casada TEXT;
BEGIN
  _casada := NEW.nombre->>'apellido_casada';
  IF _casada IS NOT NULL AND _casada != '' THEN
    IF NOT (_casada ILIKE 'de %') THEN
      _casada := 'de ' || _casada;
    END IF;
  ELSE
    _casada := '';
  END IF;
  NEW.nombre_completo := regexp_replace(
    TRIM(
      COALESCE(NEW.nombre->>'primer_nombre', '') || ' ' ||
      COALESCE(NEW.nombre->>'segundo_nombre', '') || ' ' ||
      COALESCE(NEW.nombre->>'otro_nombre', '') || ' ' ||
      COALESCE(NEW.nombre->>'primer_apellido', '') || ' ' ||
      COALESCE(NEW.nombre->>'segundo_apellido', '') || ' ' ||
      _casada
    ),
    '\s+', ' ', 'g'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Refrescar registros existentes con apellido_casada
UPDATE pacientes
SET nombre = nombre
WHERE nombre->>'apellido_casada' IS NOT NULL
  AND nombre->>'apellido_casada' != '';

COMMIT;
