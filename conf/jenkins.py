import os

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import UndefinedEnvVariableError

def str_to_bool(s):
    return s.lower() in ["true", "1", "yes"]

class JenkinsSettings:
    """Jenkins Settings"""
    
    log_handler.info("Load Jenkins configuration")

    JENKINS_IP = os.getenv("JENKINS_IP")
    JENKINS_PORT = os.getenv("JENKINS_PORT")
    JENKINS_URL = os.getenv("JENKINS_URL")
    JENKINS_USERNAME = os.getenv("JENKINS_USERNAME")
    JENKINS_PASSWORD = os.getenv("JENKINS_PASSWORD")
    JENKINS_TOKEN = os.getenv("JENKINS_TOKEN")
    JENKINS_JOB_NAME = os.getenv("JENKINS_JOB_NAME")
    TNLCM_CALLBACK = os.getenv("TNLCM_CALLBACK")
    missing_variables = []
    if not JENKINS_IP:
        missing_variables.append("JENKINS_IP")
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
    if not JENKINS_JOB_NAME:
        missing_variables.append("JENKINS_JOB_NAME")
    if not TNLCM_CALLBACK:
        missing_variables.append("TNLCM_CALLBACK")
    if missing_variables:
        raise UndefinedEnvVariableError(missing_variables)