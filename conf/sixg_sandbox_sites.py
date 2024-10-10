import os

from conf import RepositorySettings
from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import UndefinedEnvVariableError, GitCloneError

class SixGSandboxSitesSettings:
    """
    6G-Sandbox-Sites Settings
    """

    log_handler.info("Load 6G-Sandbox-Sites configuration")

    GITHUB_6G_SANDBOX_SITES_HTTPS_URL = os.getenv("GITHUB_6G_SANDBOX_SITES_HTTPS_URL")
    GITHUB_6G_SANDBOX_SITES_BRANCH = os.getenv("GITHUB_6G_SANDBOX_SITES_BRANCH")
    GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME = os.getenv("GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME")
    SITES_TOKEN = os.getenv("SITES_TOKEN")
    missing_variables = []
    if not GITHUB_6G_SANDBOX_SITES_HTTPS_URL:
        missing_variables.append("GITHUB_6G_SANDBOX_SITES_HTTPS_URL")
    if not GITHUB_6G_SANDBOX_SITES_BRANCH:
        missing_variables.append("GITHUB_6G_SANDBOX_SITES_BRANCH")
    if not GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME:
        missing_variables.append("GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME")
    if not SITES_TOKEN:
        missing_variables.append("SITES_TOKEN")
    if missing_variables:
        raise UndefinedEnvVariableError(missing_variables)
    if not RepositorySettings.is_github_repo(GITHUB_6G_SANDBOX_SITES_HTTPS_URL):
        raise GitCloneError(f"Repository url specified '{GITHUB_6G_SANDBOX_SITES_HTTPS_URL}' is not correct", 500)