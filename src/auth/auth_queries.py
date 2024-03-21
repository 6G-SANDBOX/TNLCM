from src.database.mongo_handler import MongoHandler

def create_mongo_client():
    mongo_client = MongoHandler()
    return mongo_client

def get_current_user_from_jwt(jwt_identity):
    mongo_client = create_mongo_client()
    query = {"username": jwt_identity}
    projection = {"_id": 0}
    user = mongo_client.find_data(collection_name="trial_network_user", query=query, projection=projection)
    mongo_client.disconnect()
    return user