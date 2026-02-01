CREATE TABLE expediente_control (
    anio SMALLINT PRIMARY KEY,
    ultimo_correlativo INT NOT NULL DEFAULT 0,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE emergencia_control (
    anio SMALLINT PRIMARY KEY,
    ultimo_correlativo INT NOT NULL DEFAULT 0,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

#consultar duplicados activos
SELECT
    p.id,
    p.nombre,
    p.expediente,
    p.datos_extra->>'personaid' AS personaid,
    cnt.total_registros
FROM pacientes p
JOIN (
    SELECT
        datos_extra->>'personaid' AS personaid,
        COUNT(*) AS total_registros
    FROM pacientes
    WHERE datos_extra ? 'personaid'
      AND estado <> 'I'
    GROUP BY datos_extra->>'personaid'
    HAVING COUNT(*) > 1
) cnt
ON p.datos_extra->>'personaid' = cnt.personaid
WHERE p.estado <> 'I'
ORDER BY cnt.total_registros DESC, personaid, p.id;