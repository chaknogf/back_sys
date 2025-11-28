# generate_hash.py
from app.database.security import pwd_context

if __name__ == "__main__":
    password = "admin"  # Cambia si quieres otra contraseña
    nuevo_hash = pwd_context.hash(password)
    print("\nHash CORRECTO y 100% compatible (copia esto):\n")
    print(nuevo_hash)
    print("\n")