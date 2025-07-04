import os
import shutil
from typing import List

PROJECT_PATH = os.getcwd()
CORE_PATH = os.path.join(PROJECT_PATH, "core")
SITES_PATH = os.path.join(CORE_PATH, "sites")
TEMP_PATH = os.path.join(PROJECT_PATH, ".temp")
DOTENV_DEV_PATH = os.path.join(PROJECT_PATH, ".env.dev")
DOTENV_PATH = os.path.join(PROJECT_PATH, ".env")
PYPROJECT_TOML_PATH = os.path.join(PROJECT_PATH, "pyproject.toml")
SITES_TOKEN_PATH = os.path.join(SITES_PATH, "sites_token")
TRIAL_NETWORKS_PATH = os.path.join(CORE_PATH, "trial_networks")
REPORT_DIR = os.path.join(CORE_PATH, "library/report")
TEMPLATES_DIR = os.path.join(REPORT_DIR, "templates")
CSS_FILENAME = os.path.join(TEMPLATES_DIR, "style.css")
COVER_IMAGE = os.path.join(REPORT_DIR, "sandbox.png")
FONT_FILENAME = os.path.join(REPORT_DIR, "fonts/georgia/georgia.ttf")
WATERMARK_IMAGE = os.path.join(REPORT_DIR, "sandbox-25.png")

def exist_directory(path: str) -> bool:
    """
    Check if the directory exists

    :param path: the path to the directory, ``str``
    :return: whether the directory exists, ``bool``
    """
    return os.path.exists(path=path)


def get_absolute_path(__file__) -> str:
    """
    Absolute path

    :param __file__: the file, ``str``
    :return: absolute path, ``str``
    """
    return os.path.dirname(os.path.abspath(__file__))


def get_dotenv_var(key: str) -> str:
    """
    Get the value of an environment variable

    :param key: the name of the environment variable, ``str``
    :return: the value of the environment variable, ``str``
    """
    return os.getenv(key=key)


def is_directory(path: str) -> bool:
    """
    Check if the path is a directory

    :param path: the path to the directory, ``str``
    :return: whether the path is a directory, ``bool``
    """
    return os.path.isdir(path)


def is_file(path: str) -> bool:
    """
    Check if the path is a file

    :param path: the path to the file, ``str``
    :return: whether the path is a file, ``bool``
    """
    return os.path.isfile(path=path)


def join_path(*args) -> str:
    """
    Join the paths

    :param args: the paths to be joined, ``List[str]
    :return: the joined path, ``str``
    """
    return os.path.join(*args)


def list_dirs_no_hidden(path: str) -> List[str]:
    """
    List the directories in the directory

    :param path: the path to the directory, ``str``
    :return: the list of files and directories, ``List[str]``
    """
    directories = []
    for directory in os.listdir(path=path):
        if is_directory(path=join_path(path, directory)) and not directory.startswith(
            "."
        ):
            directories.append(directory)
    return sorted(directories)


def list_files_no_hidden(path: str) -> List[str]:
    """
    List the files in the directory

    :param path: the path to the directory, ``str``
    :return: the list of files, ``List[str]``
    """
    files = []
    for file in os.listdir(path=path):
        if is_file(path=join_path(path, file)) and not file.startswith("."):
            files.append(file)
    return sorted(files)


def make_directory(path: str) -> None:
    """
    Make the directory

    :param path: the path to the directory, ``str``
    """
    os.makedirs(name=path, exist_ok=True)


def remove_directory(path: str) -> None:
    """
    Remove the directory

    :param path: the path to the directory, ``str``
    """
    if is_directory(path=path):
        shutil.rmtree(path)


def remove_file(path: str) -> None:
    """
    Remove the file

    :param path: the path to the file, ``str``
    """
    if os.path.exists(path=path):
        os.remove(path=path)


def rename_directory(old_path: str, new_path: str) -> None:
    """
    Rename the directory

    :param old_path: the old path to the directory, ``str``
    :param new_path: the new path to the directory, ``str``
    """
    if is_directory(path=old_path):
        shutil.move(src=old_path, dst=new_path)
