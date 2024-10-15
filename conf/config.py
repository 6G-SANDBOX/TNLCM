import os

from core.logs.log_handler import log_handler
from conf import MailSettings, MongoDBSettings

class Config(object):
    """
    Flask Settings
    """
    
    log_handler.info("Load Flask configuration")
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY") or "clave"
    ERROR_404_HELP = False

    ME_CONFIG_MONGODB_URL = MongoDBSettings.ME_CONFIG_MONGODB_URL
    
    MAIL_SERVER = MailSettings.MAIL_SERVER
    MAIL_PORT = MailSettings.MAIL_PORT
    MAIL_USE_TLS = MailSettings.MAIL_USE_TLS
    MAIL_USE_SSL = MailSettings.MAIL_USE_SSL
    MAIL_USERNAME = MailSettings.MAIL_USERNAME
    MAIL_PASSWORD = MailSettings.MAIL_PASSWORD

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True