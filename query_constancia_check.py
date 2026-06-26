from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT MIN(created_at), MAX(created_at), COUNT(*) FROM constancia_nacimiento")
    ).fetchall()
    for row in result:
        print(row)

    result = conn.execute(
        text("SELECT MIN(fecha_registro), MAX(fecha_registro), COUNT(*) FROM constancia_nacimiento")
    ).fetchall()
    for row in result:
        print(row)
