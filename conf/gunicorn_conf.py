from conf.tnlcm import TnlcmSettings
from core.logs.log_handler import tnlcm_log_handler
from core.utils.os_handler import get_dotenv_var

# Number of worker processes to handle requests
workers = get_dotenv_var(key="GUNICORN_WORKERS")

# Log level for output verbosity
loglevel = get_dotenv_var(key="GUNICORN_LOG_LEVEL")

# Request timeout in seconds (35 minutes). The time of the component that takes the longest time to deploy
timeout = get_dotenv_var(key="GUNICORN_TIMEOUT")

# Address and port Gunicorn will bind to
bind = f"0.0.0.0:{TnlcmSettings.TNLCM_PORT}"

# WSGI entry point for the application
wsgi_app = "app:app"

# Maximum number of pending connections
backlog = 1024

config_dict = {
    "WORKERS": workers,
    "BIND": bind,
    "TIMEOUT": timeout,
    "LOGLEVEL": loglevel,
    "BACKLOG": backlog,
}

tnlcm_log_handler.info(f"Load gunicorn configuration: {config_dict}")