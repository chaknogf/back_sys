-- ============================================================
-- 066_procedimientos_normalizar_capitalizacion.sql
-- Normaliza todos los nombres del catálogo a formato Título
-- con respeto de preposiciones (de, del, la, el, y, o, en, por, para, con, sin).
--
-- Criterios:
--   * Primera letra de cada palabra en MAYÚSCULAS
--   * Excepción: preposiciones en minúsculas (de, del, la, el, los, las, y, o, en, por, para, con, sin, a, al, un, una)
--   * Mantener siglas comunes en MAYÚSCULAS (DIU, HIV, TAC, RMN, ECG, EMG, FAST, AMEU, BJ, etc.)
--   * Conservar tildes correctas
-- ============================================================

BEGIN;

-- Función auxiliar que aplica Title Case inteligente
CREATE OR REPLACE FUNCTION titulo_inteligente(text) RETURNS text AS $$
DECLARE
    palabra text;
    palabras text[] := string_to_array($1, ' ');
    resultado text := '';
    i int;
    excepciones text[] := ARRAY['de','del','la','el','los','las','y','o','en','por','para','con','sin','a','al','un','una','unos','unas','lo','le','les'];
    siglas text[] := ARRAY['DIU','HIV','TAC','RMN','ECG','EMG','FAST','AMEU','BJ','HTA','DM','EPOC','IRC','ICC','SIDA','TBC','PCR'];
BEGIN
    IF $1 IS NULL OR btrim($1) = '' THEN
        RETURN $1;
    END IF;
    FOR i IN 1..array_length(palabras,1) LOOP
        palabra := palabras[i];
        -- Si la palabra es exactamente una sigla conocida, mantener MAYÚSCULAS
        IF upper(palabra) = ANY(siglas) THEN
            palabras[i] := upper(palabra);
        ELSIF lower(palabra) = ANY(excepciones) AND i > 1 THEN
            palabras[i] := lower(palabra);
        ELSE
            -- Title case preservando la longitud
            palabras[i] := upper(substring(palabra,1,1)) || lower(substring(palabra,2));
        END IF;
    END LOOP;
    resultado := array_to_string(palabras, ' ');
    -- Correcciones específicas de tildes perdidas
    resultado := replace(resultado, 'Repertorio', 'Repertorio');  -- placeholder
    RETURN resultado;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Actualizar nombres aplicando Title Case inteligente
UPDATE catalogo_procedimientos
SET nombre = titulo_inteligente(nombre)
WHERE activo = TRUE
  AND nombre <> titulo_inteligente(nombre);

COMMIT;