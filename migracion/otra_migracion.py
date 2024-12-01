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
old_consultas = Table("nuevaconsulta", old_metadata, autoload_with=old_engine)
old_expedientes = Table("jee", old_metadata, autoload_with=old_engine)

# Tablas de la base nueva

new_expedientes = Table("expedientes", new_metadata, autoload_with=new_engine)
new_consultas = Table("consultas", new_metadata, autoload_with=new_engine)

def migrate_consultas(old_consultas_list, consulta_mapping):
    for old_consulta in tqdm(old_consultas_list, desc="Migrando consultas", unit="consulta"):
        try:
            with new_session.begin():  # Transacción independiente
                

                # Preparar datos de consulta
                consultas_data = {
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
                # Insertar consulta
                new_session.execute(insert(new_consultas).values(consultas_data))
        except Exception as e:
                print(f"Error al migrar consulta {old_consulta.id}: {e}")
                
def migrate_expedientes(old_expedientes_list, expediente_mapping):
    for old_consulta in tqdm(old_expedientes_list, desc="Migrando consultas", unit="expedientes y emergencias"):
        try:
            with new_session.begin():  # Transacción independiente
                
                 # Insertar en expedientes
                expediente_data = {
                    "paciente_id": old_expedientes.paciente_id,
                    "expediente": old_expedientes.expediente,
                    "hoja_emergencia": old_expedientes.hoja_emergencia,
                    "referencia_anterior": old_expedientes.exp_ref,
                    "expediente_madre": old_expedientes.exp_madre,
                    "created_at": old_expedientes.created_at,
                }
                new_session.execute(insert(new_expedientes).values(expediente_data))
                
        except Exception as e:
            print(f"Error al migrar consulta {old_expedientes.id}: {e}")

# Migración
try:
    paciente_mapping = {}
    consulta_mapping = {}
    expediente_mapping = {}
    old_pacientes_list = old_session.execute(select(old_pacientes)).fetchall()
    old_consultas_list = old_session.execute(select(old_consultas)).fetchall()
    old_expedientes_list = old_session.execute(select(old_expedientes)).fetchall()

    migrate_pacientes(old_pacientes_list, paciente_mapping)
    migrate_consultas(old_consultas_list, consulta_mapping)
    migrate_expedientes(old_expedientes_list, expediente_mapping)
    
    

    print("Migración completada.")
except Exception as e:
    print(f"Error general en el proceso de migración: {e}")