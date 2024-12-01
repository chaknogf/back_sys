from sqlalchemy import create_engine, MetaData, Table, select, insert
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

# Conexión a la base de datos antigua y nueva
old_engine = create_engine("mysql+pymysql://root:Prometeus.0@localhost:3306/test_api")
new_engine = create_engine("mysql+pymysql://admin_user:turbo@localhost:3309/pluton")

old_session = sessionmaker(bind=old_engine)()
new_session = sessionmaker(bind=new_engine)()

# MetaData para tablas
old_metadata = MetaData()
new_metadata = MetaData()

# Tablas de la base antigua
old_pacientes = Table("vista_d_p_c", old_metadata, autoload_with=old_engine)
old_consultas = Table("vista_d_c", old_metadata, autoload_with=old_engine)

# Tablas de la base nueva
new_pacientes = Table("pacientes", new_metadata, autoload_with=new_engine)
new_expedientes = Table("expedientes", new_metadata, autoload_with=new_engine)
referencia_contacto = Table("referencia_contacto", new_metadata, autoload_with=new_engine)
contacto_paciente = Table("contacto_paciente", new_metadata, autoload_with=new_engine)
new_consultas = Table("consultas", new_metadata, autoload_with=new_engine)
new_emergencias = Table("emergencias", new_metadata, autoload_with=new_engine)

# Función para dividir los números de teléfono
def split_phone_number(phone_number):
    phone_number = str(phone_number).strip()
    telefono1 = phone_number[:10] if len(phone_number) >= 10 else phone_number
    telefono2 = phone_number[10:20] if len(phone_number) >= 20 else None
    telefono3 = phone_number[20:30] if len(phone_number) >= 30 else None
    return telefono1, telefono2, telefono3

# Intentar migrar los datos
try:
    # Obtener todos los pacientes y consultas de la base de datos antigua
    old_pacientes_list = old_session.execute(select(old_pacientes)).fetchall()
    old_consultas_list = old_session.execute(select(old_consultas)).fetchall()

    total_pacientes = len(old_pacientes_list)
    total_consultas = len(old_consultas_list)

    paciente_mapping = {}  # Diccionario para mapear IDs antiguos a nuevos

    # Migrar pacientes
    for old_paciente in tqdm(old_pacientes_list, desc="Migrando pacientes", unit="paciente", total=total_pacientes):
        with new_session.begin():  # Transacción independiente para cada inserción
            # Preparar los datos del paciente
            paciente_data = {
                "nombre": old_paciente.nombre.strip() if old_paciente.nombre else None,
                "apellido": old_paciente.apellido.strip() if old_paciente.apellido else None,
                "dpi": old_paciente.dpi if old_paciente.dpi != 0 else None,
                "pasaporte": old_paciente.pasaporte,
                "sexo": old_paciente.sexo if old_paciente.sexo else None,
                "nacimiento": old_paciente.nacimiento,
                "estado": old_paciente.estado,
                "padre": old_paciente.padre,
                "madre": old_paciente.madre,
                "conyugue": old_paciente.conyugue,
                "created_at": old_paciente.created_at,
                "lugar_nacimiento": old_paciente.lugar_nacimiento if old_paciente.lugar_nacimiento else None,
                "defuncion": old_paciente.defuncion,
                "nacionalidad_iso": 'GTM' if old_paciente.nacionalidad == 1 else None,
                "estado_civil_id": old_paciente.estado_civil,
                "educacion_id": old_paciente.educacion,
                "pueblo_id": old_paciente.pueblo,
                "idioma_id": old_paciente.idioma,
                "ocupacion": old_paciente.ocupacion,
            }

            # Insertar en `pacientes`
            paciente_result = new_session.execute(insert(new_pacientes).values(paciente_data))
            new_paciente_id = paciente_result.inserted_primary_key[0]  # ID insertado
            paciente_mapping[old_paciente.id] = new_paciente_id  # Mapear ID antiguo a nuevo

            # Insertar en `referencia_contacto`
            if hasattr(old_paciente, "responsable") and old_paciente.responsable:
                referencia_data = {
                    "id_paciente": new_paciente_id,
                    "nombre_contacto": old_paciente.responsable,
                    "telefono_contacto": old_paciente.telefono_responsable,
                    "parentesco_id": old_paciente.parentesco,
                }
                new_session.execute(insert(referencia_contacto).values(referencia_data))

            # Insertar en `contacto_paciente`
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

            # Insertar en `expedientes`
            expediente_data = {
                "expediente": old_paciente.expediente,
                "id_paciente": new_paciente_id,
                "referencia_anterior": old_paciente.exp_ref,
                "expediente_madre": old_paciente.exp_madre,
            }
            new_session.execute(insert(new_expedientes).values(expediente_data))

    # Migrar consultas
    for old_consulta in tqdm(old_consultas_list, desc="Migrando consultas", unit="consulta", total=total_consultas):
        with new_session.begin():  # Transacción independiente para cada inserción
            id_paciente_nuevo = paciente_mapping.get(old_consulta.id_paciente)
            if not id_paciente_nuevo:
                print(f"Consulta ignorada: No se encontró un nuevo ID para el paciente {old_consulta.id_paciente}")
                continue

            # Preparar los datos de la consulta
            consultas_data = {
                "id_paciente": id_paciente_nuevo,
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

            # Insertar en `consultas`
            new_session.execute(insert(new_consultas).values(consultas_data))

            # Preparar los datos de emergencias
            emergencias_data = {
                "id_paciente": id_paciente_nuevo,
                "hoja_emergencia": old_consulta.hoja_emergencia,
                "created_at": old_consulta.created_at,
                "updated_at": old_consulta.updated_at,
            }

            # Insertar en `emergencias`
            new_session.execute(insert(new_emergencias).values(emergencias_data))

    print("Migración completada.")
except Exception as e:
    new_session.rollback()  # En caso de error, deshacer los cambios
    print(f"Ocurrió un error: {e}")