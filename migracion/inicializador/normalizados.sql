SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS parentescos,
pueblos,
idiomas,
nacionalidades,
depto_muni,
estados_civiles,
educacion,
roles,
permisos,
tipos_parto,
clases_parto,
tipo_lesion,
especialidad,
grupo_edad,
servicios,
tipos_cita,
codigo_procedimientos,
estados_salud,
situaciones_salud,
lugares_referencia,
estadia_es,
servio_es,
tipo_consulta,
estudios,
estatus,
pacientes,
referencia_contacto,
contacto_paciente,
usuarios,
madres,
medicos,
recien_nacidos,
constancias_nacimiento,
expedientes,
consultas,
citas,
proce_medicos,
uisau,
cie10,
tipo_citas;

CREATE TABLE IF NOT EXISTS parentescos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE pueblos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE idiomas (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE nacionalidades (
    iso VARCHAR(3) PRIMARY KEY,
    nacionalidad VARCHAR(50) DEFAULT NULL,
    pais VARCHAR(50) DEFAULT NULL,
    cti INT(3) DEFAULT NULL,
    idioma VARCHAR(30) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE depto_muni (
    codigo CHAR(4) PRIMARY KEY,
    departamento VARCHAR(100) NOT NULL,
    municipio VARCHAR(100) NOT NULL,
    lugar VARCHAR(255) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE estados_civiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) UNIQUE NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE educacion (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nivel VARCHAR(50) UNIQUE NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT DEFAULT NULL,
    permisos VARCHAR(250) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE permisos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE tipos_parto (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(50) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE clases_parto (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(50) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE tipo_lesion (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE especialidad (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    especialista VARCHAR(100) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE grupo_edad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo VARCHAR(50) NOT NULL,
    edad_inicio INT NOT NULL,
    edad_fin INT,
    caracteristicas TEXT
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE servicios (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE codigo_procedimientos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    abreviatura VARCHAR(10) NOT NULL,
    procedimiento VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE estados_salud (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE situaciones_salud (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE lugares_referencia (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE estadia_es (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(50) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE servio_es (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE tipo_consulta (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE estudios (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE estatus (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(50) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE tipo_citas (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

SET FOREIGN_KEY_CHECKS = 0;