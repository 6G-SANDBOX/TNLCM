import os

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid, ConfigurationError, PyMongoError

COLLECTIONS = ["trial_network"]

class MongoHandler:

    def __init__(self):
        self.database = os.getenv("MONGO_DATABASE")
        self.uri = os.getenv("MONGO_URI")
        if self.database and self.uri:
            try:
                self.client = MongoClient(self.uri)
                self.db = self.client[self.database]
            except PyMongoError as e:
                raise PyMongoError(e)
        else:
            raise ConfigurationError("Add the value of the variables MONGO_DATABASE and MONGO_URI in the .env file")

    def disconnect(self):
        try:
            self.client.close()
        except PyMongoError as e:
            raise PyMongoError(e)
    
    def insert_data(self, collection_name, doc):
        if collection_name in COLLECTIONS:
            try:
                collection = self.db[collection_name]
                collection.insert_one(doc)
            except ConnectionFailure:
                raise ConnectionFailure(f"Unable to connect to database '{self.database}'")
        else:
            raise CollectionInvalid(f"Collection '{collection_name}' not found in database '{self.database}'") 
    
    def find_data(self, collection_name, query=None, projection=None):
        if collection_name in COLLECTIONS:
            try:
                collection = self.db[collection_name]
                return list(collection.find(query, projection))
            except ConnectionFailure:
                raise ConnectionFailure(f"Unable to connect to database '{self.database}'")
        else:
            raise CollectionInvalid(f"Collection '{collection_name}' not found in database '{self.database}'")
        
    
    def update_data(self, collection_name, query, projection):
        if collection_name in COLLECTIONS:
            try:
                collection = self.db[collection_name]
                collection.update_one(query, projection)
            except ConnectionFailure:
                raise ConnectionFailure(f"Unable to connect to database '{self.database}'")
        else:
            raise CollectionInvalid(f"Collection '{collection_name}' not found in database '{self.database}'")