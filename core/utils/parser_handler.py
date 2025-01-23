from ansible.parsing.vault import VaultLib, VaultSecret
from ansible.constants import DEFAULT_VAULT_ID_MATCH
from base64 import b64decode, b64encode
from ruamel.yaml import YAML

def ansible_decrypt(encrypted_data: str, token: str) -> None:
    """
    Decrypt a file using Ansible Vault

    :param encrypted_data: the data to be decrypted, ``str``
    :param token: the token used for decrypt data, ``str``
    """
    secret = token.encode("utf-8")
    vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(secret))])
    return vault.decrypt(encrypted_data)

def ansible_encrypt(data: str, token: str) -> None:
    """
    Encrypt a file using Ansible Vault

    :param encrypted_data: the data to be encrypted, ``str``
    :param token: the token used for encrypt data, ``str``
    """
    secret = token.encode("utf-8")
    vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(secret))])
    return vault.encrypt(data)

def decode_base64(encoded_data: str) -> str:
    """
    Decode a base64 encoded string

    :param encoded_data: the base64 encoded string to be decoded, ``str``
    :return: the decoded data as bytes, ``str``
    """
    return b64decode(encoded_data).decode("utf-8")

def encode_base64(data: str) -> str:
    """
    Encode a string to base64

    :param data: the data to be encoded, ``str``
    :return: the base64 encoded data, ``str``
    """
    return b64encode(data.encode("utf-8")).decode("utf-8")

def yaml_to_dict(data: str) -> dict:
    """
    Load data from a YAML string

    :param data: the YAML string to be loaded, ``str``
    :return: the data loaded from the YAML string, ``dict``
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    return yaml.load(data)