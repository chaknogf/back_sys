from sqlalchemy import create_engine, text
from tqdm import tqdm
import os

# Configura tu conexión a la base de datos
DATABASE_URI = "mysql+pymysql://root:Prometeus.0@localhost:3306/test_api"

# Ruta al archivo SQL
base_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(base_dir, "script.sql")
if os.path.exists(sql_file_path):
    print("¡El archivo existe!")
else:
    print(f"Archivo no encontrado en la ruta: {sql_file_path}")

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

    # Eliminar saltos de línea y comentarios de una forma más robusta
    commands = sql_content.split(";")

    # Filtrar los comandos vacíos y comentarios
    commands = [command.strip() for command in commands if command.strip() and not command.strip().startswith("--")]

    # Imprimir los comandos para depuración
    # print("Comandos procesados:")
    # for command in commands:
    #     print(command)
    
    # Devolver la lista de comandos sin caracteres innecesarios al inicio o final
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

if __name__ == "__main__":
    sql_commands = load_and_filter_sql(sql_file_path)
    execute_sql_commands(sql_commands)
    