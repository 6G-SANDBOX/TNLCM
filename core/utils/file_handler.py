import json
import yaml

def load_yaml(file_path: str, mode: str, encoding: str) -> dict:
    """
    Load data from a YAML file

    :param file_path: the path to the YAML file to be loaded, ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the YAML file, ``dict``
    """
    with open(file_path, mode=mode, encoding=encoding) as yaml_file:
        return yaml.safe_load(yaml_file)

def load_file(file_path: str, mode: str, encoding: str) -> str:
    """
    Load the content from a file
    
    :param file_path: the path to the file to be loaded (e.g. txt, markdown), ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the file, ``str``
    """
    with open(file_path, mode=mode, encoding=encoding) as file:
        return file.read()

def save_json(data, file_path: str) -> None:
    """
    Save the data to a JSON file
    
    :param data: the data to be saved (must be JSON serializable)
    :param file_path: the file path where the data will be saved, ``str``
    """
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

def save_yaml(data, file_path: str) -> None:
    """
    Save the data to a YAML file
    
    :param data: the data to be saved (must be serializable to YAML)
    :param file_path: The file path where the data will be saved, ``str``
    """
    with open(file_path, "w") as yaml_file:
        yaml.safe_dump(data, yaml_file, default_flow_style=False)

def save_file(data: str, file_path: str, mode: str, encoding: str) -> None:
    """
    Save the given data in a file
    
    :param data: the text to be saved (e.g. txt, markdown), ``str``
    :param file_path: the file path where the data will be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    """
    with open(file_path, mode=mode, encoding=encoding) as file:
        file.write(data)