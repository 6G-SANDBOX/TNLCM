import json
import tomlkit

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

def load_yaml(file_path: str, mode: str = "rt", encoding: str = "utf-8") -> dict:
    """
    Load data from a YAML file

    :param file_path: the path to the YAML file to be loaded, ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the YAML file, ``dict``
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    with open(file=file_path, mode=mode, encoding=encoding) as yaml_file:
        return yaml.load(yaml_file)

def loads_toml(file_path: str, mode: str = "rt", encoding: str = "utf-8") -> dict:
    """
    Load data from a TOML file

    :param file_path: the path to the TOML file to be loaded, ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the TOML file, ``dict``
    """
    with open(file=file_path, mode=mode, encoding=encoding) as toml_file:
        return tomlkit.loads(toml_file.read())

def load_file(file_path: str, mode: str = "rt", encoding: str = "utf-8") -> str:
    """
    Load the content from a file
    
    :param file_path: the path to the file to be loaded (e.g. txt, markdown), ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    :return: the data loaded from the file, ``str``
    """
    with open(file_path, mode=mode, encoding=encoding) as file:
        return file.read()

def save_json(data, file_path: str, mode: str = "wt", encoding: str = "utf-8") -> None:
    """
    Save the data to a JSON file
    
    :param data: the data to be saved (must be JSON serializable)
    :param file_path: the file path where the data will be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. wt, wb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    """
    with open(file=file_path, mode=mode, encoding=encoding) as json_file:
        json.dump(data, json_file, indent=4)

def save_yaml(data, file_path: str, mode: str = "wt", encoding: str = "utf-8") -> None:
    """
    Save the data to a YAML file, preserving quotes using ruamel.yaml
    
    :param data: the data to be saved (must be serializable to YAML)
    :param file_path: The file path where the data will be saved, ``str``
    """
    yaml = YAML()
    yaml.preserve_quotes = True

    def convert_to_double_quoted(data):
        if isinstance(data, dict):
            return {k: convert_to_double_quoted(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [convert_to_double_quoted(v) for v in data]
        elif isinstance(data, str):
            return DoubleQuotedScalarString(data)
        else:
            return data

    data = convert_to_double_quoted(data)

    with open(file=file_path, mode=mode, encoding=encoding) as yaml_file:
        yaml.dump(data=data, stream=yaml_file)

def save_file(data: str, file_path: str, mode: str = "wt", encoding: str = "utf-8") -> None:
    """
    Save the given data in a file
    
    :param data: the text to be saved (e.g. txt, markdown), ``str``
    :param file_path: the file path where the data will be saved, ``str``
    :param mode: the mode in which the file is opened (e.g. rt, rb), ``str``
    :param encoding: the file encoding (e.g. utf-8), ``str``
    """
    with open(file=file_path, mode=mode, encoding=encoding) as file:
        file.write(data)