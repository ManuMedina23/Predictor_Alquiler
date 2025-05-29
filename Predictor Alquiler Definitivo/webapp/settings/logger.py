import logging
import os

class LoggerConfig:
    def __init__(self, log_filename='log.log', log_dir='logs', level=logging.INFO):
        # Crear el directorio si no existe
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_path = os.path.join(log_dir, log_filename)

        # Crear el logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        self.logger.handlers = []  # Limpiar handlers anteriores para evitar duplicados

        # Formato de log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Handler para archivo
        file_handler = logging.FileHandler(log_path, mode='w')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self.logger.info(f'Logger iniciado en {log_path}')

    def get_logger(self):
        return self.logger
