-- Migration 014: catálogo propio de tipos de consulta SIGSA-3
-- Las categorías SIGSA-3 (1 Primera, 2 Reconsulta, 3 Emergencia, 4 Interconsulta)
-- NO coinciden con el catálogo tipos_consulta (COEX, Hospitalización, Emergencia).
-- Se crea una tabla separada y se repuntan las FKs de sigsa3 y sigsa3_registros.

BEGIN;

CREATE TABLE IF NOT EXISTS tipos_consulta_sigsa3 (
    id SMALLINT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(200)
);

INSERT INTO tipos_consulta_sigsa3 (id, nombre, descripcion) VALUES
    (1, 'Primeras', 'Consulta SIGSA-3 de primera vez'),
    (2, 'Reconsultas', 'Consulta SIGSA-3 de seguimiento / reconsulta'),
    (3, 'Emergencia', 'Consulta SIGSA-3 de emergencia'),
    (4, 'Interconsultas', 'Consulta SIGSA-3 de interconsulta')
ON CONFLICT (id) DO UPDATE SET nombre = EXCLUDED.nombre;

-- Repuntar FK de sigsa3 (staging): tipo_consulta_id -> tipos_consulta_sigsa3
ALTER TABLE sigsa3 DROP CONSTRAINT IF EXISTS sigsa3_tipo_consulta_id_fkey;
ALTER TABLE sigsa3
    ADD CONSTRAINT sigsa3_tipo_consulta_id_fkey
    FOREIGN KEY (tipo_consulta_id) REFERENCES tipos_consulta_sigsa3(id) ON DELETE SET NULL;

-- Repuntar FK de sigsa3_registros (normalizado): tipo_consulta_id -> tipos_consulta_sigsa3
ALTER TABLE sigsa3_registros DROP CONSTRAINT IF EXISTS sigsa3_registros_tipo_consulta_id_fkey;
ALTER TABLE sigsa3_registros
    ADD CONSTRAINT sigsa3_registros_tipo_consulta_id_fkey
    FOREIGN KEY (tipo_consulta_id) REFERENCES tipos_consulta_sigsa3(id) ON DELETE SET NULL;

COMMIT;
