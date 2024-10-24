import os

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import UndefinedEnvVariableError

class JenkinsSettings:
    """
    Jenkins Settings
    """

    JENKINS_HOST = os.getenv("JENKINS_HOST")
    JENKINS_PORT = os.getenv("JENKINS_PORT")
    JENKINS_URL = os.getenv("JENKINS_URL")
    JENKINS_USERNAME = os.getenv("JENKINS_USERNAME")
    JENKINS_PASSWORD = os.getenv("JENKINS_PASSWORD")
    JENKINS_TOKEN = os.getenv("JENKINS_TOKEN")
    JENKINS_DEPLOY_PIPELINE = os.getenv("JENKINS_DEPLOY_PIPELINE")
    JENKINS_DESTROY_PIPELINE = os.getenv("JENKINS_DESTROY_PIPELINE")
    missing_variables = []
    if not JENKINS_HOST:
        missing_variables.append("JENKINS_HOST")
    if not JENKINS_PORT:
        missing_variables.append("JENKINS_PORT")
    if not JENKINS_URL:
        missing_variables.append("JENKINS_URL")
    if not JENKINS_USERNAME:
        missing_variables.append("JENKINS_USERNAME")
    if not JENKINS_PASSWORD:
        missing_variables.append("JENKINS_PASSWORD")
    if not JENKINS_TOKEN:
        missing_variables.append("JENKINS_TOKEN")
    if not JENKINS_DEPLOY_PIPELINE:
        missing_variables.append("JENKINS_DEPLOY_PIPELINE")
    if not JENKINS_DESTROY_PIPELINE:
        missing_variables.append("JENKINS_DESTROY_PIPELINE")
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