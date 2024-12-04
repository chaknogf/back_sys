from sqlalchemy import create_engine, MetaData, Table, select, insert, update, func
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

# Conexión a las bases de datos
old_engine = create_engine("mysql+pymysql://root:Prometeus.0@localhost:3306/test_api")
new_engine = create_engine("mysql+pymysql://admin_user:turbo@localhost:3309/pluton")

old_session = sessionmaker(bind=old_engine)()
new_session = sessionmaker(bind=new_engine)()

# MetaData para tablas
old_metadata = MetaData()
new_metadata = MetaData()

# Tablas de la base antigua
old_pacientes = Table("nuevapaciente", old_metadata, autoload_with=old_engine)
old_consultas = Table("nuevaconsulta", old_metadata, autoload_with=old_engine)
old_expedientes = Table("nuevaexpediente", old_metadata, autoload_with=old_engine)
old_citas = Table("nuevacitas", old_metadata, autoload_with=old_engine)

# Tablas de la base nueva
new_pacientes = Table("pacientes", new_metadata, autoload_with=new_engine)
referencia_contacto = Table("referencia_contacto", new_metadata, autoload_with=new_engine)
contacto_paciente = Table("contacto_paciente", new_metadata, autoload_with=new_engine)
new_expedientes = Table("expedientes", new_metadata, autoload_with=new_engine)
new_consultas = Table("consultas", new_metadata, autoload_with=new_engine)
new_citas = Table("citas", new_metadata, autoload_with=new_engine, autoload_replace=False)


# Función para dividir los números de teléfono
def split_phone_number(phone_number):
    phone_number = str(phone_number).strip()
    telefono1 = phone_number[:8] if len(phone_number) >= 9 else phone_number
    telefono2 = phone_number[9:18] if len(phone_number) >= 18 else None
    telefono3 = phone_number[18:30] if len(phone_number) >= 30 else None
    return telefono1, telefono2, telefono3

# Funciones de migración
def migrate_pacientes(old_pacientes_list, paciente_mapping):
    for old_paciente in tqdm(old_pacientes_list, desc="Migrando pacientes", unit="paciente"):
        try:
            with new_session.begin():  # Transacción independiente
                # Preparar datos del paciente
                paciente_data = {
                    "id": old_paciente.id,
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

                # Insertar paciente
                paciente_result = new_session.execute(insert(new_pacientes).values(paciente_data))
                new_paciente_id = paciente_result.inserted_primary_key[0]  # ID insertado
                

                # Insertar en referencia_contacto
                if hasattr(old_paciente, "responsable") and old_paciente.responsable:
                    referencia_data = {
                        "paciente_id": new_paciente_id,
                        "nombre_contacto": old_paciente.responsable,
                        "telefono_contacto": old_paciente.telefono_responsable,
                        "parentesco_id": old_paciente.parentesco,
                    }
                    new_session.execute(insert(referencia_contacto).values(referencia_data))

                # Insertar en contacto_paciente
                telefono1, telefono2, telefono3 = split_phone_number(old_paciente.telefono)
                contacto_data = {
                    "paciente_id": new_paciente_id,
                    "direccion": old_paciente.direccion,
                    "telefono1": telefono1,
                    "telefono2": telefono2,
                    "telefono3": telefono3,
                    "email": old_paciente.email,
                }
                new_session.execute(insert(contacto_paciente).values(contacto_data))
 
               
        except Exception as e:
            print(f"Error al migrar paciente {new_pacientes.id}: {e}")
            
def migrate_expedientes(old_expedientes_list, expediente_mapping):
        for old_expediente in tqdm(old_expedientes_list, desc="Migrando expedientes y emergencias", unit="expedientes"):
            try:
                with new_session.begin():  # Transacción independiente
                    
                    # Insertar en expedientes
                    expediente_data = {
                        "id": old_expediente.id,
                        "paciente_id": old_expediente.paciente_id,
                        "expediente": old_expediente.expediente,
                        "hoja_emergencia": old_expediente.hoja_emergencia,
                        "referencia_anterior": old_expediente.exp_ref,
                        "expediente_madre": old_expediente.exp_madre,
                        "created_at": old_expediente.created_at,
                    }
                    new_session.execute(insert(new_expedientes).values(expediente_data))
                    
            except Exception as e:
                print(f"Error al migrar consulta {old_expedientes}: {e}")


def migrate_consultas(old_consultas_list, consulta_mapping):
    for old_consulta in tqdm(old_consultas_list, desc="Migrando consultas", unit="consulta"):
        try:
            with new_session.begin():  # Transacción independiente
                

                # Preparar datos de consulta
                consultas_data = {
                    "id": old_consulta.id,
                    "exp_id": old_consulta.consulta_id,
                    "fecha_consulta": old_consulta.fecha_consulta,
                    "hora": old_consulta.hora,
                    "fecha_recepcion": old_consulta.recepcion,
                    "fecha_egreso": old_consulta.egreso,
                    "tipo_consulta": old_consulta.tipo_consulta,
                    "especialidad": None if old_consulta.especialidad == 0 else old_consulta.especialidad,
                    "servicio": None if old_consulta.servicio == 0 else old_consulta.servicio,
                    "diagnostico": old_consulta.diagnostico,
                    "folios": old_consulta.folios,
                    "nota": f"{old_consulta.medico or ''} {old_consulta.nota or ''}".strip(),
                    "estatus": old_consulta.status,
                    "create_user": old_consulta.created_by,
                    "created_at": old_consulta.created_at,
                    "updated_at": old_consulta.updated_at,
                    "lactancia": 'S' if old_consulta.lactancia == 1 else 'N' if old_consulta.lactancia == 0 else None,
                    "prenatal": old_consulta.prenatal,
                }
                # Insertar consulta
                new_session.execute(insert(new_consultas).values(consultas_data))
        except Exception as e:
                print(f"Error al migrar consulta {old_consulta.id}: {e}")
                
def migrate_citas(old_citas_list, citas_mapping=None):
    from sqlalchemy.dialects.mysql import insert  # Usar dialecto correcto si es necesario

    for old_cita in tqdm(old_citas_list, desc="Migrando citas", unit="cita"):
        try:
            with new_session.begin():  # Transacción independiente
                # Preparar datos de citas
                citas_data = {
                    "id": old_cita.id,
                    "paciente_id": old_cita.paciente_id,
                    "especialidad": old_cita.especialidad,
                    "fecha_cita": old_cita.fecha,
                    "tipo_cita": old_cita.tipo,
                    "nota": old_cita.nota,
                    "created_at": old_cita.created_at,
                    "updated_at": old_cita.updated_at,
                    "created_by": old_cita.created_by,
                }

                # # Validar datos
                # if not all([citas_data["id"], citas_data["paciente_id"], citas_data["fecha_cita"]]):
                #     print(f"Datos incompletos para cita {old_cita.id}. Saltando...")
                #     continue

                # Insertar cita
                new_session.execute(insert(new_citas).values(citas_data))
        except Exception as e:
            print(f"Error al migrar cita {old_cita.id if old_cita.id else 'desconocida'}: {e}")
                


# Migración
try:
    paciente_mapping = {}
    consulta_mapping = {}
    expediente_mapping = {}
    citas_mapping = {}
    old_pacientes_list = old_session.execute(select(old_pacientes)).fetchall()
    old_expedientes_list = old_session.execute(select(old_expedientes)).fetchall()
    old_consultas_list = old_session.execute(select(old_consultas)).fetchall()
    old_citas_list = old_session.execute(select(old_citas)).fetchall()
   

    migrate_pacientes(old_pacientes_list, paciente_mapping)
    migrate_expedientes(old_expedientes_list, expediente_mapping)
    migrate_consultas(old_consultas_list, consulta_mapping)
    migrate_citas( old_citas_list, citas_mapping)
   
    
    

    print("Migración completada.")
except Exception as e:
    print(f"Error general en el proceso de migración: {e}")