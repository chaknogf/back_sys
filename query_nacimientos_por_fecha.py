from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # nacimientos_legacy con fecha (fecha de nacimiento)
    result = conn.execute(
        text("""
            SELECT
                EXTRACT(MONTH FROM fecha)::int AS mes,
                COUNT(*) AS total
            FROM nacimientos_legacy
            WHERE EXTRACT(YEAR FROM fecha) = 2026
              AND EXTRACT(MONTH FROM fecha) BETWEEN 1 AND 5
            GROUP BY EXTRACT(MONTH FROM fecha)
            ORDER BY mes
        """)
    ).fetchall()
    print("nacimientos_legacy por fecha:")
    for row in result:
        print(f"  Mes {row[0]}: {row[1]}")

    # constancia_nacimiento con fecha_registro
    result = conn.execute(
        text("""
            SELECT
                EXTRACT(MONTH FROM fecha_registro)::int AS mes,
                COUNT(*) AS total
            FROM constancia_nacimiento
            WHERE EXTRACT(YEAR FROM fecha_registro) = 2026
              AND EXTRACT(MONTH FROM fecha_registro) BETWEEN 1 AND 5
            GROUP BY EXTRACT(MONTH FROM fecha_registro)
            ORDER BY mes
        """)
    ).fetchall()
    print("constancia_nacimiento por fecha_registro:")
    for row in result:
        print(f"  Mes {row[0]}: {row[1]}")
