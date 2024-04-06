import os

class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY") or "clave"
    ERROR_404_HELP = os.getenv("ERROR_404_HELP")

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")