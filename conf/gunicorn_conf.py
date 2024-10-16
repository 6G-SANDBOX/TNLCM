import os

from conf import TnlcmSettings
from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import UndefinedEnvVariableError

# Number of worker processes to handle requests
workers = os.getenv("GUNICORN_WORKERS")

# Log level for output verbosity
loglevel = os.getenv("GUNICORN_LOG_LEVEL")

# Request timeout in seconds (35 minutes). The time of the component that takes the longest time to deploy
timeout = os.getenv("GUNICORN_TIMEOUT")

# Address and port Gunicorn will bind to
bind = f"0.0.0.0:{TnlcmSettings.TNLCM_PORT}"

# WSGI entry point for the application
wsgi_app = "app:app"

# Maximum number of pending connections
backlog = 1024

missing_variables = []
if not workers:
    missing_variables.append("GUNICORN_WORKERS")
if not workers:
    missing_variables.append("GUNICORN_LOG_LEVEL")
if not workers:
    missing_variables.append("GUNICORN_TIMEOUT")
if missing_variables:
    raise UndefinedEnvVariableError(missing_variables)

config_dict = {
    "WORKERS": workers,
    "BIND": bind,
    "TIMEOUT": timeout,
    "LOGLEVEL": loglevel,
    "BACKLOG": backlog,
}

log_handler.info(f"Load gunicorn configuration: {config_dict}")