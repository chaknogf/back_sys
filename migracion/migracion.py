from sqlalchemy import create_engine, MetaData, Table, select, insert, update, func
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
import logging

# Configuración de logging para registrar errores
logging.basicConfig(filename='migration_errors.log', level=logging.ERROR)

# Función para registrar errores
def log_error(msg):
    logging.error(msg)
    print(msg)

# Conexión a las bases de datos
old_engine = create_engine("mysql+pymysql://root:Prometeus.0@localhost:3306/test_api")
new_engine = create_engine("mysql+pymysql://admin_user:turbo@localhost:3309/pluton")

old_session = sessionmaker(bind=old_engine)()
new_session = sessionmaker(bind=new_engine)()

# MetaData para tablas
old_metadata = MetaData()
new_metadata = MetaData()

# Tablas de la base antigua
old_pacientes = Table("vista_d_p_c", old_metadata, autoload_with=old_engine)
old_consultas = Table("nuevaconsulta", old_metadata, autoload_with=old_engine)
old_expedientes = Table("jee", old_metadata, autoload_with=old_engine)

# Tablas de la base nueva
new_pacientes = Table("pacientes", new_metadata, autoload_with=new_engine)
new_expedientes = Table("expedientes", new_metadata, autoload_with=new_engine)
referencia_contacto = Table("referencia_contacto", new_metadata, autoload_with=new_engine)
contacto_paciente = Table("contacto_paciente", new_metadata, autoload_with=new_engine)
new_consultas = Table("consultas", new_metadata, autoload_with=new_engine)


# Función para dividir los números de teléfono
def split_phone_number(phone_number):
    phone_number = str(phone_number).strip()
    telefono1 = phone_number[:8] if len(phone_number) >= 9 else phone_number
    telefono2 = phone_number[9:18] if len(phone_number) >= 18 else None
    telefono3 = phone_number[18:30] if len(phone_number) >= 30 else None
    return telefono1, telefono2, telefono3


# Función para paginar las consultas
def paginate_query(query, batch_size=1000):
    offset = 0
    while True:
        results = old_session.execute(query.limit(batch_size).offset(offset)).fetchall()
        if not results:
            break
        yield results
        offset += batch_size


# Funciones de migración
def migrate_pacientes(old_pacientes_list):
    pacientes_data = []
    for old_paciente in tqdm(old_pacientes_list, desc="Migrando pacientes", unit="paciente"):
        try:
            # Preparar datos del paciente
            paciente_data = {
                "nombre": old_paciente.nombre,
                "apellido": old_paciente.apellido,
                "dpi": old_paciente.dpi if old_paciente.dpi != 0 else None,
                "pasaporte": old_paciente.pasaporte,
                "sexo": old_paciente.sexo if old_paciente.sexo else None,
                "nacimiento": old_paciente.nacimiento,
                "estado": old_paciente.estado,
                "padre": old_paciente.padre,
                "madre": old_paciente.madre,
                "conyugue": old_paciente.conyugue,
                "created_at": old_paciente.created_at,
                "lugar_nacimiento": old_paciente.lugar_nacimiento[:4] if old_paciente.lugar_nacimiento else None,
                "defuncion": None if not old_paciente.defuncion or old_paciente.defuncion == '' else old_paciente.defuncion,
                "nacionalidad_iso": 'GTM' if old_paciente.nacionalidad == 1 else None,
                "estado_civil": None if old_paciente.estado_civil == 0 else old_paciente.estado_civil,
                "educacion": None if old_paciente.educacion == 0 else old_paciente.educacion,
                "pueblo": None if old_paciente.pueblo == 0 else old_paciente.pueblo,
                "idioma": None if old_paciente.idioma == 0 else old_paciente.idioma,
                "ocupacion": old_paciente.ocupacion,
            }
            pacientes_data.append(paciente_data)
            
            # Insertar en batch si acumulamos suficientes registros
            if len(pacientes_data) >= 1000:
                batch_insert(new_pacientes, pacientes_data)
                pacientes_data = []  # Limpiar lista

        except Exception as e:
            log_error(f"Error al migrar paciente {old_paciente.id}: {e}")
    
    # Insertar cualquier remanente
    if pacientes_data:
        batch_insert(new_pacientes, pacientes_data)


def batch_insert(table, data):
    try:
        new_session.execute(insert(table), data)
    except Exception as e:
        log_error(f"Error en batch insert: {e}")


def migrate_consultas(old_consultas_list):
    for old_consulta in tqdm(old_consultas_list, desc="Migrando consultas", unit="consulta"):
        try:
            # Preparar datos de consulta
            consulta_data = {
                "paciente_id": old_consulta.paciente_id,
                "expediente": old_consulta.expediente,
                "hoja_emergencia": old_consulta.hoja_emergencia,
                "fecha_consulta": old_consulta.fecha_consulta,
                "hora": old_consulta.hora,
                "fecha_recepcion": old_consulta.recepcion,
                "fecha_egreso": old_consulta.egreso,
                "tipo_consulta": old_consulta.tipo_consulta,
                "especialidad_id": old_consulta.especialidad,
                "servicio_id": old_consulta.servicio,
                "diagnostico": old_consulta.diagnostico,
                "folios": old_consulta.folios,
                "nota": f"{old_consulta.medico or ''} {old_consulta.nota or ''}".strip(),
                "estatus": old_consulta.status,
                "create_user": old_consulta.created_by,
                "created_at": old_consulta.created_at,
                "updated_at": old_consulta.updated_at,
                "lactancia": old_consulta.lactancia,
                "prenatal": 'S' if old_consulta.prenatal == 1 else None,
            }
            new_session.execute(insert(new_consultas).values(consulta_data))

        except Exception as e:
            log_error(f"Error al migrar consulta {old_consulta.id}: {e}")


def migrate_expedientes(old_expedientes_list):
    for old_expediente in tqdm(old_expedientes_list, desc="Migrando expedientes", unit="expediente"):
        try:
            # Preparar datos de expediente
            expediente_data = {
                "paciente_id": old_expediente.paciente_id,
                "expediente": old_expediente.expediente,
                "hoja_emergencia": old_expediente.hoja_emergencia,
                "referencia_anterior": old_expediente.exp_ref,
                "expediente_madre": old_expediente.exp_madre,
                "created_at": old_expediente.created_at,
            }
            new_session.execute(insert(new_expedientes).values(expediente_data))

        except Exception as e:
            log_error(f"Error al migrar expediente {old_expediente.id}: {e}")


# Migración
try:
    old_pacientes_list = paginate_query(select(old_pacientes))
    for old_pacientes_batch in old_pacientes_list:
        migrate_pacientes(old_pacientes_batch)

    old_consultas_list = paginate_query(select(old_consultas))
    for old_consultas_batch in old_consultas_list:
        migrate_consultas(old_consultas_batch)

    old_expedientes_list = paginate_query(select(old_expedientes))
    for old_expedientes_batch in old_expedientes_list:
        migrate_expedientes(old_expedientes_batch)

    print("Migración completada.")
except Exception as e:
    log_error(f"Error general en el proceso de migración: {e}")