import os

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import UndefinedEnvVariableError

class TnlcmSettings:
    """
    TNLCM Settings
    """

    TNLCM_ADMIN_USER = os.getenv("TNLCM_ADMIN_USER")
    TNLCM_ADMIN_PASSWORD = os.getenv("TNLCM_ADMIN_PASSWORD")
    TNLCM_ADMIN_EMAIL = os.getenv("TNLCM_ADMIN_EMAIL")
    TNLCM_HOST = os.getenv("TNLCM_HOST")
    TNLCM_PORT = os.getenv("TNLCM_PORT")
    TNLCM_CALLBACK = os.getenv("TNLCM_CALLBACK")
    missing_variables = []
    if not TNLCM_ADMIN_USER:
        missing_variables.append("TNLCM_ADMIN_USER")
    if not TNLCM_ADMIN_PASSWORD:
        missing_variables.append("TNLCM_ADMIN_PASSWORD")
    if not TNLCM_ADMIN_EMAIL:
        missing_variables.append("TNLCM_ADMIN_EMAIL")
    if not TNLCM_HOST:
        missing_variables.append("TNLCM_HOST")
    if not TNLCM_PORT:
        missing_variables.append("TNLCM_PORT")
    if not TNLCM_CALLBACK:
        missing_variables.append("TNLCM_CALLBACK")
    if missing_variables:
        raise UndefinedEnvVariableError(missing_variables)
    
    TITLE = "Trial Network Lifecycle Manager - TNLCM"
    VERSION = "0.4.1"
    DESCRIPTION = ("[[6G-SANDBOX] TNLCM](https://github.com/6G-SANDBOX/TNLCM)")
    DOC = False

    TRIAL_NETWORKS_DIRECTORY = os.path.join(os.getcwd(), "core", "trial_networks")
    if not os.path.exists(TRIAL_NETWORKS_DIRECTORY):
        os.makedirs(TRIAL_NETWORKS_DIRECTORY)

    config_dict = {
        "TNLCM_ADMIN_USER": TNLCM_ADMIN_USER,
        "TNLCM_ADMIN_PASSWORD": TNLCM_ADMIN_PASSWORD,
        "TNLCM_ADMIN_EMAIL": TNLCM_ADMIN_EMAIL,
        "TNLCM_HOST": TNLCM_HOST,
        "TNLCM_PORT": TNLCM_PORT,
        "TNLCM_CALLBACK": TNLCM_CALLBACK,
        "TRIAL_NETWORKS_DIRECTORY": TRIAL_NETWORKS_DIRECTORY
    }
    
    log_handler.info(f"Load TNLCM configuration: {config_dict}")