-- 084_almacen_insumos.sql
-- Módulo de almacén de insumos: catálogo (insumos + presentaciones),
-- bodega + farmacia + productos afines, kardex unificado, requisiciones,
-- despachos (a servicio, a paciente o traslado entre almacenes), atenciones
-- con consumo de insumos y unidosis por paciente.
--
-- Flujo soportado:
--   insumo → bodega (ingreso/egreso) → kardex → farmacia/productos afines
--          → kardex → servicios y pacientes → unidosis / requisición
--
-- Estructura del catálogo espejo del CSV de importación (fuente de verdad):
--   RENGLÓN | CÓDIGO DE INSUMO | NOMBRE | CARACTERÍSTICAS |
--   NOMBRE DE LA PRESENTACIÓN | CANTIDAD Y UNIDAD DE MEDIDA | CÓDIGO DE PRESENTACIÓN
--   - `insumos` = 1 fila por CÓDIGO DE INSUMO (cols 1-4, textos CRUDOS:
--     características en formato "Estado: X;  Grado: Y;  Uso: Z;").
--   - `presentaciones` = 1 fila por CÓDIGO DE PRESENTACIÓN (cols 5-7;
--     cantidad+unidad se guardan crudos en `cantidad_unidad`, ej. "250 Mililitro").
--   - `renglon` es VARCHAR(3) para conservar ceros a la izquierda (011, 031).
--     No hay tabla de renglones: son inmutables.
--   - Parseo futuro (JSONB de características, cantidad/unidad) cuando se
--     revise el universo de datos cargados.
--   - El stock real NO vive aquí: es de `lotes` (bodega/kardex).
--
-- Aditiva e idempotente (según patrón de 078/083).

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. CATÁLOGO DE INSUMOS (espejo CSV)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS insumos (
    id             SERIAL PRIMARY KEY,
    renglon        VARCHAR(3)  NOT NULL,          -- '261', '011', '031'
    codigo_insumo  VARCHAR(20) NOT NULL,
    nombre         TEXT        NOT NULL,
    caracteristicas TEXT       NOT NULL DEFAULT '',  -- CRUDO tal cual CSV
    activo         BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_insumos_codigo UNIQUE (codigo_insumo)
);

CREATE TABLE IF NOT EXISTS presentaciones (
    id                   SERIAL PRIMARY KEY,
    insumo_id            INTEGER NOT NULL REFERENCES insumos(id) ON DELETE CASCADE,
    nombre               VARCHAR(50) NOT NULL DEFAULT 'Envase',  -- NOMBRE DE LA PRESENTACIÓN
    cantidad_unidad      TEXT        NOT NULL DEFAULT '',        -- CRUDO: '250 Mililitro' (no es stock)
    codigo_presentacion  VARCHAR(20) NOT NULL,
    activo               BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_presentaciones_codigo UNIQUE (codigo_presentacion)
);

-- ---------------------------------------------------------------------------
-- 2. ALMACENES Y STOCK (LOTES)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS almacenes (
    id          SERIAL PRIMARY KEY,
    codigo      VARCHAR(20) NOT NULL,
    nombre      VARCHAR(100) NOT NULL,
    tipo        VARCHAR(20) NOT NULL DEFAULT 'bodega'
        CHECK (tipo IN ('bodega', 'farmacia', 'productos_afines', 'servicio')),
    activo      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_almacenes_codigo UNIQUE (codigo),
    CONSTRAINT uq_almacenes_nombre UNIQUE (nombre)
);

CREATE TABLE IF NOT EXISTS lotes (
    id                 SERIAL PRIMARY KEY,
    presentacion_id    INTEGER NOT NULL REFERENCES presentaciones(id) ON DELETE RESTRICT,
    almacen_id         INTEGER NOT NULL REFERENCES almacenes(id) ON DELETE RESTRICT,
    numero_lote        VARCHAR(50) NOT NULL DEFAULT '',
    fecha_vencimiento  DATE,
    cantidad_actual    NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK (cantidad_actual >= 0),
    costo_unitario     NUMERIC(12,4) NOT NULL DEFAULT 0 CHECK (costo_unitario >= 0),
    activo             BOOLEAN NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_lotes_lote UNIQUE (presentacion_id, almacen_id, numero_lote)
);

-- ---------------------------------------------------------------------------
-- 3. KARDEX UNIFICADO (bodega, farmacia, productos afines, servicios)
--    Una fila = un movimiento sobre un lote en un almacén.
--    Traslado entre almacenes = par de filas (salida en origen + entrada en destino)
--    con el mismo (referencia_tipo='traslado', referencia_id).
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS kardex_movimientos (
    id                SERIAL PRIMARY KEY,
    lote_id           INTEGER NOT NULL REFERENCES lotes(id) ON DELETE RESTRICT,
    almacen_id        INTEGER NOT NULL REFERENCES almacenes(id) ON DELETE RESTRICT,
    tipo_movimiento   VARCHAR(10) NOT NULL
        CHECK (tipo_movimiento IN ('entrada', 'salida', 'traslado', 'consumo', 'ajuste')),
    cantidad          NUMERIC(14,3) NOT NULL CHECK (cantidad > 0),
    saldo_resultante  NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK (saldo_resultante >= 0),
    costo_unitario    NUMERIC(12,4) NOT NULL DEFAULT 0,
    referencia_tipo   VARCHAR(20) NULL
        CHECK (referencia_tipo IS NULL OR referencia_tipo IN
               ('ingreso', 'requisicion', 'despacho', 'traslado', 'unidosis', 'atencion', 'ajuste')),
    referencia_id     INTEGER NULL,
    observacion       TEXT NOT NULL DEFAULT '',
    usuario_id        INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    fecha             TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- 4. REQUISICIÓN (servicio pide → aprueba → despacha)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS requisiciones (
    id                      SERIAL PRIMARY KEY,
    numero                  VARCHAR(20) NOT NULL,
    servicio_solicitante_id INTEGER NOT NULL
        REFERENCES encamamiento(id) ON DELETE RESTRICT,
    personal_solicita_id    INTEGER NULL REFERENCES personal_atencion(id) ON DELETE SET NULL,
    usuario_solicita_id     INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    estado                  VARCHAR(12) NOT NULL DEFAULT 'pendiente'
        CHECK (estado IN ('pendiente', 'aprobada', 'rechazada', 'despachada')),
    observaciones           TEXT NOT NULL DEFAULT '',
    usuario_aprueba_id      INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    fecha_aprobacion        TIMESTAMPTZ NULL,
    activo                  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_requisiciones_numero UNIQUE (numero)
);

CREATE TABLE IF NOT EXISTS requisiciones_detalles (
    id                   SERIAL PRIMARY KEY,
    requisicion_id       INTEGER NOT NULL REFERENCES requisiciones(id) ON DELETE CASCADE,
    presentacion_id      INTEGER NOT NULL REFERENCES presentaciones(id) ON DELETE RESTRICT,
    cantidad_solicitada  NUMERIC(14,3) NOT NULL CHECK (cantidad_solicitada > 0),
    cantidad_despachada  NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK (cantidad_despachada >= 0),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- 5. DESPACHOS (servicio / paciente / traslado entre almacenes)
--    tipo='traslado': bodega ↔ farmacia / productos afines (origen → destino).
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS despachos (
    id                    SERIAL PRIMARY KEY,
    numero                VARCHAR(20) NOT NULL,
    tipo                  VARCHAR(10) NOT NULL DEFAULT 'servicio'
        CHECK (tipo IN ('servicio', 'paciente', 'traslado')),
    almacen_origen_id     INTEGER NOT NULL REFERENCES almacenes(id) ON DELETE RESTRICT,
    almacen_destino_id    INTEGER NULL REFERENCES almacenes(id) ON DELETE RESTRICT,
    requisicion_id        INTEGER NULL REFERENCES requisiciones(id) ON DELETE SET NULL,
    servicio_destino_id   INTEGER NULL REFERENCES encamamiento(id) ON DELETE SET NULL,
    paciente_id           INTEGER NULL REFERENCES pacientes(id) ON DELETE SET NULL,
    personal_receptor_id  INTEGER NULL REFERENCES personal_atencion(id) ON DELETE SET NULL,
    usuario_despacha_id   INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    estado                VARCHAR(12) NOT NULL DEFAULT 'borrador'
        CHECK (estado IN ('borrador', 'despachado', 'anulado')),
    fecha                 TIMESTAMPTZ NOT NULL DEFAULT now(),
    observaciones         TEXT NOT NULL DEFAULT '',
    activo                BOOLEAN NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_despachos_numero UNIQUE (numero),
    CONSTRAINT chk_despachos_destino CHECK (
        (tipo = 'traslado'   AND almacen_destino_id  IS NOT NULL) OR
        (tipo = 'servicio'   AND servicio_destino_id IS NOT NULL) OR
        (tipo = 'paciente'   AND paciente_id         IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS despachos_detalles (
    id             SERIAL PRIMARY KEY,
    despacho_id    INTEGER NOT NULL REFERENCES despachos(id) ON DELETE CASCADE,
    lote_id        INTEGER NOT NULL REFERENCES lotes(id) ON DELETE RESTRICT,
    cantidad       NUMERIC(14,3) NOT NULL CHECK (cantidad > 0),
    costo_unitario NUMERIC(12,4) NOT NULL DEFAULT 0,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- 6. ATENCIONES + CONSUMO DE INSUMOS
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS atenciones (
    id                    SERIAL PRIMARY KEY,
    paciente_id           INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE RESTRICT,
    personal_atencion_id  INTEGER NULL REFERENCES personal_atencion(id) ON DELETE SET NULL,
    servicio_id           INTEGER NULL REFERENCES encamamiento(id) ON DELETE SET NULL,
    consulta_id           INTEGER NULL REFERENCES consultas(id) ON DELETE SET NULL,
    estado                VARCHAR(12) NOT NULL DEFAULT 'abierta'
        CHECK (estado IN ('abierta', 'finalizada', 'cancelada')),
    fecha                 TIMESTAMPTZ NOT NULL DEFAULT now(),
    observaciones         TEXT NOT NULL DEFAULT '',
    activo                BOOLEAN NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS atenciones_insumos (
    id             SERIAL PRIMARY KEY,
    atencion_id    INTEGER NOT NULL REFERENCES atenciones(id) ON DELETE CASCADE,
    lote_id        INTEGER NOT NULL REFERENCES lotes(id) ON DELETE RESTRICT,
    despacho_id    INTEGER NULL REFERENCES despachos(id) ON DELETE SET NULL,
    cantidad       NUMERIC(14,3) NOT NULL CHECK (cantidad > 0),
    origen         VARCHAR(10) NOT NULL DEFAULT 'directo'
        CHECK (origen IN ('despacho', 'directo')),
    usuario_id     INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    fecha          TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- 7. UNIDOSIS (preparación de dosis unitaria por paciente desde farmacia)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS unidosis (
    id                 SERIAL PRIMARY KEY,
    numero             VARCHAR(20) NULL,
    paciente_id        INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE RESTRICT,
    atencion_id        INTEGER NULL REFERENCES atenciones(id) ON DELETE SET NULL,
    almacen_origen_id  INTEGER NOT NULL REFERENCES almacenes(id) ON DELETE RESTRICT,
    personal_prepara_id INTEGER NULL REFERENCES personal_atencion(id) ON DELETE SET NULL,
    usuario_prepara_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    estado             VARCHAR(12) NOT NULL DEFAULT 'preparada'
        CHECK (estado IN ('preparada', 'administrada', 'cancelada')),
    fecha              TIMESTAMPTZ NOT NULL DEFAULT now(),
    observaciones      TEXT NOT NULL DEFAULT '',
    activo             BOOLEAN NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_unidosis_numero UNIQUE (numero)
);

CREATE TABLE IF NOT EXISTS unidosis_detalles (
    id                   SERIAL PRIMARY KEY,
    unidosis_id          INTEGER NOT NULL REFERENCES unidosis(id) ON DELETE CASCADE,
    lote_id              INTEGER NOT NULL REFERENCES lotes(id) ON DELETE RESTRICT,
    cantidad             NUMERIC(14,3) NOT NULL CHECK (cantidad > 0),
    dosis                VARCHAR(100) NOT NULL DEFAULT '',   -- "1 cada 8 horas"
    fecha_administracion TIMESTAMPTZ NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- ÍNDICES
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_insumos_renglon ON insumos (renglon) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_insumos_nombre ON insumos USING gin (nombre gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_insumos_busqueda ON insumos (f_unaccent(lower(nombre)));

CREATE INDEX IF NOT EXISTS idx_presentaciones_insumo ON presentaciones (insumo_id) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_presentaciones_cantidad_unidad
    ON presentaciones USING gin (cantidad_unidad gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_lotes_almacen ON lotes (almacen_id) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_lotes_presentacion ON lotes (presentacion_id) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_lotes_vencimiento ON lotes (fecha_vencimiento)
    WHERE activo AND fecha_vencimiento IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_kardex_lote_fecha ON kardex_movimientos (lote_id, fecha DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_kardex_almacen_fecha ON kardex_movimientos (almacen_id, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_kardex_tipo_fecha ON kardex_movimientos (tipo_movimiento, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_kardex_referencia ON kardex_movimientos (referencia_tipo, referencia_id)
    WHERE referencia_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_requisiciones_estado ON requisiciones (estado) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_requisiciones_servicio ON requisiciones (servicio_solicitante_id, created_at DESC) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_requisiciones_detalles_req ON requisiciones_detalles (requisicion_id);

CREATE INDEX IF NOT EXISTS idx_despachos_tipo_estado ON despachos (tipo, estado) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_despachos_almacen ON despachos (almacen_origen_id, fecha DESC) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_despachos_servicio ON despachos (servicio_destino_id, fecha DESC) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_despachos_paciente ON despachos (paciente_id, fecha DESC) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_despachos_requisicion ON despachos (requisicion_id) WHERE requisicion_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_despachos_detalles_despacho ON despachos_detalles (despacho_id);
CREATE INDEX IF NOT EXISTS idx_despachos_detalles_lote ON despachos_detalles (lote_id);

CREATE INDEX IF NOT EXISTS idx_atenciones_paciente ON atenciones (paciente_id, fecha DESC) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_atenciones_fecha ON atenciones (fecha DESC) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_atenciones_consulta ON atenciones (consulta_id) WHERE consulta_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_atenciones_insumos_atencion ON atenciones_insumos (atencion_id);
CREATE INDEX IF NOT EXISTS idx_atenciones_insumos_lote ON atenciones_insumos (lote_id);

CREATE INDEX IF NOT EXISTS idx_unidosis_paciente ON unidosis (paciente_id, fecha DESC) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_unidosis_estado ON unidosis (estado) WHERE activo;
CREATE INDEX IF NOT EXISTS idx_unidosis_detalles_unidosis ON unidosis_detalles (unidosis_id);

-- ---------------------------------------------------------------------------
-- SEEDS (idempotentes) — ejemplo tomado del CSV de importación
-- ---------------------------------------------------------------------------

-- Almacenes de la cadena: bodega → farmacia / productos afines
INSERT INTO almacenes (codigo, nombre, tipo) VALUES
    ('BOD-01', 'Bodega Principal', 'bodega'),
    ('FAR-01', 'Farmacia', 'farmacia'),
    ('PAF-01', 'Productos Afines', 'productos_afines')
ON CONFLICT (codigo) DO NOTHING;

-- Insumos (cols 1-4 del CSV, textos crudos)
INSERT INTO insumos (renglon, codigo_insumo, nombre, caracteristicas) VALUES
    ('261', '173975', 'A-amilasa de bacillus sp',
     ' Estado: Líquido;  Grado: Reactivo;  Uso: Laboratorio; '),
    ('261', '125557', 'A-amilasa de bacillus sp',
     ' Estado: Sólido;  Grado: Reactivo;  Uso: Laboratorio; ')
ON CONFLICT (codigo_insumo) DO NOTHING;

-- Presentaciones (cols 5-7 del CSV, cantidad+unidad crudos)
INSERT INTO presentaciones (insumo_id, nombre, cantidad_unidad, codigo_presentacion)
SELECT i.id, e.nombre, e.cantidad_unidad, e.codigo_presentacion
FROM (VALUES
    ('173975', 'Envase', '250 Mililitro',  '203578'),
    ('125557', 'Envase', '250 Miligramos', '146481'),
    ('125557', 'Envase', '1 Gramos',       '146482')
) AS e(codigo_insumo, nombre, cantidad_unidad, codigo_presentacion)
JOIN insumos i ON i.codigo_insumo = e.codigo_insumo
ON CONFLICT (codigo_presentacion) DO NOTHING;

COMMIT;
