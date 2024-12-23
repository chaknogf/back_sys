from sqlalchemy import create_engine
import pandas as pd
import re
from datetime import timedelta
from sqlalchemy import text

# Configura tu conexión a la base de datos
DATABASE_URI = "mysql+pymysql://root:Prometeus.0@localhost:3306/test_api"

# Conexión a la base de datos
engine = create_engine(DATABASE_URI)

# Conectar y ejecutar la consulta
with engine.connect() as connection:
    result = connection.execute('SELECT * FROM union_old')

    # Puedes iterar sobre el resultado, que es un objeto de tipo ResultProxy
    data = result.fetchall()

# Ahora puedes manipular 'data', que es una lista de tuplas
# Puedes convertirlo a un DataFrame si es necesario para más operaciones
df = pd.DataFrame(data, columns=result.keys())

# Función para calcular la edad en años
def calcular_edad(edad):
    if pd.isnull(edad) or edad.strip() == '':
        return None
    edad = edad.lower()
    try:
        if edad.isdigit():  # Solo números
            return int(edad)
        if re.match(r'^\d+\s*a$', edad):  # Formato "XX A" o "XX años"
            return int(re.search(r'\d+', edad).group())
        if re.match(r'^\d+\s*m$', edad):  # Formato "XX M" o meses
            meses = int(re.search(r'\d+', edad).group())
            return round(meses / 12, 2)
        match = re.match(r'(?P<años>\d+)\s*años?\s*(?P<meses>\d+)?\s*meses?', edad)  # Formato completo
        if match:
            años = int(match.group('años'))
            meses = int(match.group('meses')) if match.group('meses') else 0
            return round(años + meses / 12, 2)
    except Exception as e:
        print(f"Error procesando la edad: {edad}. Error: {e}")
    return None

# Aplicar la función a la columna de edad
df['edad_anos'] = df['edad'].apply(calcular_edad)

# Calcular el nacimiento para los casos donde esté vacío
def calcular_nacimiento(row):
    if pd.isnull(row['nacimiento']) and not pd.isnull(row['fecha_consulta']) and not pd.isnull(row['edad_anos']):
        return (pd.to_datetime(row['fecha_consulta']) - timedelta(days=int(row['edad_anos'] * 365.25))).strftime('%Y-%m-%d')
    return row['nacimiento']

df['nacimiento'] = df.apply(calcular_nacimiento, axis=1)

with engine.begin() as connection:
    for index, row in df.iterrows():
        nacimiento = row['nacimiento'] if not pd.isnull(row['nacimiento']) else None
        edad_anos = row['edad_anos'] if not pd.isnull(row['edad_anos']) else None
        connection.execute(
            text("""
            UPDATE union_old
            SET nacimiento = :nacimiento, edad = :edad
            WHERE id = :id
            """),
            {"nacimiento": nacimiento, "edad": edad_anos, "id": row['id']}
        )

print("Datos transformados y actualizados correctamente.")  