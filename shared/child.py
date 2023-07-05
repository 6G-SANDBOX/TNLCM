from .log import Log, Level
from .io import IO
from os.path import realpath
import threading
from tempfile import TemporaryDirectory
from typing import List


class Child:
    TEMP_BASE = 'Temp'

    def __init__(self, name: str, tempFolder: TemporaryDirectory = None):
        self.name = name
        self.thread = threading.Thread(
            target=self._runWrapper,
            daemon=True
        )
        self.hasStarted = False
        self.hasFailed = False
        self.hasFinished = False
        self.stopRequested = False
        self.TempFolder = None if tempFolder is None else tempFolder.name
        self.tempFolderIsExternal = (tempFolder is not None)
        self.LogFile = None

    def Broadcast(self, level: Level, msg: str):
        Log.Log(level, f'[{self.name}{self.thread.ident}] {msg}')

    def Log(self, level: Level, msg: str):
        print(f"{self.name}: {msg}")
        Log.Log(level, msg, logger=self.name)

    def Start(self):
        self.thread.start()

    def RequestStop(self):
        self.stopRequested = True

    def _runWrapper(self):
        def _innerRun():
            self.LogFile = Log.OpenLogFile(self.name)
            self.Log(Level.DEBUG, f'[Using temporal folder: {self.TempFolder}]')
            self.hasStarted = True
            try:
                self.Run()
            except Exception as e:
                self.hasFailed = True
                self.Log(Level.ERROR, f'[Exception while running ({self.name}): {e}]')
                trace = Log.GetTraceback()
                for line in trace:
                    self.Log(Level.DEBUG, line.strip())
            finally:
                self.hasFinished = True
                Log.CloseLogFile(self.name)

        if self.tempFolderIsExternal:
            _innerRun()
        else:
            basefolder = realpath(self.TEMP_BASE)
            IO.EnsureFolder(basefolder)
            with TemporaryDirectory(dir=basefolder) as tempFolder:
                self.TempFolder = tempFolder
                _innerRun()

    def Run(self):
        raise NotImplementedError()

    def RetrieveLog(self, tail: int = None) -> List[str]:
        if not self.hasStarted: return []
        return Log.RetrieveLog(self.LogFile, tail)
