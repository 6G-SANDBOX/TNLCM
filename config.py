import os

from core.logs.log_handler import log_handler

class Config(object):
    log_handler.info("Load configuration file")

    # Flask configuration
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY") or "clave"
    ERROR_404_HELP = False

    # Mongo configuration
    MONGO_URI = os.getenv("MONGO_URI")

    # Mail configuration
    def str_to_bool(s):
        return s.lower() in ["true", "1", "yes"]

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_USE_TLS = str_to_bool(os.getenv("MAIL_USE_TLS", "False"))
    MAIL_USE_SSL = str_to_bool(os.getenv("MAIL_USE_SSL", "False"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True