from mongoengine import connect

def init_db(app):
    connect(
        alias="tnlcm-database-alias",
        host=app.config["MONGO_URI"]
    )