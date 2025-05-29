from locust import HttpUser, task, between
import random
import urllib.parse
import time
from ..settings.logger import LoggerConfig

# Crear logger
logger_config = LoggerConfig(log_filename="log_locustfile.log")
logger = logger_config.get_logger()
# CLASE PARA REALIZAR PRUEBA DE CARGA EN LA APLICACION DE STREAMLIT
class StreamlitUser(HttpUser):
    wait_time = between(1, 3)

    # Lista de opciones para rellenar el valor localizaciones del formulario aleatoriamente
    LOCALIZACIONES = [
        "Albaicín, Granada", "Barrio de los Periodistas, Granada", "Bola de Oro, Granada",
        "Campus de la Salud, Granada", "Carrera de la Virgen - Paseo del Salón, Granada", "Catedral, Granada",
        "Centro, Granada", "Figares, Granada", "Gran Capitán, Granada",
        "Los Pajaritos, Granada", "Plaza de Toros, Granada", "Recogidas, Granada",
        "Ronda - Arabial, Granada", "San Ildefonso, Granada", "San Matías - Pavaneras, Granada",
        "Zaidín, Granada", "Armilla", "Atarfe", "Cajar", "Gojar", "Huétor-Vega", "La Zubia", "Monachil", "Otro"
    ]
    # Lista de opciones para rellenar el valor pisos del formulario aleatoriamente
    PISOS = ["Bajo", "Primeros pisos", "Ultimos pisos"]

    # Funcion para escoger aleatoriamente true o false
    def random_bool_str(self):
        return str(random.choice([True, False])).lower()

    # Tarea a simular en la prueba de cargar la pagina principal
    @task
    def load_inicio(self):
        self.client.get("/")

    # Tarea a simular en la prueba de rellenar y enviar el formulario para la prediccion del precio
    @task
    def enviar_formulario(self):
        params = {
            "metros": random.randint(20, 200),
            "habitaciones": random.randint(1, 5),
            "banios": random.randint(1, 3),
            "localizacion": random.choice(self.LOCALIZACIONES),
            "piso": random.choice(self.PISOS),
            "ascensor": self.random_bool_str(),
            "garaje": self.random_bool_str(),
            "calefaccion": self.random_bool_str(),
            "aire_acondicionado": self.random_bool_str(),
            "trastero": self.random_bool_str(),
            "terraza": self.random_bool_str(),
            "piscina": self.random_bool_str(),
            "zonas_verdes": self.random_bool_str(),
        }
        params["submit"] = "true"
        query = urllib.parse.urlencode(params)
        # Se envia por url los parametros para realizar la prediccion
        # y se controla el tiempo que se tarda en generar la prediccion
        url = f"/Formulario?{query}"
        start = time.time()
        
        with self.client.get(url, catch_response=True) as response:
            duration = time.time() - start
            if response.status_code == 200:
                response.success()
                logger.info(f"🟢 Predicción OK en {duration:.2f}s")
            else:
                response.failure(f"🔴 Error {response.status_code}")
                logger.error(f"🔴 Error {response.status_code}")

    # Tarea a simular de cargar la pagina informacion del mercado
    @task
    def informacion_del_mercado(self):
        self.client.get("Informacion_del_mercado")