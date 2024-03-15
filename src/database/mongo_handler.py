import os

from pymongo import MongoClient

class MongoHandler:

    def __init__(self):
        self.host = os.getenv("MONGO_HOST")
        self.port = os.getenv("MONGO_PORT")
        self.username = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        self.password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
        self.database = os.getenv("MONGO_DATABASE")
        self.uri = os.getenv("MONGO_URI")
        self.client = MongoClient(self.uri)
        self.db = self.client[self.database]

    def disconnect(self):
        try:
            if self.client:
                self.client.close()
        except Exception as e:
            raise Exception("Failed to disconnect to MongoDB")
    
    def insert_data(self, collection_name, doc):
        try:
            collection = self.db[collection_name]
            collection.insert_one(doc)
        except Exception as e:
            raise Exception(e)
    
    def find_data(self, collection_name, query=None, projection=None):
        try:
            collection = self.db[collection_name]
            result = collection.find(query, projection)
            return list(result)
        except Exception as e:
            raise Exception(e)
    
    def update_data(self, collection_name, query, update):
        try:
            collection = self.db[collection_name]
            collection.update_one(query, update)
        except Exception as e:
            raise Exception(e)