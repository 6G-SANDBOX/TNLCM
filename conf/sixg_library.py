import os

from conf import RepositorySettings
from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import UndefinedEnvVariableError, GitCloneError

class SixGLibrarySettings:
    """
    6G-Library Settings
    """

    log_handler.info("Load 6G-Library configuration")

    GITHUB_6G_LIBRARY_HTTPS_URL = os.getenv("GITHUB_6G_LIBRARY_HTTPS_URL")
    GITHUB_6G_LIBRARY_BRANCH = os.getenv("GITHUB_6G_LIBRARY_BRANCH")
    GITHUB_6G_LIBRARY_REPOSITORY_NAME = os.getenv("GITHUB_6G_LIBRARY_REPOSITORY_NAME")
    missing_variables = []
    if not GITHUB_6G_LIBRARY_HTTPS_URL:
        missing_variables.append("GITHUB_6G_LIBRARY_HTTPS_URL")
    if not GITHUB_6G_LIBRARY_BRANCH:
        missing_variables.append("GITHUB_6G_LIBRARY_BRANCH")
    if not GITHUB_6G_LIBRARY_REPOSITORY_NAME:
        missing_variables.append("GITHUB_6G_LIBRARY_REPOSITORY_NAME")
    if missing_variables:
        raise UndefinedEnvVariableError(missing_variables)
    if not RepositorySettings.is_github_repo(GITHUB_6G_LIBRARY_HTTPS_URL):
        raise GitCloneError(f"Repository url specified '{GITHUB_6G_LIBRARY_HTTPS_URL}' is not correct", 500)