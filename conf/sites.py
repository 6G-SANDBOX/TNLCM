from core.exceptions.exceptions import UndefinedEnvVarError
from core.logs.log_handler import console_logger
from core.utils.os import get_dotenv_var


class SitesSettings:
    """
    Sites Settings
    """

    SITES_BRANCH = get_dotenv_var(key="SITES_BRANCH")
    SITES_HTTPS_URL = get_dotenv_var(key="SITES_HTTPS_URL")
    SITES_REPOSITORY_NAME = get_dotenv_var(key="SITES_REPOSITORY_NAME")
    SITES_DEPLOYMENT_SITE = get_dotenv_var(key="SITES_DEPLOYMENT_SITE")
    SITES_DEPLOYMENT_SITE_TOKEN = get_dotenv_var(key="SITES_DEPLOYMENT_SITE_TOKEN")

    missing_variables = []
    if not SITES_BRANCH:
        missing_variables.append("SITES_BRANCH")
    if not SITES_DEPLOYMENT_SITE:
        missing_variables.append("SITES_DEPLOYMENT_SITE")
    if not SITES_DEPLOYMENT_SITE_TOKEN:
        missing_variables.append("SITES_DEPLOYMENT_SITE_TOKEN")
    if missing_variables:
        raise UndefinedEnvVarError(missing_variables=missing_variables)

    config_dict = {
        "SITES_BRANCH": SITES_BRANCH,
        "SITES_HTTPS_URL": SITES_HTTPS_URL,
        "SITES_REPOSITORY_NAME": SITES_REPOSITORY_NAME,
        "SITES_DEPLOYMENT_SITE": SITES_DEPLOYMENT_SITE,
        "SITES_DEPLOYMENT_SITE_TOKEN": SITES_DEPLOYMENT_SITE_TOKEN,
    }

    console_logger.info(message=f"Load Sites configuration: {config_dict}")
