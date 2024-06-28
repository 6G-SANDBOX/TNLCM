import os

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import UndefinedEnvVariableError

class JenkinsSettings:
    """
    Jenkins Settings
    """
    
    log_handler.info("Load Jenkins configuration")

    JENKINS_HOST = os.getenv("JENKINS_HOST")
    JENKINS_PORT = os.getenv("JENKINS_PORT")
    JENKINS_URL = os.getenv("JENKINS_URL")
    JENKINS_USERNAME = os.getenv("JENKINS_USERNAME")
    JENKINS_PASSWORD = os.getenv("JENKINS_PASSWORD")
    JENKINS_TOKEN = os.getenv("JENKINS_TOKEN")
    JENKINS_JOB_DEPLOY = os.getenv("JENKINS_JOB_DEPLOY")
    JENKINS_JOB_DESTROY = os.getenv("JENKINS_JOB_DESTROY")
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
    if not JENKINS_JOB_DEPLOY:
        missing_variables.append("JENKINS_JOB_DEPLOY")
    if not JENKINS_JOB_DESTROY:
        missing_variables.append("JENKINS_JOB_DESTROY")
    if missing_variables:
        raise UndefinedEnvVariableError(missing_variables)