-- ============================================================
-- fix_nombre_completo_existing.sql
-- Corrige nombre_completo en registros existentes:
-- 1. Actualiza el trigger para que produzca UPPERCASE con "de " check
-- 2. Refresca TODOS los registros forzando al trigger a recalcular
-- Uso: psql -d tu_bd -f fix_nombre_completo_existing.sql
-- ============================================================

BEGIN;

-- 1. Reemplazar función trigger con UPPERCASE + "de " check
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
  NEW.nombre_completo := UPPER(regexp_replace(
    TRIM(
      COALESCE(NEW.nombre->>'primer_nombre', '') || ' ' ||
      COALESCE(NEW.nombre->>'segundo_nombre', '') || ' ' ||
      COALESCE(NEW.nombre->>'otro_nombre', '') || ' ' ||
      COALESCE(NEW.nombre->>'primer_apellido', '') || ' ' ||
      COALESCE(NEW.nombre->>'segundo_apellido', '') || ' ' ||
      _casada
    ),
    '\s+', ' ', 'g'
  ));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Refrescar registros con apellido_casada (corrige "de " faltante)
UPDATE pacientes SET nombre = nombre
WHERE nombre->>'apellido_casada' IS NOT NULL
  AND nombre->>'apellido_casada' != '';

-- 3. Refrescar registros sin apellido_casada que no estén en UPPERCASE
UPDATE pacientes SET nombre = nombre
WHERE (nombre->>'apellido_casada' IS NULL OR nombre->>'apellido_casada' = '')
  AND nombre_completo IS DISTINCT FROM UPPER(nombre_completo);

COMMIT;
