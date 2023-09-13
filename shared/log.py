import logging
import time
from logging.handlers import RotatingFileHandler
from flask import Flask
from os.path import exists, join
from .io import IO
import traceback
from typing import Union, Optional, List, Dict, Tuple
import sys
import re
from enum import Enum, unique
from os.path import abspath


@unique
class Level(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ColoredFormatter(logging.Formatter):
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    RESET_SEQ = '\033[0m'
    COLOR_SEQ = '\033[1;%dm'

    COLORS = {
        'WARNING': YELLOW,
        'INFO': WHITE,
        'DEBUG': BLUE,
        'ERROR': RED,
        'CRITICAL': MAGENTA
    }

    def format(self, record):
        if record.levelname in self.COLORS:
            color_levelname = self.COLOR_SEQ \
                              % (30 + self.COLORS[record.levelname]) \
                              + record.levelname \
                              + self.RESET_SEQ
            record.levelname = color_levelname
        return logging.Formatter.format(self, record)


entryParser = re.compile(r'(\d+-\d+-\d+) (\d+:\d+:\d+,\d+) - (CRITICAL|ERROR|WARNING|INFO|DEBUG) - ((.*\|\|)*)(.*)')


class Log:
    CONSOLE_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    FILE_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

    # Rotating log files configuration
    LOG_SIZE = 16777216
    LOG_COUNT = 10

    initialized = False
    outFolder = None
    mainLogName = None
    logger: logging.Logger = None

    @classmethod
    def Initialize(cls, outFolder: str, logName: str, consoleLevel: int|str, fileLevel: int|str, app: Flask = None):
        cls.outFolder = abspath(outFolder)
        cls.mainLogName = logName

        # Use Flask's log if inside a Flask application, otherwise create a new one.
        if app is None:
            cls.logger = logging.getLogger(cls.mainLogName)
            cls.logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        else:
            cls.logger = app.logger

        # Save messages with UTC times
        logging.Formatter.converter = time.gmtime

        # Accept all messages on Flask logger, but display only up to the selected level
        cls.logger.setLevel(logging.DEBUG)

        console_handler: logging.Handler = cls.logger.handlers[0]
        console_handler.setLevel(consoleLevel)
        console_handler.setFormatter(ColoredFormatter(cls.CONSOLE_FORMAT))

        # Attach new file handler
        IO.EnsureFolder(cls.outFolder)
        file_handler = RotatingFileHandler(
            join(cls.outFolder, f'{cls.mainLogName}.log'), maxBytes=cls.LOG_SIZE, backupCount=cls.LOG_COUNT)
        file_handler.setFormatter(logging.Formatter(cls.FILE_FORMAT))
        file_handler.setLevel(fileLevel)

        cls.logger.addHandler(file_handler)
        # Put console logger at the end (to avoid saving _colors_ to file)
        cls.logger.handlers.reverse()

        # Hide werkzeug messages below WARNING
        logging.getLogger("werkzeug").setLevel(logging.WARNING)

        cls.initialized = True

    @classmethod
    def _dump(cls, level: str, msg: str, logger: Optional[str] = None):
        if cls.initialized:
            log = cls.logger if logger is None else logging.getLogger(logger)
            method = getattr(log, level.lower())
            method(msg)
        else:
            print(f"[Log not initialized][{level}] {msg}")

    @classmethod
    def D(cls, msg, logger: Optional[str] = None): cls._dump('DEBUG', msg, logger)

    @classmethod
    def I(cls, msg, logger: Optional[str] = None): cls._dump('INFO', msg, logger)

    @classmethod
    def W(cls, msg, logger: Optional[str] = None): cls._dump('WARNING', msg, logger)

    @classmethod
    def E(cls, msg, logger: Optional[str] = None): cls._dump('ERROR', msg, logger)

    @classmethod
    def C(cls, msg, logger: Optional[str] = None): cls._dump('CRITICAL', msg, logger)

    @staticmethod
    def State(condition: bool) -> str:
        return f'{"En" if condition else "Dis"}abled'

    @classmethod
    def Log(cls, level: Union[Level, str], msg: str, logger: Optional[str] = None):
        if isinstance(level, str):
            level = Level[level]

        if level == Level.DEBUG: cls.D(msg, logger)
        if level == Level.INFO: cls.I(msg, logger)
        if level == Level.WARNING: cls.W(msg, logger)
        if level == Level.ERROR: cls.E(msg, logger)
        if level == Level.CRITICAL: cls.C(msg, logger)

    @classmethod
    def GetTraceback(cls):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        return traceback.format_exception(exc_type, exc_value, exc_traceback)

    @classmethod
    def Traceback(cls, logger: Optional[str] = None):
        lines = cls.GetTraceback()
        for line in lines:
            Log.D(line, logger)

    @classmethod
    def OpenLogFile(cls, identifier: str, filePath: Optional[str] = None) -> str:
        filePath = join(cls.outFolder, f'{identifier}.log') if filePath is None else filePath

        logger = logging.getLogger(identifier)
        logger.setLevel(logging.DEBUG)

        fileHandler = logging.FileHandler(filename=filePath, mode='a+', encoding='utf-8')
        fileHandler.setFormatter(logging.Formatter(cls.FILE_FORMAT))
        fileHandler.setLevel(logging.DEBUG)

        logger.addHandler(fileHandler)
        Log.D('[File Opened]', identifier)
        return filePath

    @classmethod
    def CloseLogFile(cls, identifier):
        Log.D('[Closing File]', identifier)
        logger = logging.getLogger(identifier)
        for handler in logger.handlers:  # type: logging.Handler
            logger.removeHandler(handler)
            handler.flush()
            handler.close()

    @classmethod
    def RetrieveLog(cls, file: str = None, tail: Optional[int] = None) -> List[str]:
        res = []
        file = join(cls.outFolder, f'{cls.mainLogName}.log') if file is None else file
        with open(file, 'rb') as log:
            for line in log:
                res.append(line.decode(encoding='utf-8', errors='replace'))

        if tail is not None and tail < len(res):
            start = len(res) - tail
            return res[start:len(res)]
        return res
