-- Tabla consultas
CREATE TABLE consultas (
    id SERIAL PRIMARY KEY,
    expediente VARCHAR(20) NOT NULL,
    paciente_id INT NOT NULL REFERENCES pacientes (id) ON DELETE CASCADE,
    tipo_consulta INT NOT NULL,
    especialidad INT NOT NULL,
    servicio INT NOT NULL,
    documento VARCHAR(255) NOT NULL,
    fecha_consulta DATE NOT NULL,
    hora_consulta TIME NOT NULL,
    indicadores JSONB,
    ciclo JSONB, -- aquí va el timeline
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

-- Índices simples
CREATE INDEX idx_consultas_paciente_id ON consultas (paciente_id);

CREATE INDEX idx_consultas_expediente ON consultas (expediente);

CREATE INDEX idx_consultas_fecha_consulta ON consultas (fecha_consulta);

-- Índices compuestos
CREATE INDEX idx_consultas_tipo_fecha ON consultas (tipo_consulta, fecha_consulta);

CREATE INDEX idx_consultas_especialidad_servicio ON consultas (especialidad, servicio);

-- Índices GIN para JSONB (permiten búsquedas dentro del ciclo y los indicadores)
CREATE INDEX idx_consultas_indicadores_gin ON consultas USING GIN (indicadores);

CREATE INDEX idx_consultas_ciclo_gin ON consultas USING GIN (ciclo);

CREATE OR REPLACE VIEW vista_consultas AS
SELECT
    p.id AS id_paciente,
    p.identificadores,
    p.cui,
    p.expediente,
    p.pasaporte,
    p.nombre,
    p.nombre ->> 'primer_nombre' AS primer_nombre,
    p.nombre ->> 'segundo_nombre' AS segundo_nombre,
    p.nombre ->> 'otro_nombre' AS otro_nombre,
    p.nombre ->> 'primer_apellido' AS primer_apellido,
    p.nombre ->> 'segundo_apellido' AS segundo_apellido,
    p.nombre ->> 'apellido_casada' AS apellido_casada,
    p.sexo,
    p.fecha_nacimiento,
    p.estado,
    c.id AS id_consulta,
    c.tipo_consulta,
    c.especialidad,
    c.servicio,
    c.documento,
    c.fecha_consulta,
    c.hora_consulta,
    c.ciclo
FROM pacientes p
    JOIN consultas c ON p.id = c.paciente_id;

CREATE OR REPLACE VIEW vista_totales AS
SELECT 'pacientes' AS entidad, COUNT(*) AS total
FROM pacientes
UNION ALL
SELECT 'consultas' AS entidad, COUNT(*) AS total
FROM consultas;