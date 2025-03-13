from mongoengine import connect

from conf.mongodb import MongoDBSettings


def init_db() -> None:
    """
    Initializes MongoDB connection
    """
    connect(alias="tnlcm-database-alias", host=MongoDBSettings.ME_CONFIG_MONGODB_URL)
