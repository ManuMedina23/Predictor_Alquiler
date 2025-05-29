from sqlalchemy import Column, Float, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from geopy.geocoders import Nominatim
from db_connection import get_engine
import time
from logger import LoggerConfig

# Crear logger
logger_config = LoggerConfig(log_filename="log_geocoder.log")
logger = logger_config.get_logger()

def geolocalizar():
    # Conexion a BD
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    # Modelo ORM
    Base = declarative_base()

    class Localizacion(Base):
        __tablename__ = 'localizaciones'
        nombre = Column(Text, primary_key=True)
        provincia = Column(Text)
        latitud = Column(Float)
        longitud = Column(Float)

    # Geocodificador
    geolocator = Nominatim(user_agent="geo_sqlalchemy")

    # Leer las direcciones desde la bd
    localizaciones = session.query(Localizacion).filter(
        (Localizacion.latitud == None) | (Localizacion.longitud == None)
    ).all()


    try:
        # De cada localizacion en la bd obtener su latitud y longitud 
        # utilizando el geolocator
        for localizacion in localizaciones:
            time.sleep(1)
            if localizacion.nombre:
                location = geolocator.geocode(localizacion.nombre)
                if location:
                    localizacion.latitud = location.latitude
                    localizacion.longitud = location.longitude
                    logger.info(f"Encontrado: {localizacion.nombre} → ({localizacion.latitud}, {localizacion.longitud})")
                else:
                    logger.info(f" Dirección no encontrada: {localizacion.nombre}")

        # Guardar cambios
        session.commit()


    except Exception as ex:
        logger.error(f"Error geolocalizando {str(ex)}")
    finally:
        session.close()
        engine.dispose()