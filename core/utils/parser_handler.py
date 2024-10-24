import base64

def decode_base64(encoded_data: str) -> str:
    """
    Decode a Base64 encoded string

    :param encoded_data: the Base64 encoded string to be decoded, ``str``
    :return: the decoded data as bytes, ``str``
    """
    return base64.b64decode(encoded_data).decode("utf-8")