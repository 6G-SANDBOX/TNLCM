import base64
from typing import Dict

from ruamel.yaml import YAML

from core.exceptions.exceptions_handler import Base64Error
from core.utils.cli import run_command
from core.utils.file import save_file
from core.utils.os import TEMP_DIRECTORY_PATH, join_path

SITES_TOKEN_PATH = join_path(TEMP_DIRECTORY_PATH, "sites_token")


def ansible_decrypt(data_path: str, token: str) -> None:
    """
    Decrypt a file using Ansible Vault

    :param data_path: the path to the file to be decrypted, ``str``
    :param token: the token to decrypt the file, ``str``
    """
    save_file(
        file_path=SITES_TOKEN_PATH,
        data=token,
    )
    run_command(
        command=f"ansible-vault decrypt {data_path} --vault-password={SITES_TOKEN_PATH}"
    )


def ansible_encrypt(data_path: str, token: str) -> None:
    """
    Encrypt a file using Ansible Vault

    :param data_path: the path to the file to be encrypted, ``str``
    :param token: the token to encrypt the file, ``str``
    """
    save_file(
        file_path=SITES_TOKEN_PATH,
        data=token,
    )
    run_command(
        command=f"ansible-vault encrypt {data_path} --vault-password={SITES_TOKEN_PATH}"
    )


def is_base64(data: str) -> bool:
    """
    Check if a string is Base64 encoded

    :param data: the string to be checked, ``str``
    :return: whether the string is Base64 encoded or not, ``bool``
    """
    try:
        base64.b64decode(s=data, validate=True)
        return True
    except Exception:
        return False


def decode_base64(encoded_data: str) -> str:
    """
    Decode a Base64 encoded string

    :param encoded_data: the Base64 encoded string to be decoded, ``str``
    :return: the decoded data as bytes, ``str``
    """
    if not is_base64(data=encoded_data):
        raise Base64Error(message=f"Invalid Base64 encoded data: {encoded_data}")
    return base64.b64decode(s=encoded_data).decode(encoding="utf-8")


def encode_base64(data: str) -> str:
    """
    Encode a string to Base64

    :param data: the string to be encoded, ``str``
    :return: the Base64 encoded string, ``str``
    """
    return base64.b64encode(s=data.encode(encoding="utf-8")).decode(encoding="utf-8")


def yaml_to_dict(data: str) -> Dict:
    """
    Load data from a YAML string

    :param data: the YAML string to be loaded, ``str``
    :return: the data loaded from the YAML string, ``Dict``
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    return yaml.load(stream=data)
