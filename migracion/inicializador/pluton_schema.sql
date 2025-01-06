CREATE TABLE pacientes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) DEFAULT NULL,
    apellido VARCHAR(100) DEFAULT NULL,
    dpi BIGINT DEFAULT NULL,
    pasaporte VARCHAR(50) DEFAULT NULL,
    sexo ENUM('M', 'F') DEFAULT 'M',
    nacimiento DATE,
    defuncion DATE DEFAULT NULL,
    tiempo_defuncion TIME DEFAULT NULL,
    nacionalidad_iso VARCHAR(3) DEFAULT NULL,
    lugar_nacimiento CHAR(4) DEFAULT NULL,
    estado_civil INT DEFAULT NULL,
    educacion INT DEFAULT NULL,
    pueblo INT DEFAULT NULL,
    idioma INT DEFAULT NULL,
    ocupacion VARCHAR(50) DEFAULT NULL,
    estado ENUM('V', 'M') DEFAULT 'V',
    gemelo INT DEFAULT NULL,
    padre VARCHAR(100) DEFAULT NULL,
    madre VARCHAR(100) DEFAULT NULL,
    conyugue VARCHAR(100) DEFAULT NULL,
    direccion VARCHAR(150) DEFAULT NULL,
    municipio VARCHAR(4) DEFAULT NULL,
    telefono1 VARCHAR(10) DEFAULT NULL,
    telefono2 VARCHAR(10) DEFAULT NULL,
    telefono3 VARCHAR(15) DEFAULT NULL,
    email VARCHAR(150) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (nacionalidad_iso) REFERENCES nacionalidades (iso),
    FOREIGN KEY (lugar_nacimiento) REFERENCES depto_muni (codigo),
    FOREIGN KEY (estado_civil) REFERENCES estados_civiles (id),
    FOREIGN KEY (educacion) REFERENCES educacion (id),
    FOREIGN KEY (pueblo) REFERENCES pueblos (id),
    FOREIGN KEY (idioma) REFERENCES idiomas (id),
    INDEX idx_pacientes_nacionalidad_iso (nacionalidad_iso),
    INDEX idx_pacientes_lugar_nacimiento (lugar_nacimiento),
    INDEX idx_pacientes_estado_civil (estado_civil),
    INDEX idx_pacientes_educacion (educacion),
    INDEX idx_pacientes_pueblo (pueblo),
    INDEX idx_pacientes_idioma (idioma)
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE referencia_contacto (
    id INT PRIMARY KEY AUTO_INCREMENT,
    paciente_id INT,
    nombre_contacto VARCHAR(100) NOT NULL,
    telefono_contacto VARCHAR(10),
    parentesco_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
    FOREIGN KEY (parentesco_id) REFERENCES parentescos (id)
) ENGINE = InnoDB CHARSET = utf8mb4;

SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) DEFAULT NULL,
    dpi BIGINT UNIQUE DEFAULT NULL,
    contraseña VARCHAR(255) DEFAULT NULL,
    rol INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rol) REFERENCES roles (id)
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE madres (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT NOT NULL,
    vecindad VARCHAR(4) DEFAULT NULL,
    hijos INT DEFAULT 0,
    vivos INT DEFAULT 0,
    muertos INT DEFAULT 0,
    edad INT DEFAULT NULL,
    FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
    INDEX idx_madres_paciente (id)
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE medicos (
    id INT NOT NULL PRIMARY KEY,
    colegiado INT NOT NULL UNIQUE,
    nombre VARCHAR(200) DEFAULT NULL,
    dpi BIGINT DEFAULT NULL,
    especialidad INT DEFAULT NULL,
    pasaporte VARCHAR(30) DEFAULT NULL,
    sexo ENUM('M', 'F') DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_medicos_especialidad FOREIGN KEY (especialidad) REFERENCES especialidad (id)
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE recien_nacidos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT NOT NULL,
    hora TIME DEFAULT NULL,
    peso_libras INT DEFAULT NULL,
    peso_onzas INT DEFAULT NULL,
    tipo_parto INT DEFAULT NULL,
    clase_parto INT DEFAULT NULL,
    FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
    FOREIGN KEY (tipo_parto) REFERENCES tipos_parto (id),
    FOREIGN KEY (clase_parto) REFERENCES clases_parto (id),
    UNIQUE INDEX idx_recien_nacido_paciente (paciente_id)
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE constancias_nacimiento (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    doc VARCHAR(15) DEFAULT NULL UNIQUE,
    madre INT NOT NULL,
    recien_nacido INT NOT NULL,
    usuario INT NOT NULL,
    medico INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_const_nac_madre (madre),
    INDEX idx_const_nac_recien_nacido (recien_nacido),
    INDEX idx_const_nac_medico (medico)
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE expedientes (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT,
    expediente VARCHAR(15) UNIQUE DEFAULT NULL,
    hoja_emergencia VARCHAR(15) UNIQUE DEFAULT NULL,
    referencia_anterior VARCHAR(11) DEFAULT NULL,
    expediente_madre VARCHAR(11) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
    INDEX idx_expedientes_paciente (id)
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE consultas (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    exp_id INT DEFAULT NULL,
    paciente_id INT DEFAULT NULL,
    historia_clinica VARCHAR(15) DEFAULT NULL,
    fecha_consulta DATE DEFAULT NULL,
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
    medico INT DEFAULT NULL,
    nota TEXT DEFAULT NULL,
    estatus INT DEFAULT NULL,
    lactancia VARCHAR(1) DEFAULT NULL,
    prenatal INT DEFAULT NULL,
    create_user VARCHAR(50) DEFAULT NULL,
    update_user VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    grupo_edad INT DEFAULT NULL,
    FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
    FOREIGN KEY (tipo_lesion) REFERENCES tipo_lesion (id),
    FOREIGN KEY (especialidad) REFERENCES especialidad (id),
    FOREIGN KEY (tipo_consulta) REFERENCES tipo_consulta (id),
    FOREIGN KEY (servicio) REFERENCES servicios (id),
    FOREIGN KEY (grupo_edad) REFERENCES grupo_edad (id),
    FOREIGN KEY (estatus) REFERENCES estatus (id),
    INDEX idx_consultas_exp_id (exp_id),
    INDEX idx_consulta_paciente (id),
    INDEX idx_consultas_fecha_consulta (fecha_consulta),
    INDEX idx_consultas_tipo_consulta (tipo_consulta)
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE citas (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT DEFAULT NULL,
    especialidad INT DEFAULT NULL,
    fecha_cita DATE DEFAULT NULL,
    tipo_cita INT DEFAULT NULL,
    doble_fecha ENUM('S', 'N') DEFAULT 'N',
    laboratorio VARCHAR(50) DEFAULT NULL,
    fecha_laboratorio DATE DEFAULT NULL,
    nota TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(8) DEFAULT NULL,
    FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (especialidad) REFERENCES especialidad (id),
    FOREIGN KEY (tipo_cita) REFERENCES tipo_citas (id),
    INDEX idx_citas_paciente_id (paciente_id),
    INDEX idx_citas_especialidad (especialidad),
    INDEX idx_citas_tipo_cita (tipo_cita)
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE proce_medicos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    fecha DATE DEFAULT NULL,
    servicio_id INT DEFAULT NULL,
    sexo ENUM('M', 'F') DEFAULT NULL,
    codigo_procedimiento_id INT NOT NULL,
    especialidad_id INT DEFAULT NULL,
    cantidad INT DEFAULT NULL,
    medico_id INT DEFAULT NULL,
    grupo_edad ENUM('N', 'A') DEFAULT NULL,
    created_by VARCHAR(10) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (servicio_id) REFERENCES servicios (id),
    FOREIGN KEY (codigo_procedimiento_id) REFERENCES codigo_procedimientos (id),
    FOREIGN KEY (especialidad_id) REFERENCES especialidad (id),
    FOREIGN KEY (medico_id) REFERENCES medicos (colegiado),
    INDEX idx_proce_medicos_servicio (servicio_id),
    INDEX idx_proce_medicos_codigo (codigo_procedimiento_id),
    INDEX idx_proce_medicos_especialidad (especialidad_id),
    INDEX idx_proce_medicos_medico (medico_id)
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE uisau (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    consulta_id INT NOT NULL,
    estado_salud_id INT NOT NULL,
    situacion_salud_id INT NOT NULL,
    lugar_referencia_id INT NOT NULL,
    fecha_referencia DATE DEFAULT NULL,
    fecha_contacto DATE DEFAULT NULL,
    hora_contacto TIME DEFAULT NULL,
    estadia SMALLINT DEFAULT NULL,
    cama_numero SMALLINT DEFAULT NULL,
    informacion ENUM('S', 'N') DEFAULT NULL,
    nombre_contacto VARCHAR(150) DEFAULT NULL,
    parentesco_id INT DEFAULT NULL,
    telefono VARCHAR(15) DEFAULT NULL,
    nota TEXT DEFAULT NULL,
    estudios VARCHAR(230) DEFAULT NULL,
    evolucion TEXT DEFAULT NULL,
    recetado_por ENUM('S', 'N') DEFAULT NULL,
    shampoo BOOLEAN DEFAULT FALSE,
    toalla BOOLEAN DEFAULT FALSE,
    peine BOOLEAN DEFAULT FALSE,
    jabon BOOLEAN DEFAULT FALSE,
    cepillo_dientes BOOLEAN DEFAULT FALSE,
    pasta_dental BOOLEAN DEFAULT FALSE,
    sandalias BOOLEAN DEFAULT FALSE,
    agua BOOLEAN DEFAULT FALSE,
    papel BOOLEAN DEFAULT FALSE,
    panales BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(50) DEFAULT NULL,
    update_by VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (consulta_id) REFERENCES consultas (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (estado_salud_id) REFERENCES estados_salud (id),
    FOREIGN KEY (situacion_salud_id) REFERENCES situaciones_salud (id),
    FOREIGN KEY (lugar_referencia_id) REFERENCES lugares_referencia (id),
    FOREIGN KEY (parentesco_id) REFERENCES parentescos (id),
    INDEX idx_uisau_consulta_id (consulta_id),
    INDEX idx_uisau_estado_salud_id (estado_salud_id),
    INDEX idx_uisau_situacion_salud_id (situacion_salud_id),
    INDEX idx_uisau_lugar_referencia_id (lugar_referencia_id),
    INDEX idx_uisau_parentesco_id (parentesco_id)
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE cie10 (
    cod VARCHAR(7) NOT NULL PRIMARY KEY,
    grupo CHAR(1) DEFAULT NULL,
    dx VARCHAR(250) NOT NULL,
    abreviatura VARCHAR(10) DEFAULT NULL,
    especialidad_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (especialidad_id) REFERENCES especialidad (id),
    INDEX idx_cie10_grupo (grupo),
    INDEX idx_cie10_especialidad (especialidad_id)
) ENGINE = InnoDB CHARSET = utf8mb4;

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

-- Índice compuesto en la tabla `pacientes` para optimizar orden y búsqueda por ID y created_at
CREATE INDEX idx_pacientes_id_created_at ON pacientes (id, created_at);

-- Índice básico en `expedientes.paciente_id` para mejorar el JOIN con `pacientes`
CREATE INDEX idx_expedientes_paciente_id ON expedientes (paciente_id);

-- Índice compuesto en `consultas` para optimizar búsquedas por `exp_id` y consultas por fecha
CREATE INDEX idx_consultas_exp_id_created_at ON consultas (exp_id, fecha_consulta);

-- Índice compuesto adicional en `pacientes` para consultas frecuentes y ordenación
CREATE INDEX idx_pacientes_optimizado ON pacientes (created_at, nombre, apellido, sexo);

-- Índices opcionales para mejorar operaciones de agregación en `expedientes`
CREATE INDEX idx_expedientes_expediente ON expedientes (expediente);
CREATE INDEX idx_expedientes_referencia ON expedientes (referencia_anterior);
CREATE INDEX idx_expedientes_expediente_madre ON expedientes (expediente_madre);