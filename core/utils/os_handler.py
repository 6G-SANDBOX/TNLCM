import os

def get_dotenv_var(key: str) -> str:
    """
    Get dotenv variable
    
    :param key: dotenv variable key, ``str``
    :return: dotenv variable value, ``str``
    """
    return os.getenv(key)

def current_directory() -> str:
    """
    Current directory
    
    :return: current directory, ``str``
    """
    return os.getcwd()

def join_path(*args) -> str:
    """
    Join path
    
    :param args: path to join, ``str``
    :return: joined path, ``str``
    """
    return os.path.join(current_directory(), *args)

def exists_path(path: str) -> bool:
    """
    Check if path exists
    
    :param path: path to check, ``str``
    :return: path exists, ``bool``
    """
    return os.path.exists(path)

def make_directory(path: str) -> None:
    """
    Make directory
    
    :param path: directory path, ``str``
    """
    os.makedirs(path)