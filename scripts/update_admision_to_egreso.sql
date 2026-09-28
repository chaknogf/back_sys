-- Cambiar estado de consultas en "admision" mayores a 1 mes a "egreso"
-- Excluye los patient_ids especificados

-- Primero, ver cuántas registros se verán afectadas
SELECT COUNT(*) AS total_a_actualizar
FROM consultas
WHERE ultimo_estado = 'admision'
  AND fecha_consulta < CURRENT_DATE - INTERVAL '1 month'
  AND paciente_id NOT IN (
    88755, 135181, 127828, 135187, 135202, 116189, 112817, 85635,
    117770, 135151, 135207, 128459, 121361, 127819, 121815, 135003,
    130338, 134802, 135125, 135052, 135006, 116205, 75630, 135115,
    135073, 135007, 134731, 124566, 118215, 135182, 135180, 135140,
    135137, 103007, 106141, 134799, 134971, 103860, 58215, 116063,
    135039, 95882, 56605, 16656, 110391, 18262, 75370, 81177,
    113724, 135011, 7860
  );

-- Descomentar la siguiente línea para ejecutar el UPDATE:
/*
UPDATE consultas
SET
    ultimo_estado = 'egreso',
    fecha_egreso = CURRENT_DATE
WHERE ultimo_estado = 'admision'
  AND fecha_consulta < CURRENT_DATE - INTERVAL '1 month'
  AND paciente_id NOT IN (
    88755, 135181, 127828, 135187, 135202, 116189, 112817, 85635,
    117770, 135151, 135207, 128459, 121361, 127819, 121815, 135003,
    130338, 134802, 135125, 135052, 135006, 116205, 75630, 135115,
    135073, 135007, 134731, 124566, 118215, 135182, 135180, 135140,
    135137, 103007, 106141, 134799, 134971, 103860, 58215, 116063,
    135039, 95882, 56605, 16656, 110391, 18262, 75370, 81177,
    113724, 135011, 7860
  );
*/
