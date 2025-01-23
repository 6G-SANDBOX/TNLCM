from core.logs.log_handler import tnlcm_log_handler
from core.utils.os_handler import get_dotenv_var
from core.exceptions.exceptions_handler import InvalidEnvVariableError, UndefinedEnvVariableError

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

    TWO_FACTOR_AUTH = get_dotenv_var(key="TWO_FACTOR_AUTH")
    if TWO_FACTOR_AUTH != "True" and TWO_FACTOR_AUTH != "False":
        raise InvalidEnvVariableError("TWO_FACTOR_AUTH", ["True", "False"])
    TWO_FACTOR_AUTH=str_to_bool(TWO_FACTOR_AUTH)
    if not TWO_FACTOR_AUTH:
        tnlcm_log_handler.info("Two Factor Authentication is disabled")
    else:
        MAIL_SERVER = get_dotenv_var(key="MAIL_SERVER")
        MAIL_PORT = get_dotenv_var(key="MAIL_PORT")
        MAIL_USE_TLS = get_dotenv_var(key="MAIL_USE_TLS")
        MAIL_USE_SSL = get_dotenv_var(key="MAIL_USE_SSL")
        MAIL_USERNAME = get_dotenv_var(key="MAIL_USERNAME")
        MAIL_PASSWORD = get_dotenv_var(key="MAIL_PASSWORD")
        missing_variables = []
        if not MAIL_USERNAME:
            missing_variables.append("MAIL_USERNAME")
        if not MAIL_PASSWORD:
            missing_variables.append("MAIL_PASSWORD")
        if missing_variables:
            raise UndefinedEnvVariableError(missing_variables)

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

        tnlcm_log_handler.info(f"Load Mail configuration: {config_dict}")