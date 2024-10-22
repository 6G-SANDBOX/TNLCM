import json
import yaml

def load_yaml(file_path: str, mode: str, encoding: str) -> dict:
    """
    Load data from a YAML file

    :param file_path: the path to the YAML file to be loaded, ``str``
    :return: the data loaded from the YAML file, ``dict``
    """
    with open(file_path, mode=mode, encoding=encoding) as yaml_file:
        return yaml.safe_load(yaml_file)

def load_markdown(file_path: str) -> str:
    """
    Load the content from a Markdown file
    
    :param file_path: the path to the Markdown file to be loaded, ``str``
    :return: the data loaded from the Markdown file, ``str``
    """
    with open(file_path, "r", encoding="utf-8") as md_file:
        return md_file.read()

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
        yaml.dump(data, yaml_file, default_flow_style=False)

def append_markdown(data: str, file_path: str) -> None:
    """
    Save the given data to a markdown file
    
    :param data: the text to be saved (markdown formatted), ``str``
    :param file_path: the file path where the data will be saved, ``str``
    """
    with open(file_path, "a") as md_file:
        md_file.write(data)