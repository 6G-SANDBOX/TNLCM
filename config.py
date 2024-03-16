import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "clave"
    FLASK_ENV = os.getenv("FLASK_ENV")
    ERROR_404_HELP = os.getenv("ERROR_404_HELP")