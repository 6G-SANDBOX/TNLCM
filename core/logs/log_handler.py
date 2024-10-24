import os
import logging
import sys

from datetime import datetime

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LOGS_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "executions")

LOG_LEVELS_AND_FORMATS = {
    "DEBUG": ("\x1b[38;21m", logging.DEBUG),
    "INFO": ("\x1b[38;5;39m", logging.INFO),
    "WARNING": ("\x1b[38;5;226m", logging.WARNING),
    "ERROR": ("\x1b[38;5;196m", logging.ERROR),
    "CRITICAL": ("\x1b[31;1m", logging.CRITICAL)
}

class CustomFormatter(logging.Formatter):
    """
    Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629
    """

    reset = "\x1b[0m"

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt

    def format(self, record):
        log_color, _ = LOG_LEVELS_AND_FORMATS[record.levelname]
        log_fmt = log_color + self.fmt + self.reset
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

        log_level_name = os.getenv("TNLCM_LOG_LEVEL", "INFO").upper()
        _, log_level = LOG_LEVELS_AND_FORMATS[log_level_name]
        self.log_file = os.path.join(LOGS_DIRECTORY, log_file_name)

        file_formatter = logging.Formatter(log_format)
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)

        console_formatter = CustomFormatter(log_format)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)

        self.logger = logging.getLogger("TNLCM")
        self.logger.propagate = False
        self.logger.setLevel(log_level)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        if self.logger:
            self.logger.debug(message)
    
    def info(self, message):
        if self.logger:
            self.logger.info(message)

    def warning(self, message):
        if self.logger:
            self.logger.warning(message)

    def error(self, message):
        if self.logger:
            self.logger.error(message)
    
    def critical(self, message):
        if self.logger:
            self.logger.critical(message)

    def close(self):
        logging.shutdown()
        self.logger = None
        self.log_file = None

log_handler = LogHandler()