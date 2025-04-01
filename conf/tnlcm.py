from core.exceptions.exceptions import UndefinedEnvVarError
from core.logs.log_handler import console_logger
from core.utils.os import get_dotenv_var


class TnlcmSettings:
    """
    TNLCM Settings
    """

    TNLCM_ADMIN_EMAIL = get_dotenv_var(key="TNLCM_ADMIN_EMAIL")
    TNLCM_ADMIN_PASSWORD = get_dotenv_var(key="TNLCM_ADMIN_PASSWORD")
    TNLCM_ADMIN_USER = get_dotenv_var(key="TNLCM_ADMIN_USER")
    TNLCM_HOST = get_dotenv_var(key="TNLCM_HOST")
    TNLCM_PORT = get_dotenv_var(key="TNLCM_PORT")
    TNLCM_CALLBACK = get_dotenv_var(key="TNLCM_CALLBACK")

    missing_variables = []
    if not TNLCM_ADMIN_USER:
        missing_variables.append("TNLCM_ADMIN_USER")
    if not TNLCM_ADMIN_PASSWORD:
        missing_variables.append("TNLCM_ADMIN_PASSWORD")
    if not TNLCM_HOST:
        missing_variables.append("TNLCM_HOST")
    if missing_variables:
        raise UndefinedEnvVarError(missing_variables=missing_variables)

    config_dict = {
        "TNLCM_ADMIN_EMAIL": TNLCM_ADMIN_EMAIL,
        "TNLCM_ADMIN_PASSWORD": TNLCM_ADMIN_PASSWORD,
        "TNLCM_ADMIN_USER": TNLCM_ADMIN_USER,
        "TNLCM_HOST": TNLCM_HOST,
        "TNLCM_PORT": TNLCM_PORT,
        "TNLCM_CALLBACK": TNLCM_CALLBACK,
    }

    console_logger.info(message=f"Load TNLCM configuration: {config_dict}")
