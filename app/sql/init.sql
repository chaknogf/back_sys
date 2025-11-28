CREATE DATABASE IF NOT EXISTS hospital;

CREATE TABLE users (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    unidad INTEGER,
    estado character(1),
    creado_en timestamp without time zone DEFAULT now(),
    actualizado_en timestamp without time zone DEFAULT now()
);

ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq');
ALTER TABLE users ADD CONSTRAINT pk_users PRIMARY KEY (id);
CREATE SEQUENCE IF NOT EXISTS users_id_seq OWNED BY users.id;
ALTER SEQUENCE users_id_seq OWNED BY users.id;

CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
    -- 🔐 Identificadores múltiples
    identificadores JSONB NOT NULL, -- Ej: [{ "tipo": "DPI", "valor": "1234567890101" }, { "tipo": "expediente", "valor": "20250001" }]
    -- 🧍‍♂️ Identificación personal
    nombre JSONB, -- { "primer": "...", "segundo": "...", "otros": ["..."], "apellido": "..." }
    sexo VARCHAR(2),
    fecha_nacimiento DATE,
    -- ☎️ Contacto
    contacto JSONB, -- { "telefono": "...", "email": "...", "direccion": "..." }
    -- 👪 Referencias
    referencias JSONB, -- [{ "nombre": "...", "parentesco": "...", "telefono": "..." }]
    -- 🌍 Otros datos del paciente
    datos_extra JSONB, -- { "nacionalidad": "...", "ocupacion": "...", "idiomas": [...], covid }
    -- ⚙️ Metadatos del sistema
    estado VARCHAR(2) DEFAULT 'A', -- 'A'=Activo, 'I'=Inactivo, 'F'=Fallecido
    metadatos JSONB, -- { "creado_por": "...", "actualizado_por": "..." }
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- 🔎 Índice para búsqueda eficiente dentro del campo 'identificadores'
-- Índice para buscar por identificadores (ej. DPI, expediente)
CREATE INDEX idx_pacientes_identificadores_gin ON pacientes USING GIN (identificadores);
-- Índice específico para buscar por valor dentro del arreglo de identificadores
-- Ejemplo: WHERE identificadores @> '[{"tipo": "DPI", "valor": "1234567890101"}]'
CREATE INDEX idx_pacientes_identificadores_tipo_valor ON pacientes USING GIN (
    (identificadores ->> 'tipo'),
    (identificadores ->> 'valor')
);

CREATE INDEX idx_pacientes_nombre_primer ON pacientes ((nombre ->> 'primer'));
-- Índices por claves del campo nombre
CREATE INDEX idx_pacientes_nombre_segundo ON pacientes ((nombre ->> 'segundo'));

CREATE INDEX idx_pacientes_nombre_apellido ON pacientes ((nombre ->> 'apellido'));

CREATE INDEX idx_pacientes_contacto_telefono ON pacientes ((contacto ->> 'telefono'));
-- Índices por contacto (en caso de que se busque por email o teléfono)
CREATE INDEX idx_pacientes_contacto_email ON pacientes ((contacto ->> 'email'));

CREATE INDEX idx_pacientes_estado ON pacientes (estado);
-- Índice por estado (activo/inactivo/fallecido)
CREATE INDEX idx_pacientes_fecha_nacimiento ON pacientes (fecha_nacimiento);
-- Índice por fecha de nacimiento
CREATE INDEX idx_pacientes_creado_en ON pacientes (creado_en);
-- Índice por fecha de creación
CREATE INDEX idx_pacientes_referencias_gin ON pacientes USING GIN (referencias);
-- Índice GIN general para búsquedas avanzadas por referencias
CREATE INDEX idx_pacientes_datos_extra_gin ON pacientes USING GIN (datos_extra);
-- Índice GIN para datos_extra (para filtros por nacionalidad, ocupación, idiomas, etc.)

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

CREATE TABLE eventos_consulta (
    id SERIAL PRIMARY KEY,
    consulta_id INTEGER NOT NULL REFERENCES consultas (id) ON DELETE CASCADE,
    tipo_evento INTEGER NOT NULL, -- Ej: 'ingreso', 'egreso', 'hospitalización', 'interconsulta', etc.
    datos JSONB, -- contenido variable: { "diagnostico": "...", "sala": "...", "tratamiento": "...", etc. }
    responsable JSONB, -- { "nombre": "...", "profesion": "...", "usuario_id": 3 }
    creado_en TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(2) DEFAULT 'A' -- 'A'=Activo, 'I'=Inactivo
);

-- Índice para acelerar búsquedas por consulta asociada
CREATE INDEX idx_eventos_consulta_consulta_id ON eventos_consulta (consulta_id);

-- Índice para tipo de evento (permite filtrar por 'ingreso', 'egreso', etc.)
CREATE INDEX idx_eventos_consulta_tipo_evento ON eventos_consulta (tipo_evento);

-- Índice para estado (activo/inactivo)
CREATE INDEX idx_eventos_consulta_estado ON eventos_consulta (estado);

-- Índice GIN para búsquedas dentro del JSONB 'datos'
CREATE INDEX idx_eventos_consulta_datos_gin ON eventos_consulta USING GIN (datos);

-- Índice GIN para búsquedas dentro del JSONB 'responsable'
CREATE INDEX idx_eventos_consulta_responsable_gin ON eventos_consulta USING GIN (responsable);


