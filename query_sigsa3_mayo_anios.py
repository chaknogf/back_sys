from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    for anio in [2024, 2025]:
        result = conn.execute(
            text("""
                SELECT
                    tipo_consulta,
                    COUNT(*) AS total
                FROM sigsa3
                WHERE especialidad = 'Terapia Respiratoria'
                  AND EXTRACT(YEAR FROM fecha_consulta) = :anio
                  AND EXTRACT(MONTH FROM fecha_consulta) = 5
                GROUP BY tipo_consulta
                ORDER BY tipo_consulta
            """),
            {"anio": anio}
        ).fetchall()
        print(f"\nMayo {anio}:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
