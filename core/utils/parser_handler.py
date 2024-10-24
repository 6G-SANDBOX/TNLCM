import yaml
import base64

def yaml_to_dict(file_path: str) -> dict:
    """
    Convert a YAML file to a Python dictionary
    
    :param file_path: the path to the YAML file to be converted, ``str``.
    :return: the content of the YAML file as a dictionary, ``dict``.
    """
    with open(file_path, "r", encoding="utf-8") as yaml_file:
        return yaml.safe_load(yaml_file)

def decode_base64(encoded_data: str) -> str:
    """
    Decode a Base64 encoded string

    :param encoded_data: the Base64 encoded string to be decoded, ``str``
    :return: the decoded data as bytes, ``str``
    """
    return base64.b64decode(encoded_data).decode("utf-8")