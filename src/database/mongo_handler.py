import os

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

COLLECTIONS = ["trial_network"]

class MongoHandler:

    def __init__(self):
        try:
            self.database = os.getenv("MONGO_DATABASE")
            self.uri = os.getenv("MONGO_URI")
            self.client = MongoClient(self.uri)
            self.db = self.client[self.database]
        except Exception as e:
            raise Exception(e)

    def disconnect(self):
        try:
            self.client.close()
        except Exception as e:
            raise Exception(e)
    
    def insert_data(self, collection_name, doc):
        if collection_name in COLLECTIONS:
            try:
                collection = self.db[collection_name]
                collection.insert_one(doc)
            except ConnectionFailure:
                raise ConnectionFailure("Unable to connect to database")
            except Exception as e:
                raise Exception(e)
        else:
            raise ValueError("Collection not found") 
    
    def find_data(self, collection_name, query=None, projection=None):
        if collection_name in COLLECTIONS:
            result = None
            try:
                collection = self.db[collection_name]
                result = list(collection.find(query, projection))
            except ConnectionFailure:
                raise ConnectionFailure("Unable to connect to database")
            except Exception as e:
                raise Exception(e)
            if result:
                return result
            else:
                raise ValueError("No results found in the database")
        else:
            raise ValueError("Collection not found")
        
    
    def update_data(self, collection_name, query, update):
        if collection_name in COLLECTIONS:
            try:
                collection = self.db[collection_name]
                collection.update_one(query, update)
            except ConnectionFailure:
                raise ConnectionFailure("Unable to connect to database")
            except Exception as e:
                raise Exception(e)
        else:
            raise ValueError("Collection not found")