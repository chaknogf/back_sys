DROP TABLE IF EXISTS union_old,
noemergencia,
siemergencia,
nuevaexpediente,
nuevaconsulta,
nuevapaciente,
pacientesUnicos,
xxx,
old_consultas,
old_pacientes,
temp_duplicados,
nuevacitas,
nuevamedicos,
nuevausuario,
nuevarn,
temp_union_old,
sin_rn,
filtro_rn,
listado_pacientes,
expedientes,
consultas_pacientes,
sin_expedientes,
union_old_clean;

CREATE TABLE union_old (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    expediente INT DEFAULT NULL,
    nombre VARCHAR(50) DEFAULT NULL,
    apellido VARCHAR(50) DEFAULT NULL,
    nombre_completo VARCHAR(150) DEFAULT NULL,
    sexo VARCHAR(2) DEFAULT NULL,
    dpi VARCHAR(20) DEFAULT NULL,
    nacimiento DATE DEFAULT NULL,
    direccion VARCHAR(100) DEFAULT NULL,
    telefono VARCHAR(50) DEFAULT NULL,
    responsable VARCHAR(50) DEFAULT NULL,
    parentesco VARCHAR(19) DEFAULT NULL,
    paciente_id VARCHAR(50) DEFAULT NULL,
    pasaporte VARCHAR(50) DEFAULT NULL,
    nacionalidad VARCHAR(3) DEFAULT NULL,
    lugar_nacimiento VARCHAR(4) DEFAULT NULL,
    estado_civil INT DEFAULT NULL,
    educacion INT DEFAULT NULL,
    pueblo INT DEFAULT NULL,
    idioma INT DEFAULT NULL,
    ocupacion VARCHAR(50) DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL,
    padre VARCHAR(50) DEFAULT NULL,
    madre VARCHAR(50) DEFAULT NULL,
    dpi_responsable BIGINT DEFAULT NULL,
    telefono_responsable VARCHAR(18) DEFAULT NULL,
    estado VARCHAR(2) DEFAULT NULL,
    exp_madre VARCHAR(20) DEFAULT NULL,
    gemelo VARCHAR(2) DEFAULT NULL,
    conyugue VARCHAR(100) DEFAULT NULL,
    defuncion VARCHAR(10) DEFAULT NULL,
    exp_ref INT DEFAULT NULL,
    updated_at DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT NULL,
    created_by VARCHAR(11) DEFAULT NULL,
    consulta_id INT DEFAULT NULL,
    hoja_emergencia VARCHAR(15) DEFAULT NULL,
    fecha_consulta DATE DEFAULT NULL,
    hora TIME DEFAULT NULL,
    edad VARCHAR(200) DEFAULT NULL,
    nota TEXT NULL,
    especialidad INT DEFAULT NULL,
    servicio INT DEFAULT NULL,
    status INT DEFAULT NULL,
    egreso DATETIME DEFAULT NULL,
    recepcion DATETIME DEFAULT NULL,
    tipo_consulta INT DEFAULT NULL,
    prenatal INT DEFAULT NULL,
    lactancia VARCHAR(2) DEFAULT NULL,
    diagnostico VARCHAR(100) DEFAULT NULL,
    folios VARCHAR(25) DEFAULT NULL,
    medico VARCHAR(100) DEFAULT NULL,
    consulta_por INT DEFAULT NULL,
    archivado_por VARCHAR(10) DEFAULT NULL,
    expediente_id INT DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE xxx LIKE union_old;

CREATE TABLE expedientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    expediente VARCHAR(15) UNIQUE DEFAULT NULL,
    hoja_emergencia VARCHAR(15) UNIQUE DEFAULT NULL,
    paciente_id INT DEFAULT NULL,
    consulta_id INT DEFAULT NULL,
    exp_madre INT DEFAULT NULL,
    created_at DATETIME DEFAULT NULL,
    exp_ref INT DEFAULT NULL,
    user_crated VARCHAR(15) DEFAULT NULL,
    nombre_completo VARCHAR(125) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE consultas_pacientes (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT DEFAULT NULL,
    expediente_id INT DEFAULT NULL,
    nombre_completo VARCHAR(200) DEFAULT NULL,
    nacimiento DATE DEFAULT null,
    fecha_consulta DATE DEFAULT NULL,
    historia_clinica VARCHAR(15) DEFAULT NULL,
    hora TIME DEFAULT NULL,
    fecha_recepcion DATETIME DEFAULT NULL,
    fecha_egreso DATETIME DEFAULT NULL,
    tipo_consulta INT DEFAULT NULL,
    tipo_lesion INT DEFAULT NULL,
    estancia INT DEFAULT NULL,
    especialidad INT DEFAULT NULL,
    servicio INT DEFAULT NULL,
    fallecido VARCHAR(1) DEFAULT NULL,
    referido VARCHAR(1) DEFAULT NULL,
    contraindicado VARCHAR(1) DEFAULT NULL,
    diagnostico VARCHAR(100) DEFAULT NULL,
    folios INT DEFAULT NULL,
    medico VARCHAR(50) DEFAULT NULL,
    nota TEXT DEFAULT NULL,
    estatus INT DEFAULT NULL,
    lactancia VARCHAR(1) DEFAULT NULL,
    prenatal INT DEFAULT NULL,
    created_by VARCHAR(50) DEFAULT NULL,
    updated_by VARCHAR(50) DEFAULT NULL,
    created_at DATETIME DEFAULT NULL,
    updated_at DATETIME DEFAULT NULL,
    grupo_edad INT DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE listado_pacientes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) DEFAULT NULL,
    apellido VARCHAR(100) DEFAULT NULL,
    nombre_completo VARCHAR(200) DEFAULT NULL,
    dpi BIGINT DEFAULT NULL,
    pasaporte VARCHAR(50) DEFAULT NULL,
    sexo VARCHAR(2) DEFAULT NULL,
    nacimiento DATE DEFAULT NULL,
    defuncion DATE DEFAULT NULL,
    hora_defuncion TIME DEFAULT NULL,
    nacionalidad VARCHAR(3) DEFAULT NULL,
    lugar_nacimiento CHAR(4) DEFAULT NULL,
    estado_civil INT DEFAULT NULL,
    educacion INT DEFAULT NULL,
    pueblo INT DEFAULT NULL,
    idioma INT DEFAULT NULL,
    ocupacion VARCHAR(50) DEFAULT NULL,
    estado VARCHAR(2) DEFAULT NULL,
    gemelo INT DEFAULT NULL,
    padre VARCHAR(100) DEFAULT NULL,
    madre VARCHAR(100) DEFAULT NULL,
    direccion VARCHAR(200) DEFAULT NULL,
    municipio INT DEFAULT NULL,
    telefono VARCHAR(30) DEFAULT NULL,
    tel_contacto VARCHAR(10) DEFAULT NULL,
    conyugue VARCHAR(100) DEFAULT NULL,
    user_created VARCHAR(20) DEFAULT NULL,
    created_at DATETIME DEFAULT NULL,
    updated_at DATETIME DEFAULT NULL,
    exp_madre INT DEFAULT NULL,
    exp_ref INT DEFAULT NULL,
    expediente VARCHAR(10) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE Table sin_expedientes AS
SELECT *
FROM consultas
WHERE
    expediente IS NULL
    AND hoja_emergencia IS NULL;

CREATE TABLE nuevacitas (
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT DEFAULT NULL,
    expediente INT DEFAULT NULL,
    especialidad INT DEFAULT NULL,
    fecha DATE DEFAULT NULL,
    nota TEXT DEFAULT NULL,
    tipo INT DEFAULT NULL,
    lab INT DEFAULT NULL,
    fecha_lab DATE DEFAULT NULL,
    created_at DATETIME DEFAULT NULL,
    updated_at DATETIME DEFAULT NULL,
    created_by VARCHAR(8) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE nuevausuario (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL,
    contraseña VARCHAR(255) DEFAULT NULL,
    dpi BIGINT UNIQUE DEFAULT NULL,
    rol INT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE nuevamedicos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    colegiado INT NOT NULL,
    nombre VARCHAR(200) DEFAULT NULL,
    dpi BIGINT DEFAULT NULL,
    especialidad INT DEFAULT NULL,
    pasaporte VARCHAR(30) DEFAULT NULL,
    sexo ENUM('M', 'F') DEFAULT NULL,
    created_at DATETIME,
    updated_at DATETIME
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE nuevarn (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    fecha DATE DEFAULT NULL,
    cor INT DEFAULT NULL,
    ao INT DEFAULT NULL,
    doc VARCHAR(12) DEFAULT NULL UNIQUE,
    fecha_parto DATE DEFAULT NULL,
    madre VARCHAR(100) DEFAULT NULL,
    madre_id INT DEFAULT NULL,
    rn_id INT DEFAULT NULL,
    dpi BIGINT DEFAULT NULL,
    passport VARCHAR(30) DEFAULT NULL,
    libro INT DEFAULT NULL,
    folio INT DEFAULT NULL,
    partida VARCHAR(20) DEFAULT NULL,
    depto INT DEFAULT NULL,
    muni INT DEFAULT NULL,
    edad INT DEFAULT NULL,
    vecindad INT DEFAULT NULL,
    sexo_rn VARCHAR(1) DEFAULT NULL,
    lb INT DEFAULT NULL,
    onz INT DEFAULT NULL,
    hora TIME DEFAULT NULL,
    medico VARCHAR(200) DEFAULT NULL,
    colegiado INT DEFAULT NULL,
    dpi_medico BIGINT DEFAULT NULL,
    hijos INT DEFAULT NULL,
    vivos INT DEFAULT NULL,
    muertos INT DEFAULT NULL,
    tipo_parto INT DEFAULT NULL,
    clase_parto INT DEFAULT NULL,
    certifica VARCHAR(200) DEFAULT NULL,
    usuario_id INT DEFAULT NULL,
    create_by VARCHAR(10) NULL,
    expediente INT DEFAULT NULL,
    nacionalidad VARCHAR(25) DEFAULT NULL,
    pais VARCHAR(25) DEFAULT NULL,
    created_at DATETIME,
    updated_at DATETIME
) ENGINE = InnoDB CHARSET = utf8mb4;