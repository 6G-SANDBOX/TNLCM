from core.logs.log_handler import tnlcm_log_handler
from core.utils.os_handler import current_directory, exists_path, get_dotenv_var, join_path, make_directory
from core.utils.file_handler import load_toml
from core.exceptions.exceptions_handler import UndefinedEnvVariableError

class TnlcmSettings:
    """
    TNLCM Settings
    """

    TNLCM_ADMIN_USER = get_dotenv_var(key="TNLCM_ADMIN_USER")
    TNLCM_ADMIN_PASSWORD = get_dotenv_var(key="TNLCM_ADMIN_PASSWORD")
    TNLCM_ADMIN_EMAIL = get_dotenv_var(key="TNLCM_ADMIN_EMAIL")
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
        raise UndefinedEnvVariableError(missing_variables)
    
    TITLE = "Trial Network Lifecycle Manager - TNLCM"
    DESCRIPTION = ("[[6G-SANDBOX] TNLCM](https://github.com/6G-SANDBOX/TNLCM)")
    DOC = False
    VERSION = load_toml(file_path=join_path(current_directory(), "pyproject.toml"))["project"]["version"]

    TRIAL_NETWORKS_DIRECTORY: str = join_path(current_directory(), "core", "trial_networks")
    if not exists_path(path=TRIAL_NETWORKS_DIRECTORY):
        make_directory(path=TRIAL_NETWORKS_DIRECTORY)

    config_dict = {
        "TNLCM_ADMIN_USER": TNLCM_ADMIN_USER,
        "TNLCM_ADMIN_PASSWORD": TNLCM_ADMIN_PASSWORD,
        "TNLCM_ADMIN_EMAIL": TNLCM_ADMIN_EMAIL,
        "TNLCM_HOST": TNLCM_HOST,
        "TNLCM_PORT": TNLCM_PORT,
        "TNLCM_CALLBACK": TNLCM_CALLBACK,
        "TRIAL_NETWORKS_DIRECTORY": TRIAL_NETWORKS_DIRECTORY
    }
    
    tnlcm_log_handler.info(f"Load TNLCM configuration: {config_dict}")