from core.logs.log_handler import tnlcm_log_handler
from core.utils.os_handler import get_dotenv_var

class LibrarySettings:
    """
    Library Settings
    """

    LIBRARY_HTTPS_URL = get_dotenv_var(key="LIBRARY_HTTPS_URL")
    LIBRARY_BRANCH = get_dotenv_var(key="LIBRARY_BRANCH")
    LIBRARY_REPOSITORY_NAME = get_dotenv_var(key="LIBRARY_REPOSITORY_NAME")
    
    config_dict = {
        "LIBRARY_HTTPS_URL": LIBRARY_HTTPS_URL,
        "LIBRARY_BRANCH": LIBRARY_BRANCH,
        "LIBRARY_REPOSITORY_NAME": LIBRARY_REPOSITORY_NAME,
    }

    tnlcm_log_handler.info(f"Load Library configuration: {config_dict}")