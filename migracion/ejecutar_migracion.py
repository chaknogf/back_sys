import subprocess
import os

# Lista de scripts a ejecutar
scripts = [
    "migracionPrevia/predata_1.py",
    "migracionPrevia/clearNacimientos.py",
    "migracionPrevia/predata_2.py",
    "inicializador/make_pluton2.py",
    "inicializador/migraCopy2.py"
]

for script in scripts:
    if not os.path.exists(script):
        print(f"El archivo {script} no existe. Saltando...")
        continue
    print(f"Ejecutando {script}...")
    subprocess.run(["python", script], check=True)
    print(f"Finalizó {script}\n")