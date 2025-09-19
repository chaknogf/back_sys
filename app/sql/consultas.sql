-- Tabla consultas
CREATE TABLE consultas (
    id SERIAL PRIMARY KEY,
    expediente_id VARCHAR(20) NOT NULL,
    paciente_id INT NOT NULL,
    tipo_consulta INT NOT NULL,
    especialidad INT NOT NULL,
    servicio INT NOT NULL,
    documento VARCHAR(255) NOT NULL,
    fecha_consulta DATE NOT NULL,
    hora_consulta TIME NOT NULL,
    ciclo JSONB DEFAULT '{}'::jsonb,
    indicadores JSONB DEFAULT '[]'::jsonb,
    detalle_clinicos JSONB DEFAULT '{}'::jsonb,
    sistema JSONB DEFAULT '{}'::jsonb,
    signos_vitales JSONB DEFAULT '{}'::jsonb,
    antecedentes JSONB DEFAULT '{}'::jsonb,
    ordenes JSONB DEFAULT '{}'::jsonb,
    estudios JSONB DEFAULT '{}'::jsonb,
    comentario JSONB DEFAULT '{}'::jsonb,
    impresion_clinica JSONB DEFAULT '{}'::jsonb,
    tratamiento JSONB DEFAULT '{}'::jsonb,
    examen_fisico JSONB DEFAULT '{}'::jsonb,
    nota_enfermeria JSONB DEFAULT '{}'::jsonb,
    contraindicado TEXT,
    presa_quirurgica JSONB DEFAULT '{}'::jsonb,
    egreso JSONB DEFAULT '{}'::jsonb,
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

-- Índices compuestos para filtros frecuentes
CREATE INDEX idx_consultas_paciente_fecha ON consultas (paciente_id, fecha_consulta);

CREATE INDEX idx_consultas_paciente_tipo ON consultas (paciente_id, tipo_consulta);

-- Índices GIN para JSONB
CREATE INDEX idx_consultas_ciclo_gin ON consultas USING GIN (ciclo);

CREATE INDEX idx_consultas_indicadores_gin ON consultas USING GIN (indicadores);

CREATE INDEX idx_consultas_detalle_clinicos_gin ON consultas USING GIN (detalle_clinicos);

CREATE INDEX idx_consultas_signos_vitales_gin ON consultas USING GIN (signos_vitales);

CREATE INDEX idx_consultas_antecedentes_gin ON consultas USING GIN (antecedentes);

CREATE INDEX idx_consultas_ordenes_gin ON consultas USING GIN (ordenes);

CREATE INDEX idx_consultas_estudios_gin ON consultas USING GIN (estudios);

-- GIN opcionales para campos clínicos recientes
CREATE INDEX idx_consultas_comentario_gin ON consultas USING GIN (comentario);

CREATE INDEX idx_consultas_impresion_clinica_gin ON consultas USING GIN (impresion_clinica);

CREATE INDEX idx_consultas_tratamiento_gin ON consultas USING GIN (tratamiento);

CREATE INDEX idx_consultas_examen_fisico_gin ON consultas USING GIN (examen_fisico);

CREATE INDEX idx_consultas_nota_enfermeria_gin ON consultas USING GIN (nota_enfermeria);

CREATE INDEX idx_consultas_egreso_gin ON consultas USING GIN (egreso);

CREATE INDEX idx_consultas_presa_quirurgica_gin ON consultas USING GIN (presa_quirurgica);

-- Índice correcto para texto simple
CREATE INDEX idx_consultas_contraindicado_text ON consultas (contraindicado);