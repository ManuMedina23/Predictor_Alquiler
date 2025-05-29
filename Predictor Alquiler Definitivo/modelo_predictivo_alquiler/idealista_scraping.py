from bs4 import BeautifulSoup as bs #Permite extraer el html y analizarlo
import random
import time
import pandas as pd
import undetected_chromedriver as uc #Permite no ser detectado
import time
from datetime import datetime
from pathlib import Path
from logger import LoggerConfig

# Crear logger
logger_config = LoggerConfig(log_filename="log_IdealistaScraping.log")
logger = logger_config.get_logger()

# PATH GUARDAR ARCHIVO
date = datetime.now().strftime("%d-%m-%Y")
DIR = Path('./csvcasas')
PATH_CSV = f'{DIR}/casas_idealista_{date}.csv'

# URL SCRAPING
URL = 'https://www.idealista.com/areas/alquiler-viviendas/?shape=%28%28sy%7CaFjhxU%7DlIcyDgf%40%7DqNxvAc%60ErxQytHz%7DEpvGi%7E%40%7EzKyzMloN%29%29'

# Numero página de anuncios idealista
npagina = 1
maxpaginas= 15
def parsear_inmueble(id_inmueble):
    logger.info('\n Casa numero: ' + id_inmueble)
    
    url = "https://www.idealista.com/inmueble/" + id_inmueble + "/"

    browser.get(url)
    html = browser.page_source
    soup = bs(html, 'html')
    
    # Obtener titulo del anuncio
    titulo = soup.find('span',{'class':'main-info__title-main'}).text
    logger.info('\n Titulo: ' + titulo)

    # Obtener localizacion del anuncio
    localizacion = soup.find('span', {'class':'main-info__title-minor'}).text
    logger.info('\n Localizacion: ' + localizacion)

    # Obtener precio del anuncio
    precio = int(soup.find('span',{'class':'txt-bold'}).text.replace('.',''))
    
    # Se obtiene todo el bloque de caracteristicas basicas
    c1 = soup.find('div',{'class':'details-property-feature-one'})
    
    # Se procesa el bloque de caracteristicas basicas y se crea un array con cada una
    caract_basicas = [caract.text.strip() for caract in c1.find_all('li')]
    
    # Se obtiene todo el bloque de caracteristicas extras
    c2 = soup.find('div',{'class':'details-property-feature-two'})
    
    # Se procesa el bloque de caracteristicas extras  y se crea un array con cada una
    caract_extra = [caract.text.strip() for caract in c2.find_all('li')]

    casas['referencia'] = id_inmueble
    casas['titulo'] = titulo
    casas['localizacion'] = localizacion
    casas['precio'] = precio
    casas['caracteristicas_basicas'] = caract_basicas
    casas['caracteristicas_extras'] = caract_extra
    df_casas = pd.DataFrame(casas)

    return(df_casas.T)

try:
    # Abrir navegador
    browser = uc.Chrome()

    url_grande = URL
    # Cargar url principal de la busqueda 
    browser.get(url_grande)
    # Aceptar cookies
    browser.find_element("xpath", '//*[@id="didomi-notice-agree-button"]').click()
    # Obtener el html de la web
    html = browser.page_source
    #Cargar el html a BeautifulSoup
    soup = bs(html, 'html')

except Exception as ex:
    logger.error("Error montando el navegador ", str(ex))

try:
    #Recoger todos los anuncios
    article = soup.find('main',{'class':'listing-items'}).find_all('article')

    #Obtener id de los anuncios (pisos)
    id_inmuebles = [article.get('data-element-id') for article in article]

    #Eliminar los None
    id_inmuebles = [muebles for muebles in id_inmuebles if muebles is not None]

    busqueda = 'shape=%28%28sy%7CaFjhxU%7DlIcyDgf%40%7DqNxvAc%60ErxQytHz%7DEpvGi%7E%40%7EzKyzMloN%29%29'
    
    ids = []

    while True and npagina < maxpaginas:
        url = f'https://www.idealista.com/areas/alquiler-viviendas/pagina-{npagina}?{busqueda}'
        browser.get(url)

        #Tiempo de esperar para no ser bloqueados por la web
        time.sleep(random.randint(10,12))

        # Aceptar cookies
        try:
            browser.find_element("xpath", '//*[@id="didomi-notice-agree-button"]').click()
        except:
            pass

        html = browser.page_source
        soup = bs(html, 'html')
        # Obtener pagina actual
        pagina_actual = int(soup.find('div',{'class':'pagination'}).find('li',{'class':'selected'}).text)
        if npagina == pagina_actual:
            # Obtener todos los anuncios
            articles = soup.find('main',{'class':'listing-items'}).find_all('article')
        else:
            break
        # Recorrer todos los anuncios para obtener sus ids y guardarlas
        for article in articles:
            id_inmuebles = article.get('data-element-id')

            ids.append(id_inmuebles)
            # Tiempo de esperar para no ser bloqueados por la web
            time.sleep(random.randint(1,3))
            logger.info(id_inmuebles)
            # Excluir los none
            ids = [inmuebles for inmuebles in ids if inmuebles is not None]

        npagina += 1

    casas = pd.Series()
except Exception as ex:
    logger.error(f"Error obteniendo los ids  {str(ex)}")
    pass
finally:
    ids_casas = pd.DataFrame(ids)
    ids_casas.columns = ['id']
    ids_casas


# Inicializar df_casas
df_casas = parsear_inmueble(ids_casas.iloc[0].id)

# Continuar con el resto de ids de la lista para parsear todos los inmuebles obtenidos
for i in range(1, len(ids)):
    try:
        df_casas = pd.concat([df_casas, parsear_inmueble(ids[i])])
        time.sleep(random.randint(4,8))
    except Exception as ex:
        logger.error('Error parseando el inmueble' + str(ex))
    finally:

        # Crear la ruta si no existe
        DIR.mkdir(parents=True, exist_ok=True)
        # Eliminar el index del df
        df_casas.reset_index(drop=True, inplace=True)
        # Guardar los datos en un csv
        df_casas.to_csv(PATH_CSV, index = False, sep = ';', encoding = 'utf-16')
        
        logger.info(f"Datos recopilados en {PATH_CSV}")
