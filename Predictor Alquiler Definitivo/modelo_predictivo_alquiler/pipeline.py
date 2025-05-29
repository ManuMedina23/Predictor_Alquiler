import pandas as pd
import numpy as np
from ast import literal_eval
import re
from db_connection import get_engine
from geocoder import geolocalizar
from psycopg2.errors import UniqueViolation
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import MetaData
from logger import LoggerConfig
import time
from datetime import datetime
from pathlib import Path 
# Crear logger
logger_config = LoggerConfig(log_filename="log_pipeline.log")
logger = logger_config.get_logger()

# Ruta del csv resultante del scraping y que se va a procesar
date = datetime.now().strftime("%d-%m-%Y")
DIR = Path('csvcasas')
PATH_CSV = f'{DIR}/casas_idealista_{date}.csv'

#PATH_CSV = "csvcasas/casas_idealista_11-05-2025.csv" # descomentar esta linea y comentar la anterior para introducir un archivo con otra fecha

# Funcion para encontrar una palabra en la propiedad
def match_property(property, patterns):
    for pat in patterns:
        match_prop = re.search(pat, property)
        if match_prop:
            return True
    return False        
# Funcion para comprobar si se cumple una propiedad o no
def check_property(property, patterns):
    for pat in patterns:
        check = re.search(pat, property)
        if check:
            return 1
    return 0        

def get_number(property):
    nums = re.findall(r'\d', property)
    if len(nums) == 2:
        return int(nums[0] + nums[1])
    else:
        return int(nums[0])
    
def get_ascensor(features):
    for prop in features:
        if match_property(prop.lower().strip(), ['ascensor']):
            return(check_property(prop.lower().strip(), ['con']))    
        
def get_baños(features):
    for prop in features:
        if match_property(prop.lower().strip(), ['baño']):
            return(get_number(prop.lower().strip()))

def get_año(features):
    for prop in features:
        if match_property(prop.lower().strip(), ['construido en']):
            return(get_number(prop.lower().strip()))

def get_trastero(features):
    value = 0
    for prop in features:
        if match_property(prop.lower().strip(), ['trastero']):
            value +=1
    return(value)

def get_orientacion(features):
    for prop in features:
        if match_property(prop.lower().strip(), ['orientacion']):
            return(prop.split(' ', maxsplit=1)[1].strip().split(', ')[0])                        

def get_piso(features):
    for prop in features:
        if match_property(prop.lower().strip(), ['bajo','planta','interior','exterior']):
            return(prop)

def get_habitaciones(features):
    for prop in features:
        if match_property(prop.lower().strip(), ['habitaci']):
            try:
                habitaciones = get_number(prop.lower().strip())
            except:
                habitaciones = prop
            return(habitaciones)

def get_metros_reales(features):
    for prop in features:
        if match_property(prop.lower().strip(), ['m²']):
            try:
                metros = get_number(prop.lower().strip().split(',')[0])
            except:
                metros = prop
            return(metros)    
                            
def get_condicion(features):
    for prop in features:
        if match_property(prop.lower().strip(), ['segunda mano', 'promocion de obra nueva']):
            return(prop)

def get_armario_empotrado(features):
    value = 0
    for prop in features:
        if match_property(prop.lower().strip(), ['armarios empotrados']):
            value +=1
    return(value)                

def get_terraza(features):
    value = 0
    for prop in features:
        if match_property(prop.lower().strip(), ['terraza']):
            value +=1
    return(value)   

def get_balcon(features):
    value = 0
    for prop in features:
        if match_property(prop.lower().strip(), ['balcon']):
            value +=1
    return(value)          

def get_jardin(features):
    value = 0
    for prop in features:
        if match_property(prop.lower().strip(), ['jardin']):
            value +=1
    return(value)

def get_garaje(features):
    value = 0
    for prop in features:
        if match_property(prop.lower().strip(), ['garaje']):
            value +=1
    return(value)

def get_calefaccion(features):
    value = 0
    for prop in features:
        if match_property(prop.lower().strip(), ['calefacción']):
            value +=1
    return(value)

def get_aire_acon(features):
    value = 0
    for prop in features:
        if match_property(prop.lower().strip(), ['aire acondicionado']):
            value +=1
    return(value)

def get_piscina(features):
    value = 0
    for prop in features:
        if match_property(prop.lower().strip(), ['piscina']):
            value +=1
    return(value)

def get_zonas_verdes(features):
    value = 0
    for prop in features:
        if match_property(prop.lower().strip(), ['zonas verdes']):
            value +=1
    return(value)

# Obtener planta del piso
def process_piso(serie):
    lista = serie.split()
    mapeo = ''
    if ((lista[0] == 'Bajo') | (lista[0] == 'Entreplanta') | (lista[0] == 'Exterior')):
        mapeo = 'Bajo'
    elif lista[0] == 'Planta':
        try:           
            if int(lista[1][0]) < 4:
                mapeo = 'Primeros_pisos'
            else:
                mapeo = 'Ultimos_pisos'
        #Excepcion que ocurre con aquellos que incluyen un signo antes del número,         
        except ValueError:
            if int(lista[1][1]) < 4:
                mapeo = 'Primeros_pisos'
            else:
                mapeo = 'Ultimos_pisos'              
    else:
        mapeo = 'Muchas_plantas'
    return(mapeo)    

# Leer CSV con los datos
def cargar_csv(csv):
    df = pd.read_csv(csv, 
                    sep=';', 
                    encoding='utf-16', 
                    converters={'caracteristicas_basicas': literal_eval, 
                                'caracteristicas_extras': literal_eval})
    return df

# Funcion para guardar las localizaciones en su respectiva tabla la BD
def guardar_localizaciones(localizaciones):
    try:
        engine = get_engine()
        con = engine.connect()

        metadata = MetaData()
        metadata.reflect(bind=engine)
        tabla = metadata.tables['localizaciones']
        df_localizaciones = pd.DataFrame(localizaciones, columns=['nombre']).to_dict(orient='records')

        try:
            # Se inserta fila por fila en la bd para en caso de que ya exista no la inserte 
            # y no se genere una excepcion
            for row in df_localizaciones:
                query = insert(tabla).values(nombre=row['nombre']).on_conflict_do_nothing(index_elements=['nombre'])
                con.execute(query)        
            con.commit()
        except Exception as ex:
            logger.error(f"Error insertando localizaciones: {str(ex)}")
            con.rollback()

    except UniqueViolation as ex:
        pass
    except Exception as ex:
        logger.error(f"Error creando tabla localizaciones: {str(ex)}")
        con.rollback()   
    finally:
        con.close()
        engine.dispose()

# Funcion para guardar las casas en su respectiva tabla en la BD
def guardar_casas(df_casas):
    try:
        engine = get_engine()
        con = engine.connect()

        metadata = MetaData()
        metadata.reflect(bind=engine)
        tabla = metadata.tables['casas']
        df_casas = pd.DataFrame(df_casas).to_dict(orient='records')

        try:
            # Se inserta fila por fila en la bd para en caso de que ya exista no la inserte 
            # y no se genere una excepcion
            for row in df_casas:
                query = insert(tabla).values(row).on_conflict_do_nothing()
                con.execute(query)

            con.commit() 
        except Exception as ex:
            logger.error(f"Error insertando casas: {str(ex)}")
            con.rollback()    
            

    except AttributeError:
        logger.error(AttributeError)
    except ValueError:
        pass    

# Se carga el archivo csv procedente del scraping 
logger.info(f"Cargando archivo {PATH_CSV}") 
df = cargar_csv(PATH_CSV)

logger.info("Procensado...")

# Añadir columnas con los datos procesados
df['ascensor'] = df.caracteristicas_basicas.apply(get_ascensor)
df['baños'] = df.caracteristicas_basicas.apply(get_baños)
df['año'] = df.caracteristicas_basicas.apply(get_año)
df['trastero'] = df.caracteristicas_basicas.apply(get_trastero)
df['orientacion'] = df.caracteristicas_basicas.apply(get_orientacion)
df['piso'] = df.caracteristicas_basicas.apply(get_piso)
df['habitaciones'] = df.caracteristicas_basicas.apply(get_habitaciones)
df['metros_reales'] = df.caracteristicas_basicas.apply(get_metros_reales)
df['condicion'] = df.caracteristicas_basicas.apply(get_condicion)
df['armarios_empotrados'] = df.caracteristicas_basicas.apply(get_armario_empotrado)
df['terraza'] = df.caracteristicas_basicas.apply(get_terraza)
df['balcon'] = df.caracteristicas_basicas.apply(get_balcon)
df['jardin'] = df.caracteristicas_basicas.apply(get_jardin)
df['garaje'] = df.caracteristicas_basicas.apply(get_garaje)
df['calefaccion'] = df.caracteristicas_basicas.apply(get_calefaccion)
df['aire_acondicionado'] = df.caracteristicas_extras.apply(get_aire_acon)
df['piscina'] = df.caracteristicas_extras.apply(get_piscina)
df['zonas_verdes'] = df.caracteristicas_extras.apply(get_zonas_verdes)

# Borras columnas de caracteristicas basicas y extras, ya no son necesarias
df.drop(columns = ['caracteristicas_basicas', 'caracteristicas_extras'], inplace = True)

# Procesado de datos basados en el EDA
df.loc[df['ascensor'].isna(), 'ascensor'] = 0 # Reemplazar NA del ascensor por 0
df = df[~df.piso.isna()] # Como el dataframe no es reciente y quizas no existan los anuncios se eliminan aquellos sin el dato piso
df.piso = df.piso.apply(process_piso) # Se procesa el numero del piso para categorizarlo
df.loc[df.habitaciones == 'Sin habitación', 'habitaciones'] = 1 # Aquellos sin habitación se cambian por 1, se supone que al menos 1  hay
df.drop(columns = ['balcon','jardin','año','orientacion','condicion'], inplace=True) # Se eliminan la columnas balcon, jardin, año y orientacion porque no aportan apenas informacion


# Eliminar pisos con pocos metros cuadrados mediante Umbral Dinamico
# Calcular el percentil 1% de la columna 'metros_reales'
# Esto se hace para eliminar outliers que puedan afectar el modelo
percentil = np.percentile(df['metros_reales'], 1)  # Percentil 1%
umbral_final = max(percentil, 20)  # Elige el mayor entre el percentil y 20
df_filtrado = df[df['metros_reales'] >= umbral_final]

# Calcular la media de precio por localización
media_por_localizacion = df_filtrado.groupby('localizacion')['precio'].transform('mean')


# Se eliminan aquellos con mas de un 100% diferencia arriba o abajo respecto a la media de su localizacion
# este df filtrado será el que se guarde en la bd finalmente
df_filtrado = df_filtrado[
    (df_filtrado['precio'] >= media_por_localizacion * 0) &
    (df_filtrado['precio'] <= media_por_localizacion * 2)
]

# Df con con cada una de las localizaciones sin repetir
df_localizaciones = df_filtrado['localizacion'].unique()
# Se guarda una copia en formato csv por si fallase la conexión con la bd 
df_filtrado.to_csv('idealista_machine_learning.csv', index = False)

logger.info("Guardando en la base de datos")

# Guardas las localizaciones
guardar_localizaciones(df_localizaciones)
time.sleep(3)
# Guardar df final en la bd
guardar_casas(df_filtrado)
# Funcion importada de la clase geocoder para obtener la latitud y longitud de las localizaciones
# automaticamente este cambio se guarda en la bd
logger.info("Obteniendo geolocalizaciones")
geolocalizar()
