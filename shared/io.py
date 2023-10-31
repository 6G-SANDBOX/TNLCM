from os.path import abspath, join, isdir, isfile, exists
from os import listdir, makedirs
from shutil import copytree, copy
from typing import List


class IO:
    @staticmethod
    def ListFiles(path) -> List[str]:
        return [join(path, f) for f in listdir(path) if isfile(join(path, f))]

    @staticmethod
    def ListFolders(path) -> List[str]:
        return [join(path, f) for f in listdir(path) if isdir(join(path, f))]

    @staticmethod
    def ListFileNames(path) -> List[str]:
        return [f for f in listdir(path) if isfile(join(path, f))]

    @staticmethod
    def ListFolderNames(path) -> List[str]:
        return [f for f in listdir(path) if isdir(join(path, f))]

    @staticmethod
    def GetAllFiles(path) -> List[str]:
        res = []

        for folder in IO.ListFolders(path):
            res.extend(IO.GetAllFiles(folder))
        for file in IO.ListFiles(path):
            res.append(file)

        return res

    @staticmethod
    def EnsureFolder(folder) -> bool:
        """Returns True if the folder already exists"""
        folder = abspath(folder)
        if not exists(folder):
            makedirs(folder, exist_ok=True)
            return False
        return True

    @staticmethod
    def CopyFolderContents(source, target):
        folders = IO.ListFolderNames(source)
        for folder in folders:
            src = join(source, folder)
            tgt = join(target, folder)
            copytree(src, tgt)

        files = IO.ListFileNames(source)
        for file in files:
            src = join(source, file)
            tgt = join(target, file)
            copy(src, tgt)
