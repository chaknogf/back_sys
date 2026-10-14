-- 077_ciclos_uisau.sql
-- Agrega la columna JSONB `uisau` a `ciclos_consulta` para registrar los datos
-- propios del rol UISAU (estado del paciente, información/contacto y nota
-- clínica), reutilizando el flujo de ciclos/notas existente.
-- Aditiva e idempotente.

ALTER TABLE ciclos_consulta
    ADD COLUMN IF NOT EXISTS uisau JSONB;

COMMENT ON COLUMN ciclos_consulta.uisau IS
    'Datos exclusivos del rol UISAU: estado_paciente, informacion_contacto y nota_clinica';
