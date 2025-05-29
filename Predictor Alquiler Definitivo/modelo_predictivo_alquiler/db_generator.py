import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from logger import LoggerConfig

# Crear logger
logger_config = LoggerConfig(log_filename="log_db_generator.log")
logger = logger_config.get_logger()

# Cargar variables de entorno
load_dotenv()

NEW_DB_NAME = "idealista_analyzer" # Nombre de la bd
# Obtener una conexión directa sin SQLAlchemy para crear la BD   
def get_raw_connection():
    
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        dbname="postgres"
    )

# Obtener conexion SQLAlchemy para la creacion de tablas
def get_db_engine():   
    return create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{NEW_DB_NAME}"
    )

# Funcion para crear la BD
def create_database():
   # Crea la base de datos usando psycopg2 directamente
    conn = None
    try:
        conn = get_raw_connection()
        conn.autocommit = True  # Necesario para CREATE DATABASE, por eso usa psycopg2 para crear la bd 
        cursor = conn.cursor()
        
        # Verificar si la BD ya existe
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", 
            (NEW_DB_NAME,)
        )
        exists = cursor.fetchone()

        if not exists:
            logger.info(f"Creando base de datos {NEW_DB_NAME}...")
            cursor.execute(f"CREATE DATABASE {NEW_DB_NAME}")
            logger.info("Base de datos creada exitosamente")
        else:
            logger.info(f"La base de datos {NEW_DB_NAME} ya existe")
            
    except Exception as e:
        logger.error(f"Error al crear la base de datos: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Funcion para crear las tablas
def create_tables(): 
    engine = get_db_engine()
    try:
        sql_statements = [
            """
            CREATE TABLE IF NOT EXISTS localizaciones(
                nombre TEXT PRIMARY KEY,
                provincia TEXT,
                latitud DECIMAL(9, 6),
                longitud DECIMAL(9, 6)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS usuarios(
                id_usuario SERIAL PRIMARY KEY,
                nombre TEXT,
                password_hash TEXT,
                es_admin BOOL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS casas(
                idcasas SERIAL PRIMARY KEY,
                referencia INTEGER UNIQUE,
                titulo TEXT,
                localizacion TEXT REFERENCES localizaciones(nombre),
                precio INTEGER,
                ascensor SMALLINT,
                baños SMALLINT,
                trastero SMALLINT,
                piso TEXT,
                habitaciones SMALLINT,
                metros_reales SMALLINT,
                armarios_empotrados SMALLINT,
                terraza SMALLINT,
                garaje SMALLINT,
                calefaccion SMALLINT,
                aire_acondicionado SMALLINT,
                piscina SMALLINT,
                zonas_verdes SMALLINT,
                fecha_agregacion DATE DEFAULT CURRENT_DATE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS incidencias(
                id_incidencia SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL,
                asunto TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                en_curso BOOL DEFAULT false,
                finalizada BOOL DEFAULT false,
                observaciones TEXT
            )
            """
        ]
        logger.info("Creando tablas...")
        with engine.begin() as conn:
            for statement in sql_statements:
                conn.execute(text(statement))
        
        logger.info("Tablas creadas exitosamente")

    except SQLAlchemyError as e:
        logger.error(f"Error al crear las tablas: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    try:
        create_database()
        
        create_tables()
        
        logger.info("Proceso completado exitosamente")
    except Exception as e:
        logger.error(f"Error en el proceso: {e}")