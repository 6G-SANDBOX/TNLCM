from core.logs.log_handler import tnlcm_log_handler
from core.utils.os_handler import get_dotenv_var
from core.exceptions.exceptions_handler import UndefinedEnvVariableError

class SitesSettings:
    """
    Sites Settings
    """

    SITES_HTTPS_URL = get_dotenv_var(key="SITES_HTTPS_URL")
    SITES_BRANCH = get_dotenv_var(key="SITES_BRANCH")
    SITES_REPOSITORY_NAME = get_dotenv_var(key="SITES_REPOSITORY_NAME")
    SITES_TOKEN = get_dotenv_var(key="SITES_TOKEN")
    missing_variables = []
    if not SITES_TOKEN:
        missing_variables.append("SITES_TOKEN")
    if missing_variables:
        raise UndefinedEnvVariableError(missing_variables)
    
    config_dict = {
        "SITES_HTTPS_URL": SITES_HTTPS_URL,
        "SITES_BRANCH": SITES_BRANCH,
        "SITES_REPOSITORY_NAME": SITES_REPOSITORY_NAME,
        "SITES_TOKEN": SITES_TOKEN,
    }
    
    tnlcm_log_handler.info(f"Load Sites configuration: {config_dict}")