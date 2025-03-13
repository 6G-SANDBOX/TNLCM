import logging
import sys

from core.utils.os import TRIAL_NETWORKS_DIRECTORY_PATH, get_dotenv_var, join_path

LOG_LEVELS_AND_FORMATS = {
    "DEBUG": ("\x1b[38;21m", logging.DEBUG),
    "INFO": ("\x1b[38;5;39m", logging.INFO),
    "WARNING": ("\x1b[38;5;226m", logging.WARNING),
    "ERROR": ("\x1b[38;5;196m", logging.ERROR),
    "CRITICAL": ("\x1b[31;1m", logging.CRITICAL),
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
        formatter = logging.Formatter(fmt=log_fmt)
        return formatter.format(record=record)


class ConsoleLogger:
    def __init__(self):
        log_format = "[%(asctime)s] - [%(process)d] - [%(levelname)s] - %(message)s"
        log_level_name = get_dotenv_var(key="TNLCM_CONSOLE_LOG_LEVEL").upper()
        _, log_level = LOG_LEVELS_AND_FORMATS[log_level_name]

        console_formatter = CustomFormatter(fmt=log_format)
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setLevel(level=log_level)
        console_handler.setFormatter(fmt=console_formatter)

        self.logger = logging.getLogger(name="TNLCM")
        self.logger.propagate = False
        self.logger.setLevel(level=log_level)
        self.logger.addHandler(hdlr=console_handler)

    def critical(self, message: str) -> None:
        if self.logger:
            self.logger.critical(msg=message)

    def debug(self, message: str) -> None:
        if self.logger:
            self.logger.debug(msg=message)

    def error(self, message: str) -> None:
        if self.logger:
            self.logger.error(msg=message)

    def info(self, message: str) -> None:
        if self.logger:
            self.logger.info(msg=message)

    def warning(self, message: str) -> None:
        if self.logger:
            self.logger.warning(msg=message)


class TrialNetworkLogger:
    def __init__(self, tn_id: str):
        self.tn_id = tn_id
        log_file_name = f"{tn_id}.log"
        log_file_path = join_path(TRIAL_NETWORKS_DIRECTORY_PATH, tn_id, log_file_name)
        log_level_name = get_dotenv_var(key="TRIAL_NETWORK_LOG_LEVEL").upper()

        self.logger = logging.getLogger(name=tn_id)
        self.logger.setLevel(level=log_level_name)

        if not self.logger.hasHandlers():
            log_format = "[%(asctime)s] - [%(process)d] - [%(levelname)s] - [%(tn_id)s] - %(message)s"
            file_formatter = logging.Formatter(fmt=log_format)
            file_handler = logging.FileHandler(filename=log_file_path)
            file_handler.setFormatter(fmt=file_formatter)
            self.logger.addHandler(file_handler)

    def _log(self, level, message):
        if self.logger:
            self.logger.log(level, message, extra={"tn_id": self.tn_id})

    def critical(self, message: str) -> None:
        self._log(logging.CRITICAL, message)

    def debug(self, message: str) -> None:
        self._log(logging.DEBUG, message)

    def error(self, message: str) -> None:
        self._log(logging.ERROR, message)

    def info(self, message: str) -> None:
        self._log(logging.INFO, message)

    def warning(self, message: str) -> None:
        self._log(logging.WARNING, message)


console_logger = ConsoleLogger()
