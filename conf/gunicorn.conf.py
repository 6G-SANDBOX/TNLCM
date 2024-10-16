from conf import TnlcmSettings

# Number of worker processes to handle requests
workers = 3

# Address and port Gunicorn will bind to
bind = f"0.0.0.0:{TnlcmSettings.TNLCM_PORT}"

# Request timeout in seconds (35 minutes). The time of the component that takes the longest time to deploy
timeout = 2100

# WSGI entry point for the application
wsgi_app = "app:app"

# Log level for output verbosity
loglevel = "info"

# Maximum number of pending connections
backlog = 1024