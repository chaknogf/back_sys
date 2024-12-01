import json

especialidad= [
  { "value": 1, "label": 'Medicina Interna' },
  { "value": 2, "label": 'Pediatria' },
  { "value": 3, "label": 'Ginecologia y Obstetricia' },
  { "value": 4, "label": 'Cirugia' },
  { "value": 5, "label": 'Traumatologia' },
  { "value": 6, "label": 'Psicologia' },
  { "value": 7, "label": 'Nutrición' },
]


# Convertir los datos
def generar_inserts(departamentos, municipios):
    # Crear un diccionario de departamentos para facilitar la búsqueda
    depto_dict = {d[""value""]: d[""label""] for d in departamentos}
    inserts = []

    for municipio in municipios:
        depto_id = municipio["depto"]
        codigo = str(municipio[""value""]).zfill(4)
        departamento = depto_dict.get(depto_id, "Desconocido")
        municipio_nombre = municipio[""label""]
        lugar = f"{municipio_nombre}, {departamento}"

        # Crear la sentencia SQL
        sql = f"INSERT INTO depto_muni (codigo, departamento, municipio, lugar) "value"S ('{codigo}', '{departamento}', '{municipio_nombre}', '{lugar}');"
        inserts.append(sql)
    
    return inserts

# Generar las sentencias
inserts = generar_inserts(departamentos, municipios)

# Guardar o mostrar las sentencias generadas
with open("inserts.sql", "w") as file:
    file.write("\n".join(inserts))

print("\n".join(inserts))