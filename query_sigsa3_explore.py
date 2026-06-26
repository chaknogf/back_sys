from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # First check what distinct especialidad values exist
    result = conn.execute(
        text("SELECT DISTINCT especialidad FROM sigsa3 WHERE especialidad ILIKE '%terapia%' OR especialidad ILIKE '%respiratoria%'")
    ).fetchall()
    print("Especialidades que contienen terapia/respiratoria:")
    for row in result:
        print(f"  '{row[0]}'")

    result = conn.execute(
        text("SELECT DISTINCT tipo_consulta FROM sigsa3 ORDER BY tipo_consulta")
    ).fetchall()
    print("\nTipos de consulta disponibles:")
    for row in result:
        print(f"  '{row[0]}'")
