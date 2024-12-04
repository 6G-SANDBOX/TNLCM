import os

from core.logs.log_handler import log_handler
from conf import MailSettings, MongoDBSettings
from core.exceptions.exceptions_handler import UndefinedEnvVariableError

class FlaskConf(object):
    """
    Flask Settings
    """
    
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY") or "clave"
    ERROR_404_HELP = False

    ME_CONFIG_MONGODB_URL = MongoDBSettings.ME_CONFIG_MONGODB_URL
    FLASK_ENV=os.getenv("FLASK_ENV")
    if FLASK_ENV != "production" and FLASK_ENV != "development":
        raise UndefinedEnvVariableError(["FLASK_ENV"])
    TWO_FACTOR_AUTH=MailSettings.TWO_FACTOR_AUTH
    if not TWO_FACTOR_AUTH:
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

    log_handler.info(f"Load Flask configuration: {config_dict}")