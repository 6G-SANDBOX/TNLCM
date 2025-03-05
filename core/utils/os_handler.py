import os

def current_directory() -> str:
    """
    Current directory
    
    :return: current directory, ``str``
    """
    return os.getcwd()

def exists_path(path: str) -> bool:
    """
    Check if path exists
    
    :param path: path to check, ``str``
    :return: path exists, ``bool``
    """
    return os.path.exists(path)

def get_dotenv_var(key: str) -> str:
    """
    Get dotenv variable
    
    :param key: dotenv variable key, ``str``
    :return: dotenv variable value, ``str``
    """
    return os.getenv(key)

def is_directory(path: str) -> bool:
    """
    Check if path is directory
    
    :param path: path to check, ``str``
    :return: path is directory, ``bool``
    """
    return os.path.isdir(path)

def join_path(*args) -> str:
    """
    Join path
    
    :param args: path to join, ``str``
    :return: joined path, ``str``
    """
    return os.path.join(*args)

def list_directory(path: str) -> list[str]:
    """
    List directory
    
    :param path: directory path, ``str``
    :return: list of files in directory, ``list[str]``
    """
    return os.listdir(path)

def make_directory(path: str) -> None:
    """
    Make directory
    
    :param path: directory path, ``str``
    """
    os.makedirs(path)

def get_absolute_path(__file__) -> str:
    """
    Absolute path
    
    :param path: path to convert to absolute, ``str``
    :return: absolute path, ``str``
    """
    return os.path.dirname(os.path.abspath(__file__))
