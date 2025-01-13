from core.logs.log_handler import log_handler
from core.utils.os_handler import get_dotenv_var
from core.exceptions.exceptions_handler import UndefinedEnvVariableError

class JenkinsSettings:
    """
    Jenkins Settings
    """

    JENKINS_HOST = get_dotenv_var(key="JENKINS_HOST")
    JENKINS_PORT = get_dotenv_var(key="JENKINS_PORT")
    JENKINS_URL = get_dotenv_var(key="JENKINS_URL")
    JENKINS_USERNAME = get_dotenv_var(key="JENKINS_USERNAME")
    JENKINS_PASSWORD = get_dotenv_var(key="JENKINS_PASSWORD")
    JENKINS_TOKEN = get_dotenv_var(key="JENKINS_TOKEN")
    JENKINS_DEPLOY_PIPELINE = get_dotenv_var(key="JENKINS_DEPLOY_PIPELINE")
    JENKINS_DESTROY_PIPELINE = get_dotenv_var(key="JENKINS_DESTROY_PIPELINE")
    missing_variables = []
    if not JENKINS_HOST:
        missing_variables.append("JENKINS_HOST")
    if not JENKINS_URL:
        missing_variables.append("JENKINS_URL")
    if not JENKINS_USERNAME:
        missing_variables.append("JENKINS_USERNAME")
    if not JENKINS_PASSWORD:
        missing_variables.append("JENKINS_PASSWORD")
    if not JENKINS_TOKEN:
        missing_variables.append("JENKINS_TOKEN")
    if missing_variables:
        raise UndefinedEnvVariableError(missing_variables)
    
    config_dict = {
        "JENKINS_HOST": JENKINS_HOST,
        "JENKINS_PORT": JENKINS_PORT,
        "JENKINS_URL": JENKINS_URL,
        "JENKINS_USERNAME": JENKINS_USERNAME,
        "JENKINS_PASSWORD": JENKINS_PASSWORD,
        "JENKINS_TOKEN": JENKINS_TOKEN,
        "JENKINS_DEPLOY_PIPELINE": JENKINS_DEPLOY_PIPELINE,
        "JENKINS_DESTROY_PIPELINE": JENKINS_DESTROY_PIPELINE,
    }

    log_handler.info(f"Load Jenkins configuration: {config_dict}")