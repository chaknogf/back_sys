from sqlalchemy import create_engine
import pandas as pd
from tqdm import tqdm

# Configuración del motor de base de datos
engine = create_engine("mysql+pymysql://root:Prometeus.0@localhost:3306/test_api")

# Consulta SQL
query = "SELECT * FROM union_old"  # Reemplaza "nombre_tabla" con el nombre real de tu tabla

# Leer datos de la base de datos
try:
    print("Cargando datos desde la base de datos...")
    # Usar raw_connection() para obtener una conexión DBAPI2 compatible
    with engine.raw_connection() as connection:
        df = pd.read_sql(query, con=connection)
    print(f"Datos cargados: {len(df)} registros encontrados.")
except Exception as e:
    print(f"Error al cargar los datos: {e}")
    exit(1)  # Salir si ocurre un error

# Función para fusionar duplicados
def fusionar_duplicados(grupo):
    # Combina filas con la misma clave agrupando columnas relevantes
    grupo_sorted = grupo.sort_values(by="ultima_actualizacion", ascending=False)  # Ordenar por la columna deseada
    return grupo_sorted.iloc[0]  # Conserva solo la fila más reciente

# Procesar duplicados con tqdm para ver progreso
try:
    print("Procesando duplicados...")
    tqdm.pandas()  # Habilitar barra de progreso para pandas
    df_cleaned = (
        df.sort_values("ultima_actualizacion", ascending=False)  # Ajustar columna si es necesario
        .groupby(["expediente", "nombre_completo", "nacimiento", "gemelo"], as_index=False)
        .progress_apply(fusionar_duplicados)
    )
except Exception as e:
    print(f"Error al procesar los duplicados: {e}")
    exit(1)  # Salir si ocurre un error

# Eliminar índices innecesarios (si aplica)
df_cleaned.reset_index(drop=True, inplace=True)

# Guardar el resultado en una nueva tabla
output_table_name = "nombre_tabla_limpia"  # Cambia al nombre que desees para la nueva tabla
try:
    print(f"Guardando datos limpios en la tabla '{output_table_name}'...")
   