import multiprocessing

from conf.tnlcm import TnlcmSettings
from core.logs.log_handler import console_logger
from core.utils.os import get_dotenv_var

# Maximum number of pending connections
backlog = 1024

# Address and port Gunicorn will bind to
bind = f"0.0.0.0:{TnlcmSettings.TNLCM_PORT}"

# Request timeout in seconds (35 minutes). The time of the component that takes the longest time to deploy
timeout = get_dotenv_var(key="GUNICORN_TIMEOUT")

# Number of worker processes to handle requests
workers = multiprocessing.cpu_count() * 2 + 1

# WSGI entry point for the application
wsgi_app = "app:app"

config_dict = {
    "BACKLOG": backlog,
    "BIND": bind,
    "TIMEOUT": timeout,
    "WORKERS": workers,
}

console_logger.info(f"Load gunicorn configuration: {config_dict}")
