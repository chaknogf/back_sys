CREATE DATABASE hospital;

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

-- Índices por claves del campo nombre
CREATE INDEX idx_pacientes_nombre_primer ON pacientes ((nombre ->> 'primer'));

CREATE INDEX idx_pacientes_nombre_segundo ON pacientes ((nombre ->> 'segundo'));

CREATE INDEX idx_pacientes_nombre_apellido ON pacientes ((nombre ->> 'apellido'));

-- Índices por contacto (en caso de que se busque por email o teléfono)
CREATE INDEX idx_pacientes_contacto_telefono ON pacientes ((contacto ->> 'telefono'));

CREATE INDEX idx_pacientes_contacto_email ON pacientes ((contacto ->> 'email'));

-- Índice por estado (activo/inactivo/fallecido)
CREATE INDEX idx_pacientes_estado ON pacientes (estado);

-- Índice por fecha de nacimiento
CREATE INDEX idx_pacientes_fecha_nacimiento ON pacientes (fecha_nacimiento);

-- Índice por fecha de creación
CREATE INDEX idx_pacientes_creado_en ON pacientes (creado_en);

-- Índice GIN general para búsquedas avanzadas por referencias
CREATE INDEX idx_pacientes_referencias_gin ON pacientes USING GIN (referencias);

-- Índice GIN para datos_extra (para filtros por nacionalidad, ocupación, idiomas, etc.)
CREATE INDEX idx_pacientes_datos_extra_gin ON pacientes USING GIN (datos_extra);