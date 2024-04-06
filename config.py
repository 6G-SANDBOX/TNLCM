import os

class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY") or "clave"
    ERROR_404_HELP = os.getenv("ERROR_404_HELP")