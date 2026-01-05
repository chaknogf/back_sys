

Tpacientes = ('''
    CREATE TABLE `pacientes` (
  `id` int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `expediente` int UNIQUE DEFAULT NULL,
  `nombre` varchar(50) DEFAULT NULL,
  `apellido` varchar(50) DEFAULT NULL,
  `dpi` bigint DEFAULT NULL,
  `pasaporte` varchar(50) DEFAULT NULL,
  `sexo` varchar(2) DEFAULT NULL,
  `nacimiento` date DEFAULT NULL,
  `nacionalidad` int DEFAULT NULL,
  `depto_nac` int DEFAULT NULL,
  `lugar_nacimiento` int DEFAULT NULL,
  `estado_civil` int DEFAULT NULL,
  `educacion` int DEFAULT NULL,
  `pueblo` int DEFAULT NULL,
  `idioma` int DEFAULT NULL,
  `ocupacion` varchar(50) DEFAULT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `municipio` int DEFAULT NULL,
  `depto` int DEFAULT NULL,
  `telefono` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `padre` varchar(50) DEFAULT NULL,
  `madre` varchar(50) DEFAULT NULL,
  `responsable` varchar(50) DEFAULT NULL,
  `parentesco` int DEFAULT NULL,
  `dpi_responsable` bigint DEFAULT NULL,
  `telefono_responsable` int DEFAULT NULL,
  `estado` varchar(2) DEFAULT NULL,
  `exp_madre` int DEFAULT NULL,
  `gemelo` varchar(2) DEFAULT NULL,
  `conyugue` VARCHAR(100) DEFAULT NULL,
  `created_by` varchar(8) DEFAULT NULL,
  `fechaDefuncion` varchar(10) DEFAULT NULL,
  `hora_defuncion` time DEFAULT NULL,
  `exp_ref` int DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `expediente_unico` (`expediente`)
) ENGINE=InnoDB AUTO_INCREMENT=72879 DEFAULT CHARSET=utf8mb4 
''')



# Definición del modelo de datos
class PacienteModel(Base):
    __tablename__ = "pacientes"
    
    id = Column(Integer, primary_key=True) 
    expediente = Column(Integer)
    nombre = Column(String(50), index=True)
    apellido = Column(String(50), index=True)
    dpi = Column(Integer)
    pasaporte = Column(String(50))
    sexo = Column(String(2))
    nacimiento = Column(Date)
    nacionalidad = Column(Integer)
    depto_nac = Column(Integer)
    lugar_nacimiento = Column(Integer)
    estado_civil = Column(Integer)
    educacion = Column(Integer)
    pueblo= Column(Integer)
    idioma = Column(Integer)
    ocupacion = Column(String(50))
    municipio = Column(Integer)
    depto = Column(Integer)
    direccion = Column(String(100))
    telefono = Column(String(50))
    email = Column(String(100))
    padre = Column(String(50))
    madre = Column(String(50))
    responsable = Column(String(50))
    parentesco = Column(Integer)
    dpi_responsable = Column(Integer)
    telefono_responsable = Column(Integer)
    estado = Column(String(2))
    exp_madre = Column(Integer)
    created_by = Column(String(8))
    fechaDefuncion = Column(String(10))
    hora_defuncion = Column(Time)
    gemelo = Column(String(2))
    conyugue = Column(String(100))
    exp_ref = Column(Integer)


Tconsultas = ('''
  CREATE TABLE `consultas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hoja_emergencia` varchar(15) DEFAULT NULL,
  `expediente` int DEFAULT NULL,
  `fecha_consulta` date DEFAULT NULL,
  `hora` time DEFAULT NULL,
  `nombres` varchar(50) DEFAULT NULL,
  `apellidos` varchar(50) DEFAULT NULL,
  `nacimiento` date DEFAULT NULL,
  `edad` varchar(25) DEFAULT NULL,
  `sexo` varchar(1) DEFAULT NULL,
  `dpi` varchar(20) DEFAULT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `acompa` varchar(50) DEFAULT NULL,
  `parente` int DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `nota` varchar(200) DEFAULT NULL,
  `especialidad` int DEFAULT NULL,
  `servicio` int DEFAULT NULL,
  `status` int DEFAULT NULL,
  `fecha_egreso` date DEFAULT NULL,
  `fecha_recepcion` datetime DEFAULT NULL,
  `tipo_consulta` int DEFAULT NULL,
  `prenatal` int DEFAULT NULL,
  `lactancia` int DEFAULT NULL,
  `dx` varchar(100) DEFAULT NULL,
  `folios` int DEFAULT NULL,
  `medico` varchar(25) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `archived_by` varchar(8) DEFAULT NULL,
  `created_by` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hoja_emergencia` (`hoja_emergencia`),
  KEY `expediente` (`expediente`),
  CONSTRAINT `consultas_ibfk_1` FOREIGN KEY (`expediente`) REFERENCES `pacientes` (`expediente`)
             )   ENGINE=InnoDB CHARSET=utf8mb4
               ''')


            
            
#Definición del modelo de datos
class ConsultasModel(Base):
    __tablename__ = "consultas"
    
    id = Column(Integer, primary_key=True)
    hoja_emergencia = Column(String(12))
    expediente = Column(Integer, ForeignKey('pacientes.expediente'))
    fecha_consulta = Column(Date)
    hora = Column(Time)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    nacimiento = Column(Date)
    edad = Column(String(25))
    sexo = Column(String(1))
    dpi = Column(String(20))
    direccion = Column(String(100))
    acompa = Column(String(50))
    parente = Column(Integer)
    telefono = Column(String)
    nota = Column(String(200))
    especialidad = Column(Integer)
    servicio = Column(Integer)
    status = Column(Integer)
    fecha_egreso = Column(Date)
    fecha_recepcion = Column(DateTime)
    tipo_consulta = Column(Integer)
    prenatal = Column(Integer)
    lactancia = Column(Integer)
    dx = Column(String(100))
    folios = Column(Integer)
    medico = Column(String(25))
    archived_by = Column(String(8))
    created_by = Column(String(8))
    created_at = Column(String(25))
    updated_at = Column(String(25))
    bomberos = Column(Boolean)
    transito = Column(Boolean)
    arma_blanca = Column(Boolean)
    arma_fuego = Column(Boolean)
    estudiante_publica = Column(Boolean)
    accidente_laboral = Column(Boolean)
    personal_hospital = Column(Boolean)
    reserva = Column(Boolean)
    
 
Tcons_nac = ('''
             CREATE TABLE cons_nac (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `fecha` DATE DEFAULT NULL,
    `cor` INT DEFAULT NULL,
    `ao` INT DEFAULT NULL,
    `doc` VARCHAR(12) DEFAULT NULL UNIQUE,
    `fecha_parto` DATE DEFAULT NULL,  
    `madre` VARCHAR(100) DEFAULT NULL,
    `dpi` BIGINT DEFAULT NULL,
    `passport` VARCHAR(30) DEFAULT NULL,
    `libro` INT DEFAULT NULL,
    `folio` INT DEFAULT NULL,
    `partida` VARCHAR(10) DEFAULT NULL,
    `depto` INT DEFAULT NULL,    
    `muni` INT DEFAULT NULL,
    `edad` INT DEFAULT NULL,
    `vecindad` INT DEFAULT NULL,
    `sexo_rn` VARCHAR(1) DEFAULT NULL,
    `lb` INT DEFAULT NULL,
    `onz` INT DEFAULT NULL,
    `hora` TIME DEFAULT NULL,
    `medico` VARCHAR(200) DEFAULT NULL, 
    `colegiado` INT DEFAULT NULL,
    `dpi_medico` BIGINT DEFAULT NULL,
    `hijos` INT DEFAULT NULL,
    `vivos` INT DEFAULT NULL,
    `muertos` INT DEFAULT NULL,
    `tipo_parto` INT DEFAULT NULL,
    `clase_parto` INT DEFAULT NULL,
    `certifica` VARCHAR(200) DEFAULT NULL,
    `create_by` VARCHAR(10) NULL,
    `expediente` INT DEFAULT NULL,
    `nacionalidad` VARCHAR(25) DEFAULT NULL,
    `pais` VARCHAR(25) DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARSET=utf8mb4
             ''')


#Definición del modelo de datos            
class Cons_NacModel(Base):
    __tablename__ = "cons_nac"
    id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    cor = Column(Integer)
    ao = Column(Integer)
    doc = Column(String(12))
    fecha_parto = Column(Date)
    madre = Column(String(100))
    dpi = Column(BigInteger)
    passport = Column(String(30))
    libro = Column(Integer)
    folio = Column(Integer)
    partida = Column(String(10))
    depto = Column(Integer)
    muni = Column(Integer)
    edad = Column(Integer)
    vecindad = Column(Integer)
    sexo_rn = Column(String(1))
    lb = Column(Integer)
    onz = Column(Integer)
    hora = Column(Time)
    medico = Column(String(200))
    colegiado = Column(Integer)
    dpi_medico = Column(BigInteger)
    hijos = Column(Integer)
    vivos = Column(Integer)
    muertos = Column(Integer)
    tipo_parto = Column(Integer)
    clase_parto = Column(Integer)
    certifica = Column(String(200))
    create_by = Column(String(10))
    expediente = Column(Integer)
    nacionalidad = Column(String(25))
    pais = Column(String(25))
    
    
     
   