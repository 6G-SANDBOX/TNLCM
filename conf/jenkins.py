from core.exceptions.exceptions import UndefinedEnvVarError
from core.logs.log_handler import console_logger
from core.utils.os import get_dotenv_var


class JenkinsSettings:
    """
    Jenkins Settings
    """

    JENKINS_DESTROY_PIPELINE = get_dotenv_var(key="JENKINS_DESTROY_PIPELINE")
    JENKINS_DEPLOY_PIPELINE = get_dotenv_var(key="JENKINS_DEPLOY_PIPELINE")
    JENKINS_HOST = get_dotenv_var(key="JENKINS_HOST")
    JENKINS_PASSWORD = get_dotenv_var(key="JENKINS_PASSWORD")
    JENKINS_PORT = get_dotenv_var(key="JENKINS_PORT")
    JENKINS_TNLCM_DIRECTORY = get_dotenv_var(key="JENKINS_TNLCM_DIRECTORY")
    JENKINS_TOKEN = get_dotenv_var(key="JENKINS_TOKEN")
    JENKINS_URL = get_dotenv_var(key="JENKINS_URL")
    JENKINS_USERNAME = get_dotenv_var(key="JENKINS_USERNAME")

    missing_variables = []
    if not JENKINS_HOST:
        missing_variables.append("JENKINS_HOST")
    if not JENKINS_PASSWORD:
        missing_variables.append("JENKINS_PASSWORD")
    if not JENKINS_TOKEN:
        missing_variables.append("JENKINS_TOKEN")
    if not JENKINS_USERNAME:
        missing_variables.append("JENKINS_USERNAME")
    if missing_variables:
        raise UndefinedEnvVarError(missing_variables)

    config_dict = {
        "JENKINS_DESTROY_PIPELINE": JENKINS_DESTROY_PIPELINE,
        "JENKINS_DEPLOY_PIPELINE": JENKINS_DEPLOY_PIPELINE,
        "JENKINS_HOST": JENKINS_HOST,
        "JENKINS_PASSWORD": JENKINS_PASSWORD,
        "JENKINS_PORT": JENKINS_PORT,
        "JENKINS_TNLCM_DIRECTORY": JENKINS_TNLCM_DIRECTORY,
        "JENKINS_TOKEN": JENKINS_TOKEN,
        "JENKINS_URL": JENKINS_URL,
        "JENKINS_USERNAME": JENKINS_USERNAME,
    }

    console_logger.info(message=f"Load Jenkins configuration: {config_dict}")
