from flask import Flask
from mongoengine import connect

def init_db(app: Flask) -> None:
    """
    Initializes MongoDB connection using the configuration from the given Flask application

    :param app: Flask application instance containing the configuration for the MongoDB connection, ``Flask``
    """
    connect(
        alias="tnlcm-database-alias",
        host=app.config["ME_CONFIG_MONGODB_URL"]
    )