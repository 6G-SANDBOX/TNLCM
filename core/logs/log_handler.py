import os
import logging
import sys

from datetime import datetime

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LOGS_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "executions")

class CustomFormatter(logging.Formatter):
    """
    Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629
    """

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class LogHandler:
    def __init__(self):
        self.log_file = None
        self.logger = None

        os.makedirs(LOGS_DIRECTORY, exist_ok=True)

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        log_file_name = f"tnlcm_{timestamp}.log"
        log_format = "[%(asctime)s] - [%(process)d] - %(name)s - [%(levelname)s] %(message)s"
        self.log_file = os.path.join(LOGS_DIRECTORY, log_file_name)

        file_formatter = logging.Formatter(log_format)
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)

        console_formatter = CustomFormatter(log_format)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        self.logger = logging.getLogger("TNLCM")
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)
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