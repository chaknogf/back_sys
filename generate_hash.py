# generate_hash.py
from core.security import pwd_context

if __name__ == "__main__":
    import getpass
    password = getpass.getpass("Nueva contraseña: ")
    nuevo_hash = pwd_context.hash(password)
    print("\nHash CORRECTO y 100% compatible (copia esto):\n")
    print(nuevo_hash)
    print("\n")