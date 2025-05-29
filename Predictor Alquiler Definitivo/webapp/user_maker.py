from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import bcrypt
from settings.db_connection import get_engine
from settings.models import Usuario

engine = get_engine()
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Funcion para crear un usuario
def crear_usuario(nombre, password, es_admin=False):
    db = SessionLocal()
    try:
        # Encriptar el password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Crear instancia del usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            password_hash=hashed_password,
            es_admin=es_admin
        )

        # Añadir y guardar en la BD
        db.add(nuevo_usuario)
        db.commit()
        print(f"Usuario '{nombre}' creado exitosamente.")
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        db.rollback()
    finally:
        db.close()

# Ejecucion
if __name__ == "__main__":
    nombre = input("Introduce el nombre de usuario: ")
    password = input("Introduce la contraseña: ")
    admin_input = input("¿Es administrador? (s/n): ").lower()
    es_admin = True if admin_input == 's' else False

    crear_usuario(nombre, password, es_admin)
