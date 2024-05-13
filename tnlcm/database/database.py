from mongoengine import connect, disconnect

def init_db(app):
    # disconnect(alias="tnlcm-database-alias")
    connect(
        alias="tnlcm-database-alias",
        host=app.config["MONGO_URI"]
    )