import os
import logging
import sys

from datetime import datetime

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class LogHandler:
    def __init__(self, executions_folder="src/logs/executions"):
        self.executions_folder = executions_folder
        self.log_file = None
        self.logger = None

        if not os.path.exists(self.executions_folder):
            os.makedirs(self.executions_folder)

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        log_file_name = f"execution_{timestamp}.log"
        self.log_file = os.path.join(self.executions_folder, log_file_name)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)")

        console_formatter = CustomFormatter()

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

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

log_handler = LogHandler()