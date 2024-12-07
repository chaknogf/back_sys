CREATE VIEW vi_paciente AS
SELECT
    p.id,
    p.nombre,
    p.apellido,
    p.dpi,
    p.pasaporte,
    p.sexo,
    p.nacimiento,
    p.defuncion,
    p.tiempo_defuncion,
    p.nacionalidad_iso,
    n.nacionalidad AS nacionalidad,
    p.lugar_nacimiento,
    dm.lugar,
    p.estado_civil,
    ec.nombre AS e_civil,
    p.educacion,
    e.nivel AS nivel_educacion,
    p.pueblo,
    pu.nombre AS pueblo_,
    p.idioma,
    i.nombre AS idioma_,
    p.ocupacion,
    p.estado,
    p.padre,
    p.madre,
    p.conyugue,
    p.created_at,
    p.updated_at,
    cp.direccion,
    cp.telefono1,
    cp.telefono2,
    cp.telefono3,
    cp.email,
    rc.nombre_contacto,
    rc.telefono_contacto,
    rc.parentesco_id,
    pa.nombre AS parentesco_nombre
FROM
    pacientes p
    LEFT JOIN contacto_paciente cp ON p.id = cp.paciente_id
    LEFT JOIN referencia_contacto rc ON p.id = rc.paciente_id
    LEFT JOIN nacionalidades n ON p.nacionalidad_iso = n.iso
    LEFT JOIN depto_muni dm ON p.lugar_nacimiento = dm.codigo
    LEFT JOIN estados_civiles ec ON p.estado_civil = ec.id
    LEFT JOIN educacion e ON p.educacion = e.id
    LEFT JOIN pueblos pu ON p.pueblo = pu.id
    LEFT JOIN idiomas i ON p.idioma = i.id
    LEFT JOIN parentescos pa ON rc.parentesco_id = pa.id;

CREATE VIEW card_paciente AS
SELECT
    p.id AS paciente_id,
    p.nombre,
    p.apellido,
    p.dpi,
    p.sexo,
    p.nacimiento,
    p.defuncion,
    p.estado,
    cp.direccion,
    cp.telefono1,
    cp.telefono2,
    cp.telefono3,
    cp.email,
    e.id AS expediente_id,
    e.expediente,
    e.hoja_emergencia,
    e.referencia_anterior,
    e.expediente_madre,
    p.created_at AS paciente_created_at,
    p.updated_at AS paciente_updated_at,
    cp.created_at AS contacto_created_at,
    cp.updated_at AS contacto_updated_at,
    e.created_at AS expediente_created_at,
    e.updated_at AS expediente_updated_at
FROM
    pacientes p
    LEFT JOIN contacto_paciente cp ON p.id = cp.paciente_id
    LEFT JOIN expedientes e ON p.id = e.paciente_id;