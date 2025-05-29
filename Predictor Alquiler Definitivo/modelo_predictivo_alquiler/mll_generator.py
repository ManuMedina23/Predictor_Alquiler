import numpy as np
import pandas as pd
from pathlib import Path 
import pickle
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV
from db_connection import get_engine
from logger import LoggerConfig

# Ruta donde se almacena el modelo y los encoders
DIR = Path('./generado')
# Crear la ruta si no existe
DIR.mkdir(parents=True, exist_ok=True)
MODELO = f"{DIR}/modelo_mll.pkl"
ENCODERS = f"{DIR}/encoded_columns.npy"

# Crear logger
logger_config = LoggerConfig(log_filename="log_mll_generator.log")
logger = logger_config.get_logger()

# Obtener los datos desde la base de datos
engine = get_engine()
query = "SELECT * FROM casas"
df_pisos = pd.read_sql(query, engine)
# Se eliminan columnas innecesarias 
df_pisos = df_pisos.drop(columns=['idcasas', 'referencia', 'fecha_agregacion'])
logger.info("Datos obtenidos")

#Eliminar pisos con pocos metros cuadrados mediante Umbral Dinamico
# Calcular el percentil 1% de la columna 'metros_reales'
# Esto se hace para eliminar outliers que puedan afectar el modelo
threshold = np.percentile(df_pisos['metros_reales'], 1)  # Percentil 1% de los m2 de todos los pisos
umbral_final = max(threshold, 20)  # Si el percentil esta por debajo de 20 se asegura eliminar cualquier piso con menos de 20m2
df_filtrado = df_pisos[df_pisos['metros_reales'] >= umbral_final] # Se filtra el df
logger.info("Percentil aplicado a la columna m2")

# One HOT Encoding
df_pisos = pd.get_dummies(df_filtrado, dtype='int', columns=["localizacion","piso"])

# Se guardan caracteristicas en la variable x y precio que es la variable objetivo en la y. axis=1 indica que queremos eliminar columnas y no registros.
x, y = df_pisos.drop(["precio","titulo"], axis=1), df_pisos["precio"]

# Se prepara del mismo modo una variable que contendrá una lista con todos características
vars_pisos = list(df_pisos.columns)
vars_pisos.remove('precio')
vars_pisos.remove('titulo')

# GENERACION DEL MODELO
# Se va a aplicar GridSearchCV para buscar el mejor alpha posible y su resultado.

# Definir el rango de valores para alpha
param_grid_lr_m = {'alpha': [0.01, 0.1, 1, 10, 100, 500, 1000]}

logger.info("Generando modelo aplicando mejora de hiper parametros")
# Crear modelo base
lr_m = Ridge()

# Configurar GridSearch con validación cruzada
grid_search_lr_m = GridSearchCV(estimator=lr_m,
                                param_grid=param_grid_lr_m, 
                                scoring='neg_mean_absolute_error', 
                                cv=5,
                                verbose=1)

# Ajustar a los datos
grid_search_lr_m.fit(x, y)

# Mostrar el mejor valor de alpha y su resultado
logger.info("Mejor alpha:", grid_search_lr_m.best_params_['alpha'])
logger.info("MAE (validación cruzada): %.3f" % -grid_search_lr_m.best_score_)


lr_estimador = grid_search_lr_m.best_estimator_

logger.info("Guardando modelo")
# Guardar el modelo
with open(MODELO, 'wb') as f:
    pickle.dump(lr_estimador, f)

logger.info("Modelo guardado")

logger.info("Guardando encoders")
# Guardar encoders
features = df_pisos.drop(columns=['titulo', 'precio']).columns
np.save(ENCODERS, features)
logger.info("Encoders guardados")


