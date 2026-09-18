-- Migration 005: Columnas FK faltantes en sigsa3

ALTER TABLE sigsa3 ADD COLUMN IF NOT EXISTS personal_salud_id INTEGER REFERENCES personal_salud(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_sigsa3_personal_salud_id ON sigsa3(personal_salud_id);

ALTER TABLE sigsa3 ADD COLUMN IF NOT EXISTS codigo_cie_10_id INTEGER REFERENCES cie10_catalogo(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_sigsa3_codigo_cie10_id ON sigsa3(codigo_cie_10_id);
