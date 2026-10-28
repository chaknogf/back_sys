-- Rollback de 087. Revisar conteos del paso 1 antes de ejecutar.
BEGIN;

SELECT
  COUNT(*) FILTER (WHERE aplicado)                            AS aplicados,
  COUNT(*) FILTER (WHERE aplicado AND paciente_id IS NOT NULL) AS con_paciente_real,
  COUNT(*) FILTER (WHERE aplicado AND pacientes_sigsa3_id IS NOT NULL) AS con_paciente_sigsa
FROM sigsa3_asociacion;

-- 1. Quitar asociación de staging
UPDATE sigsa3
   SET paciente_id = NULL,
       consulta_id = NULL,
       pacientes_sigsa3_id = NULL
  FROM sigsa3_asociacion a
 WHERE a.sigsa3_id = sigsa3.id AND a.aplicado;

-- 2. Eliminar pacientes creados en pacientes_sigsa3 que no tengan dependencias
DELETE FROM pacientes_sigsa3 ps
 WHERE NOT EXISTS (SELECT 1 FROM sigsa3 s WHERE s.pacientes_sigsa3_id = ps.id)
   AND NOT EXISTS (SELECT 1 FROM sigsa3_registros r WHERE r.pacientes_sigsa3_id = ps.id);

-- 3. Quitar columnas y tablas
ALTER TABLE sigsa3 DROP COLUMN IF EXISTS pacientes_sigsa3_id;
ALTER TABLE sigsa3_registros DROP COLUMN IF EXISTS pacientes_sigsa3_id;
DROP TABLE IF EXISTS sigsa3_asociacion;
DROP TABLE IF EXISTS pacientes_sigsa3;

COMMIT;
