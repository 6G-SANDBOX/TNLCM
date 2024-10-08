import os

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import UndefinedEnvVariableError

class TnlcmSettings:
    """
    TNLCM Settings
    """

    log_handler.info("Load TNLCM configuration")

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
    
    TITLE = "Trial Network Life Cycle Manager - TNLCM"
    VERSION = "0.3.1"
    DESCRIPTION = ("""
    Welcome to the Trial Network Life Cycle Manager (TNLCM) API! This powerful tool facilitates the management and orchestration of network life cycles, designed specifically for the cutting-edge 6G Sandbox project.

    Explore our documentation and contribute to the project's development on GitHub.\n"""
    "[6G-Sandbox - TNLCM Repository](https://github.com/6G-SANDBOX/TNLCM)")
    DOC = False