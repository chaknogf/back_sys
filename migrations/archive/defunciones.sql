-- Migration: Crear tabla defunciones
-- Los datos del fallecido, madre y médico se obtienen vía JOIN con pacientes/medicos.
-- Las edades se calculan automáticamente desde fecha_nacimiento y fecha_defuncion.

CREATE TABLE IF NOT EXISTS defunciones (
    id SERIAL PRIMARY KEY,

    -- Médico que reporta (el resto se obtiene de medicos.id)
    medico_id INTEGER REFERENCES medicos(id) ON DELETE SET NULL,

    -- Fecha de defunción
    fecha_defuncion TIMESTAMPTZ,

    -- Fallecido (datos demográficos desde pacientes.id)
    paciente_id INTEGER REFERENCES pacientes(id) ON DELETE SET NULL,
    fallecido_edad_horas INTEGER,   -- calculado: < 1 día
    fallecido_edad_dias INTEGER,    -- calculado: < 30 días
    fallecido_edad_meses INTEGER,   -- calculado: < 1 año
    fallecido_edad_anios INTEGER,   -- calculado: >= 1 año
    mujer_edad_fertil BOOLEAN DEFAULT FALSE,  -- TRUE si sexo=F y edad 10-54

    -- III - Muerte gestacional (mujer 10-54 años)
    muerte_gestacion VARCHAR(30),   -- EMBARAZO, PARTO, PUERPERIO, 43d_11m, NO_ESTABA, IGNORADO

    -- IV - Causas de defunción
    causa_a TEXT,
    causa_b TEXT,
    causa_c TEXT,
    causa_d TEXT,
    causa_intervalo TEXT,
    causa_otros TEXT,

    -- V - Presunto suicidio/homicidio/accidente
    fue_presunto VARCHAR(20),
    lugar_lesion VARCHAR(50),
    ocurrio_trabajo BOOLEAN,
    accidente_transito BOOLEAN,
    arma VARCHAR(200),

    -- Madre (datos demográficos desde pacientes.id)
    madre_id INTEGER REFERENCES pacientes(id) ON DELETE SET NULL,
    madre_edad INTEGER,                        -- calculado
    madre_sabe_leer_escribir VARCHAR(10),       -- calculado de datos_extra.socioeconomico.educacion

    -- Datos del feto (mortinato)
    es_fetal BOOLEAN DEFAULT FALSE,
    embarazos_previvos_vivos INTEGER,
    embarazos_previvos_muertos INTEGER,
    fetal_sexo VARCHAR(1),
    fetal_murio_antes_parto BOOLEAN,
    fetal_parto_tipo VARCHAR(20),
    fetal_clase_parto VARCHAR(20),
    fetal_via_parto VARCHAR(20),
    fetal_semanas_gestacion INTEGER,
    fetal_causas_fetales TEXT,
    fetal_causas_maternas TEXT,

    -- Metadata
    registrador_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    observaciones TEXT,
    estado VARCHAR(1) NOT NULL DEFAULT 'A',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_defunciones_paciente_id ON defunciones(paciente_id);
CREATE INDEX IF NOT EXISTS idx_defunciones_madre_id ON defunciones(madre_id);
CREATE INDEX IF NOT EXISTS idx_defunciones_medico_id ON defunciones(medico_id);
CREATE INDEX IF NOT EXISTS idx_defunciones_fecha ON defunciones(fecha_defuncion);
CREATE INDEX IF NOT EXISTS idx_defunciones_es_fetal ON defunciones(es_fetal);
CREATE INDEX IF NOT EXISTS idx_defunciones_mujer_fertil ON defunciones(mujer_edad_fertil);
CREATE INDEX IF NOT EXISTS idx_defunciones_estado ON defunciones(estado);

-- Trigger para updated_at
CREATE OR REPLACE FUNCTION update_defunciones_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_defunciones_updated_at ON defunciones;
CREATE TRIGGER trg_defunciones_updated_at
    BEFORE UPDATE ON defunciones
    FOR EACH ROW
    EXECUTE FUNCTION update_defunciones_updated_at();

-- 2026-07-15: Added estado column (A=Activo, I=Inactivo)
-- ALTER TABLE defunciones ADD COLUMN estado VARCHAR(1) NOT NULL DEFAULT 'A';
