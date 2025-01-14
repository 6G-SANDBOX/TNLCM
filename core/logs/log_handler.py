import os
import logging
import sys

from core.utils.os_handler import get_dotenv_var

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

class ConsoleHandler:
    def __init__(self):
        self.log_file = None
        self.logger = None

        log_format = "[%(asctime)s] - [%(process)d] - [%(levelname)s] - %(message)s"
        log_level_name = get_dotenv_var(key="TNLCM_LOG_LEVEL").upper()
        _, log_level = LOG_LEVELS_AND_FORMATS[log_level_name]

        console_formatter = CustomFormatter(log_format)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)

        self.logger = logging.getLogger("TNLCM")
        self.logger.propagate = False
        self.logger.setLevel(log_level)
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

class TnLogHandler:
    def __init__(self, tn_id: str):
        from conf.tnlcm import TnlcmSettings
        log_file_name = f"{tn_id}.log"
        log_file_path = os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, tn_id, log_file_name)

        self.logger = logging.getLogger(tn_id)
        self.logger.setLevel(logging.INFO)
        
        log_format = "[%(asctime)s] - [%(process)d] - [%(levelname)s] %(message)s"
        file_formatter = logging.Formatter(log_format)
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

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

    @staticmethod
    def get_logger(tn_id):
        return logging.getLogger(tn_id)

    # @staticmethod
    # def get_log_content(tn_id):
    #     log_file_path = os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, tn_id, f"{tn_id}.log")
    #     with open(log_file_path, "rb") as log_file:
    #         return log_file.read()
    
    # @staticmethod
    # def get_last_log_line(tn_id):
    #     log_file_path = os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, tn_id, f"{tn_id}.log")
    #     if not os.path.isfile(log_file_path):
    #         return f"Log file for TN ID {tn_id} not found."

    #     with open(log_file_path, "r") as log_file:
    #         lines = log_file.readlines()
    #         return lines[-1].strip() if lines else "No log entries found."

    def close(self):
        logging.shutdown()
        self.logger = None
        self.log_file = None

tnlcm_log_handler = ConsoleHandler()