﻿# Predictor_Alquiler
Modelo predictivo de precios de alquiler basado en Regresion Lineal empleando scikit-learn

# Funcionamiento
https://predictoralquilergr.streamlit.app/

# Instrucciones para utilizarlo

REQUISITOS:
POSTGRESQL BD (Testeado con con la version 17)
PYTHON 13.x.x


 1. Primero ejecutar preparar_entorno.bat para crear el entorno virtual de python con los paquetes necesarios.
 2. En la carpeta modelo_predictivo_alquiler crear un archivo .env con los siguientes datos:
    DB_HOST=    #[Host de la base de datos]
    DB_PORT=    #[Puerto de la bd]
    DB_USER=    #[usuario de la bd]
    DB_PASSWORD=    #[password de la bd]
    DB_NAME=    #[nombre de la bd]
 3. Activar el entorno virtual de python y ejecutar la clase db_generator.py
 4. Ejecutar idealista_scraping.py
    Dentro de esta clase se puede cambiar la constante URL por otra url de busqueda de idealista para cambiar al target de los datos obtenidos. 
 5. Ejecutar pipeline.py
 6. Ejecutar mll_generator.py
    Esto habrá creado un carpeta llamada generado con un archivo pkl y otro npy. Estos archivos se deben copiar en webapp/resources. Es el modelo de machine learning empleado para la prediccion en la web
 7. En la carpeta webapp ejecutar crear_usuario.bat para crear un administrador
 8. Ejecutar iniciar.bat para levantar la aplicación.
