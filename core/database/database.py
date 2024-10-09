from flask import Flask
from mongoengine import connect, disconnect

def init_db(app: Flask) -> None:
    """
    Initializes MongoDB connection using the configuration from the given Flask application

    :param app: Flask application instance containing the configuration for the MongoDB connection, ``Flask``
    """
    # disconnect(alias="tnlcm-database-alias")
    connect(
        alias="tnlcm-database-alias",
        host=app.config["MONGO_URI"]
    )