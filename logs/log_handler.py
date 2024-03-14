import logging
import os
from datetime import datetime

class LogHandler:
    def __init__(self, executions_folder='logs/executions'):
        self.executions_folder = executions_folder
        self.log_file = None
        self.logger = None

        if not os.path.exists(self.executions_folder):
            print(self.executions_folder)
            os.makedirs(self.executions_folder)

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        log_file_name = f"execution_{timestamp}.log"
        self.log_file = os.path.join(self.executions_folder, log_file_name)

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.logger = logging.getLogger()
        file_handler = logging.FileHandler(self.log_file)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def info(self, message):
        if self.logger:
            self.logger.info(message)

    def warning(self, message):
        if self.logger:
            self.logger.warning(message)

    def error(self, message):
        if self.logger:
            self.logger.error(message)

    def close(self):
        logging.shutdown()
        self.logger = None
        self.log_file = None