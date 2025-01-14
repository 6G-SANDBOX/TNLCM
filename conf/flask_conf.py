from conf.mail import MailSettings
from conf.mongodb import MongoDBSettings
from core.logs.log_handler import tnlcm_log_handler
from core.utils.os_handler import get_dotenv_var
from core.exceptions.exceptions_handler import InvalidEnvVariableError

class FlaskConf(object):
    """
    Flask Settings
    """
    
    DEBUG = False
    TESTING = False
    SECRET_KEY = get_dotenv_var(key="SECRET_KEY") or "clave"
    ERROR_404_HELP = False

    ME_CONFIG_MONGODB_URL = MongoDBSettings.ME_CONFIG_MONGODB_URL
    FLASK_ENV = get_dotenv_var(key="FLASK_ENV")
    if FLASK_ENV != "production" and FLASK_ENV != "development":
        raise InvalidEnvVariableError("FLASK_ENV", ["production", "development"])
    if not MailSettings.TWO_FACTOR_AUTH:
        config_dict = {
            "DEBUG": DEBUG,
            "TESTING": TESTING,
            "SECRET_KEY": SECRET_KEY,
            "ERROR_404_HELP": ERROR_404_HELP,
            "ME_CONFIG_MONGODB_URL": ME_CONFIG_MONGODB_URL
        }
    else:
        MAIL_SERVER = MailSettings.MAIL_SERVER
        MAIL_PORT = MailSettings.MAIL_PORT
        MAIL_USE_TLS = MailSettings.MAIL_USE_TLS
        MAIL_USE_SSL = MailSettings.MAIL_USE_SSL
        MAIL_USERNAME = MailSettings.MAIL_USERNAME
        MAIL_PASSWORD = MailSettings.MAIL_PASSWORD

        config_dict = {
            "DEBUG": DEBUG,
            "TESTING": TESTING,
            "SECRET_KEY": SECRET_KEY,
            "ERROR_404_HELP": ERROR_404_HELP,
            "ME_CONFIG_MONGODB_URL": ME_CONFIG_MONGODB_URL,
            "MAIL_SERVER": MAIL_SERVER,
            "MAIL_PORT": MAIL_PORT,
            "MAIL_USE_TLS": MAIL_USE_TLS,
            "MAIL_USE_SSL": MAIL_USE_SSL,
            "MAIL_USERNAME": MAIL_USERNAME,
            "MAIL_PASSWORD": MAIL_PASSWORD,
        }

    tnlcm_log_handler.info(f"Load Flask configuration: {config_dict}")