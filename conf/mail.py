import os

from email_validator import validate_email, EmailNotValidError

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import UndefinedEnvVariableError, InvalidEmailError

def str_to_bool(s: str) -> bool:
    """
    Convert a string representation of truth values to a boolean

    :param s: string to be converted to a boolean, ``str``
    :return: boolean representation of the string, ``bool``
    """
    return s.lower() in ["true", "1", "yes"]

class MailSettings:
    """
    Mail Settings
    """

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    missing_variables = []
    if not MAIL_SERVER:
        missing_variables.append("MAIL_SERVER")
    if not MAIL_PORT:
        missing_variables.append("MAIL_PORT")
    if not MAIL_USE_TLS:
        missing_variables.append("MAIL_USE_TLS")
    if not MAIL_USE_SSL:
        missing_variables.append("MAIL_USE_SSL")
    if not MAIL_USERNAME:
        missing_variables.append("MAIL_USERNAME")
    if not MAIL_PASSWORD:
        missing_variables.append("MAIL_PASSWORD")
    if missing_variables:
        raise UndefinedEnvVariableError(missing_variables)
    try:
        valid = validate_email(MAIL_USERNAME)
        email = valid.email
    except EmailNotValidError:
        raise InvalidEmailError("Invalid 'MAIL_USERNAME' entered in .env file", 500)
    MAIL_PORT = int(MAIL_PORT)
    MAIL_USE_TLS = str_to_bool(MAIL_USE_TLS)
    MAIL_USE_SSL = str_to_bool(MAIL_USE_SSL)

    config_dict = {
        "MAIL_SERVER": MAIL_SERVER,
        "MAIL_PORT": MAIL_PORT,
        "MAIL_USE_TLS": MAIL_USE_TLS,
        "MAIL_USE_SSL": MAIL_USE_SSL,
        "MAIL_USERNAME": MAIL_USERNAME,
        "MAIL_PASSWORD": MAIL_PASSWORD
    }

    log_handler.info(f"Load Mail configuration: {config_dict}")