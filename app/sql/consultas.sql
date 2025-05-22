CREATE TABLE consultas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes (id) ON DELETE CASCADE ON UPDATE CASCADE,
    tipo_consulta INTEGER,
    especialidad INTEGER,
    servicio INTEGER,
    documento VARCHAR(20),
    fecha_consulta DATE,
    hora_consulta TIME,
    ciclo JSONB, -- { "activo": "...", "egreso": "...", ... }
    indicadores JSONB, -- { "prenatal": 4, "lactancia": true, ... }
    detalle_clinico JSONB, -- { "medico": "...", "diagnostico": "...", ... }
    sistema JSONB, -- { "usuario_creador": "...", ... }
    signos_vitales JSONB, -- { "temperatura": ..., "presion_arterial": "...", ... }
    ansigmas JSONB, -- { "sintomas": [...], "examen_fisico": "...", ... }
    antecedentes JSONB, -- { "alergias": [...], "enfermedades": [...], ... }
    ordenes JSONB, -- { "medicamentos": [...], "examen_fisico": "...", ... }
    estudios JSONB, -- { "laboratorios": [...], "rayos_x": "...", ... }
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🔍 Índice por paciente
CREATE INDEX idx_consultas_paciente_id ON consultas (paciente_id);

-- 📅 Índice por fecha de consulta
CREATE INDEX idx_consultas_fecha ON consultas (fecha_consulta);

-- 🩺 Índice por tipo de consulta
CREATE INDEX idx_consultas_tipo ON consultas (tipo_consulta);

-- 📦 Índice GIN para búsquedas en JSONB
CREATE INDEX idx_consultas_ciclo_gin ON consultas USING GIN (ciclo);

CREATE INDEX idx_consultas_indicadores_gin ON consultas USING GIN (indicadores);

CREATE INDEX idx_consultas_detalle_clinico_gin ON consultas USING GIN (detalle_clinico);

CREATE INDEX idx_consultas_signos_vitales_gin ON consultas USING GIN (signos_vitales);

CREATE INDEX idx_consultas_ansigmas_gin ON consultas USING GIN (ansigmas);

CREATE INDEX idx_consultas_antecedentes_gin ON consultas USING GIN (antecedentes);

CREATE INDEX idx_consultas_ordenes_gin ON consultas USING GIN (ordenes);

CREATE INDEX idx_consultas_estudios_gin ON consultas USING GIN (estudios);