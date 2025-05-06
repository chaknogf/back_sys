CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
     -- 🔐 Identificadores múltiples
    identificadores JSONB NOT NULL, -- Ej: [{ "tipo": "DPI", "valor": "1234567890101" }, { "tipo": "expediente", "valor": "20250001" }]
    -- 🧍‍♂️ Identificación personal
    primer_nombre VARCHAR(50),
    segundo_nombre VARCHAR(50),
    otros_nombres VARCHAR(100),
    primer_apellido VARCHAR(50),
    segundo_apellido VARCHAR(50),
    sexo VARCHAR(2),
    fecha_nacimiento DATE,
    -- ☎️ Contacto
    contacto JSONB,         -- { "telefono": "...", "email": "...", "direccion": "..." }
    -- 👪 Referencias
    referencias JSONB,      -- [{ "nombre": "...", "parentesco": "...", "telefono": "..." }]
    -- 🌍 Otros datos del paciente
    datos_extra JSONB,      -- { "nacionalidad": "...", "ocupacion": "...", "idiomas": [...] }
    -- ⚙️ Metadatos del sistema
    estado VARCHAR(2) DEFAULT 'A',         -- 'A'=Activo, 'I'=Inactivo, 'F'=Fallecido
    creado_por VARCHAR(50),                -- usuario o sistema creador
    actualizado_por VARCHAR(50),           -- último usuario que modificó
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 🔎 Índice para búsqueda eficiente dentro del campo 'identificadores'
CREATE INDEX idx_identificadores_gin
ON pacientes USING GIN (identificadores jsonb_path_ops);
-- 🔎 Índice para filtrar rápidamente por 'estado' (activo, inactivo, fallecido)
CREATE INDEX idx_estado
ON pacientes (estado);
-- 📅 Índices útiles para ordenar o filtrar por fechas
CREATE INDEX idx_creado_en
ON pacientes (creado_en);
CREATE INDEX idx_actualizado_en
ON pacientes (actualizado_en);
-- ☎️ Índice para búsquedas dentro del campo 'contacto'
CREATE INDEX idx_contacto_gin
ON pacientes USING GIN (contacto jsonb_path_ops);
-- 👪 Índice para búsquedas dentro de 'referencias'
CREATE INDEX idx_referencias_gin
ON pacientes USING GIN (referencias jsonb_path_ops);
-- 🌍 Índice para consultas en 'datos_extra'
CREATE INDEX idx_datos_extra_gin
ON pacientes USING GIN (datos_extra jsonb_path_ops);

-- Buscar por DPI dentro de identificadores
-- SELECT * FROM pacientes
-- WHERE identificadores @> '[{"tipo": "DPI", "valor": "1234567890101"}]';

-- Buscar pacientes por nacionalidad
-- SELECT * FROM pacientes
-- WHERE datos_extra @> '{"nacionalidad": "Guatemalteca"}';

-- Filtrar pacientes activos creados en el último mes
-- SELECT * FROM pacientes
-- WHERE estado = 'A' AND creado_en >= NOW() - INTERVAL '1 month';

