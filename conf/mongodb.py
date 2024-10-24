import os

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import UndefinedEnvVariableError

class MongoDBSettings:
    """
    MongoDB Settings
    """

    MONGO_HOST = os.getenv("MONGO_HOST")
    MONGO_PORT = os.getenv("MONGO_PORT")
    MONGO_DATABASE = os.getenv("MONGO_DATABASE")
    ME_CONFIG_MONGODB_ADMINUSERNAME = os.getenv("ME_CONFIG_MONGODB_ADMINUSERNAME")
    ME_CONFIG_MONGODB_ADMINPASSWORD = os.getenv("ME_CONFIG_MONGODB_ADMINPASSWORD")
    ME_CONFIG_MONGODB_ENABLE_ADMIN = os.getenv("ME_CONFIG_MONGODB_ENABLE_ADMIN")
    ME_CONFIG_MONGODB_URL = os.getenv("ME_CONFIG_MONGODB_URL")
    ME_CONFIG_BASICAUTH = os.getenv("ME_CONFIG_BASICAUTH")
    ME_CONFIG_SITE_SESSIONSECRET = os.getenv("ME_CONFIG_SITE_SESSIONSECRET")
    VCAP_APP_HOST = os.getenv("VCAP_APP_HOST")
    ME_CONFIG_BASICAUTH_USERNAME = os.getenv("ME_CONFIG_BASICAUTH_USERNAME")
    ME_CONFIG_BASICAUTH_PASSWORD = os.getenv("ME_CONFIG_BASICAUTH_PASSWORD")
    missing_variables = []
    if not MONGO_HOST:
        missing_variables.append("MONGO_HOST")
    if not MONGO_PORT:
        missing_variables.append("MONGO_PORT")
    if not MONGO_DATABASE:
        missing_variables.append("MONGO_DATABASE")
    if not ME_CONFIG_MONGODB_ADMINUSERNAME:
        missing_variables.append("ME_CONFIG_MONGODB_ADMINUSERNAME")
    if not ME_CONFIG_MONGODB_ADMINPASSWORD:
        missing_variables.append("ME_CONFIG_MONGODB_ADMINPASSWORD")
    if not ME_CONFIG_MONGODB_ENABLE_ADMIN:
        missing_variables.append("ME_CONFIG_MONGODB_ENABLE_ADMIN")
    if not ME_CONFIG_MONGODB_URL:
        missing_variables.append("ME_CONFIG_MONGODB_URL")
    if not ME_CONFIG_BASICAUTH:
        missing_variables.append("ME_CONFIG_BASICAUTH")
    if not ME_CONFIG_SITE_SESSIONSECRET:
        missing_variables.append("ME_CONFIG_SITE_SESSIONSECRET")
    if not VCAP_APP_HOST:
        missing_variables.append("VCAP_APP_HOST")
    if not ME_CONFIG_BASICAUTH_USERNAME:
        missing_variables.append("ME_CONFIG_BASICAUTH_USERNAME")
    if not ME_CONFIG_BASICAUTH_PASSWORD:
        missing_variables.append("ME_CONFIG_BASICAUTH_PASSWORD")
    if missing_variables:
        raise UndefinedEnvVariableError(missing_variables)
    
    config_dict = {
        "MONGO_HOST": MONGO_HOST,
        "MONGO_PORT": MONGO_PORT,
        "MONGO_DATABASE": MONGO_DATABASE,
        "ME_CONFIG_MONGODB_ADMINUSERNAME": ME_CONFIG_MONGODB_ADMINUSERNAME,
        "ME_CONFIG_MONGODB_ADMINPASSWORD": ME_CONFIG_MONGODB_ADMINPASSWORD,
        "ME_CONFIG_MONGODB_ENABLE_ADMIN": ME_CONFIG_MONGODB_ENABLE_ADMIN,
        "ME_CONFIG_MONGODB_URL": ME_CONFIG_MONGODB_URL,
        "ME_CONFIG_BASICAUTH": ME_CONFIG_BASICAUTH,
        "ME_CONFIG_SITE_SESSIONSECRET": ME_CONFIG_SITE_SESSIONSECRET,
        "VCAP_APP_HOST": VCAP_APP_HOST,
        "ME_CONFIG_BASICAUTH_USERNAME": ME_CONFIG_BASICAUTH_USERNAME,
        "ME_CONFIG_BASICAUTH_PASSWORD": ME_CONFIG_BASICAUTH_PASSWORD
    }

    log_handler.info(f"Load MongoDB configuration: {config_dict}")