import os

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import UndefinedEnvVariableError, InvalidEnvVariableValueError

JENKINS_DEPLOYMENT_SITES = ["uma", "athens", "fokus"]

class JenkinsSettings:
    """Jenkins Settings"""
    
    log_handler.info("Load Jenkins configuration")

    JENKINS_URL = os.getenv("JENKINS_URL")
    JENKINS_USERNAME = os.getenv("JENKINS_USERNAME")
    JENKINS_PASSWORD = os.getenv("JENKINS_PASSWORD")
    JENKINS_TOKEN = os.getenv("JENKINS_TOKEN")
    JENKINS_PIPELINE_FOLDER = os.getenv("JENKINS_PIPELINE_FOLDER")
    JENKINS_PIPELINE_NAME = os.getenv("JENKINS_PIPELINE_NAME")
    JENKINS_DEPLOYMENT_SITE = os.getenv("JENKINS_DEPLOYMENT_SITE")
    TNLCM_CALLBACK = os.getenv("TNLCM_CALLBACK")
    missing_variables = []
    if not JENKINS_URL:
        missing_variables.append("JENKINS_URL")
    if not JENKINS_USERNAME:
        missing_variables.append("JENKINS_USERNAME")
    if not JENKINS_PASSWORD:
        missing_variables.append("JENKINS_PASSWORD")
    if not JENKINS_TOKEN:
        missing_variables.append("JENKINS_TOKEN")
    if not JENKINS_PIPELINE_NAME:
        missing_variables.append("JENKINS_PIPELINE_NAME")
    if not JENKINS_DEPLOYMENT_SITE:
        missing_variables.append("JENKINS_DEPLOYMENT_SITE")
    if not TNLCM_CALLBACK:
        missing_variables.append("TNLCM_CALLBACK")
    if missing_variables:
        raise UndefinedEnvVariableError(missing_variables)
    JENKINS_DEPLOYMENT_SITE = JENKINS_DEPLOYMENT_SITE.lower()
    if JENKINS_DEPLOYMENT_SITE not in JENKINS_DEPLOYMENT_SITES:
        raise InvalidEnvVariableValueError(f"The value of the variable 'JENKINS_DEPLOYMENT_SITE' should be {', '.join(JENKINS_DEPLOYMENT_SITES)} in the .env file")
    JENKINS_PIPELINE = JENKINS_PIPELINE_NAME if not JENKINS_PIPELINE_FOLDER else f"{JENKINS_PIPELINE_FOLDER}/{JENKINS_PIPELINE_NAME}"