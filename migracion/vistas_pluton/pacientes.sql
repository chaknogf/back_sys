CREATE OR REPLACE VIEW vista_pacientes AS
SELECT
    p.id AS paciente_id,
    p.nombre,
    p.apellido,
    p.dpi,
    p.pasaporte,
    p.sexo,
    p.nacimiento,
    p.defuncion,
    p.nacionalidad_iso AS nacionalidad,
    p.lugar_nacimiento,
    p.estado AS estado,
    p.gemelo,
    p.direccion,
    p.municipio,
    p.created_at,
    CONCAT(
        p.telefono1,
        ', ',
        p.telefono2,
        ', ',
        p.telefono3
    ) AS telefono,
    p.email,
    -- Concatenamos los expedientes, referencias y expedientes madre asociados con el paciente
    COALESCE(
        GROUP_CONCAT(
            DISTINCT e.expediente
            ORDER BY e.expediente
        ),
        'Sin expediente'
    ) AS expediente,
    COALESCE(
        GROUP_CONCAT(
            DISTINCT e.referencia_anterior
            ORDER BY e.referencia_anterior
        ),
        'No aplica'
    ) AS referencia_anterior,
    COALESCE(
        GROUP_CONCAT(
            DISTINCT e.expediente_madre
            ORDER BY e.expediente_madre
        ),
        'Sin expediente madre'
    ) AS expediente_madre
FROM pacientes p
    JOIN expedientes e ON p.id = e.paciente_id -- Establece la relación entre paciente y expediente
GROUP BY
    p.id;

CREATE INDEX idx_pacientes_id ON pacientes (id);

CREATE INDEX idx_expedientes_paciente_id ON expedientes (paciente_id);

CREATE OR REPLACE VIEW vr_consultas (
    id,
    exp_id,
    paciente_id,
    historia_clinica,
    fecha_consulta,
    hora,
    fecha_recepcion,
    fecha_egreso,
    tipo_consulta,
    estatus,
    FROM consultas;

CREATE OR REPLACE VIEW vista_pacientes AS
SELECT
    p.id AS paciente_id,
    p.nombre,
    p.apellido,
    p.dpi,
    p.pasaporte,
    p.sexo,
    p.nacimiento,
    p.defuncion,
    p.nacionalidad_iso AS nacionalidad,
    p.lugar_nacimiento,
    p.estado AS estado,
    p.gemelo,
    p.direccion,
    p.municipio,
    p.created_at,
    CONCAT(
        p.telefono1,
        ', ',
        p.telefono2,
        ', ',
        p.telefono3
    ) AS telefono,
    p.email,
    -- Concatenamos los expedientes, referencias y expedientes madre asociados con el paciente
    COALESCE(
        GROUP_CONCAT(
            DISTINCT NULLIF(e.expediente, NULL) 
            ORDER BY e.expediente
        ),
        'Sin expediente'
    ) AS expediente,  -- Aquí agregamos la coma
    COALESCE(
        GROUP_CONCAT(
            DISTINCT e.referencia_anterior
            ORDER BY e.referencia_anterior
        ),
        'No aplica'
    ) AS referencia_anterior,
    COALESCE(
        GROUP_CONCAT(
            DISTINCT e.expediente_madre
            ORDER BY e.expediente_madre
        ),
        'Sin expediente madre'
    ) AS expediente_madre,
    -- Datos de la consulta
    c.id AS consulta_id,
    c.exp_id,
    c.historia_clinica,
    c.fecha_consulta,
    c.hora,
    c.fecha_recepcion,
    c.fecha_egreso,
    c.tipo_consulta,
    c.estatus
FROM
    pacientes p
    JOIN expedientes e ON p.id = e.paciente_id -- Relación entre pacientes y expedientes
    LEFT JOIN consultas c ON e.id = c.exp_id -- Relación entre expedientes y consultas
GROUP BY
    p.id,
    c.id;

CREATE or REPLACE VIEW consulta_rapida AS
SELECT id AS consulta_id,
exp_id,
historia_clinica,
fecha_consulta, 
hora, 
fecha_recepcion, 
fecha_egreso, 
tipo_consulta, 
estatus,
paciente_id 
FROM consultas;