from core.logs.log_handler import console_logger
from core.utils.os import get_dotenv_var


class LibrarySettings:
    """
    Library Settings
    """

    LIBRARY_BRANCH = get_dotenv_var(key="LIBRARY_BRANCH")
    LIBRARY_HTTPS_URL = get_dotenv_var(key="LIBRARY_HTTPS_URL")
    LIBRARY_REPOSITORY_NAME = get_dotenv_var(key="LIBRARY_REPOSITORY_NAME")

    config_dict = {
        "LIBRARY_BRANCH": LIBRARY_BRANCH,
        "LIBRARY_HTTPS_URL": LIBRARY_HTTPS_URL,
        "LIBRARY_REPOSITORY_NAME": LIBRARY_REPOSITORY_NAME,
    }

    console_logger.info(f"Load Library configuration: {config_dict}")
