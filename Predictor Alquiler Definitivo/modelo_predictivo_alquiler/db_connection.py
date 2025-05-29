import sqlalchemy as sa
from sqlalchemy import URL
import os
from dotenv import load_dotenv
from logger import LoggerConfig

# Cargar variables del entorno
if not load_dotenv():
    load_dotenv("./modelo_predictivo_alquiler/.env")

# Crear logger
logger_config = LoggerConfig(log_filename="log_db_connection.log")
logger = logger_config.get_logger()

#Conexion BD
__url_object = URL.create(
    drivername='postgresql',
    username=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME')
)
try:
    engine = sa.create_engine(__url_object)
    if (engine != None):
        logger.info('Se ha conectado con exito a la bd')
except:
    logger.error('Error conectando a la bd')    


def get_engine():
    return engine
