import os
import logging
import sys

from datetime import datetime

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LOGS_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "executions")

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] - %(name)s - [%(levelname)s] %(message)s"

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
    def __init__(self, loggers):
        self.log_file = None
        self.logger = None

        os.makedirs(LOGS_DIRECTORY, exist_ok=True)

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        log_file_name = f"execution_{timestamp}.log"
        self.log_file = os.path.join(LOGS_DIRECTORY, log_file_name)

        file_formatter = logging.Formatter("[%(asctime)s] -%(name)s - [%(levelname)s] %(message)s")
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)

        console_formatter = CustomFormatter()
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        self.logger = logging.getLogger("tnlcm")
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        for log in loggers:
            if log != "waitress" and log != "werkzeug":
                log_libraries = logging.getLogger(log)
                log_libraries.propagate = False
                log_libraries.setLevel(logging.INFO)
                log_libraries.addHandler(file_handler)
                log_libraries.addHandler(console_handler)

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

log_handler = LogHandler(["waitress", "werkzeug"])