from core.exceptions.exceptions import InvalidEnvVarError
from core.logs.log_handler import console_logger
from core.utils.os import get_dotenv_var

FLASK_ENV_OPTIONS = ["production", "development"]
LOG_LEVEL_OPTIONS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class FlaskConf(object):
    """
    Flask Settings
    """

    DEBUG = False
    ERROR_404_HELP = False
    TESTING = False

    FLASK_ENV = get_dotenv_var(key="FLASK_ENV")
    SECRET_KEY = get_dotenv_var(key="SECRET_KEY") or "key123"
    TNLCM_CONSOLE_LOG_LEVEL = get_dotenv_var(key="TNLCM_CONSOLE_LOG_LEVEL")
    TRIAL_NETWORK_LOG_LEVEL = get_dotenv_var(key="TRIAL_NETWORK_LOG_LEVEL")

    if FLASK_ENV not in FLASK_ENV_OPTIONS:
        raise InvalidEnvVarError(
            variable="FLASK_ENV", possible_values=FLASK_ENV_OPTIONS
        )
    if TNLCM_CONSOLE_LOG_LEVEL not in LOG_LEVEL_OPTIONS:
        raise InvalidEnvVarError(
            variable="TNLCM_CONSOLE_LOG_LEVEL", possible_values=LOG_LEVEL_OPTIONS
        )
    if TRIAL_NETWORK_LOG_LEVEL not in LOG_LEVEL_OPTIONS:
        raise InvalidEnvVarError(
            variable="TRIAL_NETWORK_LOG_LEVEL", possible_values=LOG_LEVEL_OPTIONS
        )

    config_dict = {
        "ERROR_404_HELP": ERROR_404_HELP,
        "DEBUG": DEBUG,
        "FLASK_ENV": FLASK_ENV,
        "SECRET_KEY": SECRET_KEY,
        "TESTING": TESTING,
        "TNLCM_CONSOLE_LOG_LEVEL": TNLCM_CONSOLE_LOG_LEVEL,
        "TRIAL_NETWORK_LOG_LEVEL": TRIAL_NETWORK_LOG_LEVEL,
    }

    console_logger.info(message=f"Load Flask configuration: {config_dict}")
