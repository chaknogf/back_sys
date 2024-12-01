CREATE VIEW vista_pacientes_contacto AS
SELECT
    p.id_paciente,
    CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo,
    p.dpi,
    p.pasaporte,
    p.sexo,
    p.nacimiento,
    p.defuncion,
    p.tiempo_defuncion,
    p.ocupacion,
    c.direccion,
    c.telefono1,
    c.telefono2,
    c.telefono3,
    c.email
FROM
    pacientes p
    LEFT JOIN contacto_paciente c ON p.id_paciente = c.paciente_id;

CREATE VIEW vista_medicos AS
SELECT
    m.id,
    CONCAT(m.name, ' ', m.dpi) AS nombre_completo,
    m.colegiado,
    m.pasaporte,
    m.sexo,
    e.nombre AS especialidad
FROM medicos m
    LEFT JOIN especialidad e ON m.especialidad_id = e.id;

CREATE VIEW vista_consultas AS
SELECT
    c.id AS consulta_id,
    c.id_paciente,
    c.id_expediente,
    c.id_hoja_emergencia,
    CONCAT(
        'expediente: ',
        e.numero_expediente,
        ' - emergencia: ',
        em.hoja_emergencia
    ) AS historia_clinica,
    c.fecha_consulta,
    c.hora,
    c.fecha_recepcion,
    c.fecha_egreso,
    c.tipo_consulta,
    c.tipo_lesion_id,
    c.estancia,
    c.especialidad_id,
    c.servicio_id,
    c.fallecido,
    c.referido,
    c.contraindicado,
    c.diagnostico,
    c.folios,
    c.id_medico,
    c.nota,
    c.estatus,
    c.create_user,
    c.update_user,
    c.created_at,
    c.updated_at
FROM
    consultas c
    JOIN expedientes e ON c.id_expediente = e.id_paciente
    JOIN emergencias em ON c.id_hoja_emergencia = em.id_paciente;

CREATE VIEW vista_citas AS
SELECT
    c.id,
    CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo,
    c.fecha_cita,
    c.nota,
    t.tipo AS tipo_cita,
    e.nombre AS especialidad_nombre
FROM
    citas c
    JOIN pacientes p ON c.expediente = p.id_paciente
    JOIN tipos_cita t ON c.tipo_cita_id = t.id
    JOIN especialidad e ON c.especialidad_id = e.id;

CREATE VIEW vista_uisau AS
SELECT
    u.id,
    CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo,
    s.nombre AS estado_salud,
    ss.nombre AS situacion_salud,
    lr.nombre AS lugar_referencia,
    u.fecha_referencia,
    u.fecha_contacto,
    u.hora_contacto,
    u.estadia,
    u.cama,
    u.informacion,
    u.contacto,
    u.telefono
FROM
    uisau u
    JOIN consultas c ON u.consulta_id = c.id
    JOIN pacientes p ON c.id_paciente = p.id_paciente
    JOIN estados_salud s ON u.estado_id = s.id
    JOIN situaciones_salud ss ON u.situacion_id = ss.id
    JOIN lugares_referencia lr ON u.lugar_referencia_id = lr.id;

CREATE VIEW vista_paciente_completo AS
SELECT
    p.id_paciente,
    CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo, -- Nombre completo concatenado
    p.dpi,
    p.pasaporte,
    p.sexo,
    p.nacimiento,
    p.defuncion,
    p.tiempo_defuncion,
    p.nacionalidad_id,
    p.depto_nac_id,
    p.lugar_nacimiento_id,
    p.estado_civil_id,
    p.educacion_id,
    p.pueblo_id,
    p.idioma_id,
    p.ocupacion,
    p.estado,
    p.created_at,
    p.updated_at,
    -- Datos de contacto_paciente
    cp.direccion,
    cp.telefono1,
    cp.telefono2,
    cp.telefono3,
    cp.email,
    cp.parentesco_id,
FROM
    pacientes p
    -- Relación con la tabla contacto_paciente
    LEFT JOIN contacto_paciente cp ON p.id_paciente = cp.paciente_id;

CREATE VIEW vista_detalles_consultas AS
SELECT
    c.id_paciente,
    e.numero_expediente AS expediente,
    em.hoja_emergencia AS hoja_emergencia,
    c.fecha AS fecha_consulta,
    c.hora AS hora_consulta,
    c.estatus AS estado_consulta,
    c.tipo AS tipo_consulta
FROM
    consultas c
    LEFT JOIN expedientes e ON c.id_expediente = e.id_expediente
    LEFT JOIN emergencias em ON c.id_emergencia = em.id_emergencia;

CREATE VIEW vista_historias_clinicas AS
SELECT p.id_paciente, CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo, vc.detalles_consultas
FROM
    pacientes p
    LEFT JOIN vista_detalles_consultas vc ON vc.id_paciente = p.id_paciente;

CREATE VIEW vista_referencias_contacto AS
SELECT
    r.id AS id_referencia,
    r.id_paciente,
    CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo,
    r.nombre_contacto,
    r.telefono_contacto,
    pr.descripcion AS parentesco,
    r.created_at AS referencia_created_at,
    r.updated_at AS referencia_updated_at
FROM
    referencia_contacto r
    JOIN pacientes p ON r.id_paciente = p.id_paciente
    JOIN parentescos pr ON r.parentesco_id = pr.id;