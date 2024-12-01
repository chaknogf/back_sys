from sqlalchemy import create_engine, text
from tqdm import tqdm
import os

# Configura tu conexión a la base de datos
DATABASE_URI = "mysql+pymysql://admin_user:turbo@localhost:3309/pluton" 

# Ruta al directorio de archivos SQL
base_dir = os.path.dirname(os.path.abspath(__file__))

# Lista de archivos SQL en el orden deseado
sql_files = ["normalizados.sql", "pluton_schema.sql", "inserts.sql"]

# Conexión a la base de datos
engine = create_engine(DATABASE_URI)

def load_and_filter_sql(file_path):
    """
    Lee un archivo SQL y lo divide en comandos.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as file:
        # Leer todo el contenido del archivo y dividir por ";"
        sql_content = file.read()

    # Dividir en comandos y filtrar vacíos o comentarios
    commands = [command.strip() for command in sql_content.split(";") if command.strip() and not command.strip().startswith("--")]
    
    return commands

def execute_sql_commands(commands):
    """
    Ejecuta una lista de comandos SQL con tqdm.
    """
    with engine.connect() as connection:
        for command in tqdm(commands, desc="Ejecutando comandos SQL"):
            try:
                connection.execute(text(command))
            except Exception as e:
                print(f"Error ejecutando el comando: {command}\n{e}")
        
        # Commit explícito después de la ejecución
        connection.commit()

if __name__ == "__main__":
    for sql_file in sql_files:
        sql_file_path = os.path.join(base_dir, sql_file)
        if os.path.exists(sql_file_path):
            print(f"Procesando archivo: {sql_file}")
            sql_commands = load_and_filter_sql(sql_file_path)
            execute_sql_commands(sql_commands)
        else:
            print(f"Archivo no encontrado: {sql_file}")
