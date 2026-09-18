-- Migration 009: pacientes - extraer datos_extra.socioeconomicos → columnas
-- Ahorro: ~20 MB (132k filas)

BEGIN;

ALTER TABLE pacientes ADD COLUMN IF NOT EXISTS discapacidad VARCHAR(50);
ALTER TABLE pacientes ADD COLUMN IF NOT EXISTS educacion VARCHAR(100);
ALTER TABLE pacientes ADD COLUMN IF NOT EXISTS estado_civil VARCHAR(50);
ALTER TABLE pacientes ADD COLUMN IF NOT EXISTS es_estudiante_publico VARCHAR(2);
ALTER TABLE pacientes ADD COLUMN IF NOT EXISTS ocupacion VARCHAR(100);
ALTER TABLE pacientes ADD COLUMN IF NOT EXISTS es_personal_hospital VARCHAR(2);

-- Migrar datos existentes desde JSONB
UPDATE pacientes SET
    discapacidad = datos_extra->'socioeconomicos'->>'discapacidad',
    educacion = datos_extra->'socioeconomicos'->>'educacion',
    estado_civil = datos_extra->'socioeconomicos'->>'estado_civil',
    es_estudiante_publico = datos_extra->'socioeconomicos'->>'estudiante_publico',
    ocupacion = datos_extra->'socioeconomicos'->>'ocupacion',
    es_personal_hospital = datos_extra->'socioeconomicos'->>'personal_hospital'
WHERE datos_extra IS NOT NULL
  AND jsonb_typeof(datos_extra->'socioeconomicos') = 'object';

-- Eliminar socioeconomicos del JSONB (ahora en columnas)
UPDATE pacientes SET datos_extra = datos_extra - 'socioeconomicos'
WHERE datos_extra ? 'socioeconomicos';

COMMIT;
