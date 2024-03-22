import os

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from src.exceptions.exceptions_handler import VariablesNotDefinedInEnvError, MongoDBConnectionError, MongoDBCollectionError

COLLECTIONS = ["trial_network", "trial_network_user"]

class MongoHandler:

    def __init__(self):
        """Constructor"""
        self.database = os.getenv("MONGO_DATABASE")
        self.uri = os.getenv("MONGO_URI")
        if self.database and self.uri:
            try:
                self.client = MongoClient(self.uri)
                self.db = self.client[self.database]
            except ConnectionFailure as e:
                raise MongoDBConnectionError(f"Unable to establish connection to the '{self.database}' database", 500)
        else:
            raise VariablesNotDefinedInEnvError("Add the value of the variables MONGO_DATABASE and MONGO_URI in the .env file", 500)

    def disconnect(self):
        """Delete connection"""
        self.client.close()
    
    def insert_data(self, collection_name, doc):
        """Insert data into the database"""
        if collection_name in COLLECTIONS:
            try:
                collection = self.db[collection_name]
                collection.insert_one(doc)
            except ConnectionFailure:
                raise MongoDBConnectionError(f"Unable to connect to database '{self.database}'", 500)
        else:
            raise MongoDBCollectionError(f"Collection '{collection_name}' not found in database '{self.database}'", 404)
    
    def find_data(self, collection_name, query=None, projection=None):
        """Find data in the database"""
        if collection_name in COLLECTIONS:
            try:
                collection = self.db[collection_name]
                return list(collection.find(query, projection))
            except ConnectionFailure:
                raise MongoDBConnectionError(f"Unable to connect to database '{self.database}'", 500)
        else:
            raise MongoDBCollectionError(f"Collection '{collection_name}' not found in database '{self.database}'", 404) 

    def update_data(self, collection_name, query=None, projection=None):
        """Update data in the database"""
        if collection_name in COLLECTIONS:
            try:
                collection = self.db[collection_name]
                collection.update_one(query, projection)
            except ConnectionFailure:
                raise MongoDBConnectionError(f"Unable to connect to database '{self.database}'", 500)
        else:
            MongoDBCollectionError(f"Collection '{collection_name}' not found in database '{self.database}'", 404)
    
    def delete_data(self, collection_name, query=None, projection=None):
        """Delete data in the database"""
        if collection_name in COLLECTIONS:
            try:
                collection = self.db[collection_name]
                collection.delete_one(query, projection)
            except ConnectionFailure:
                raise MongoDBConnectionError(f"Unable to connect to database '{self.database}'", 500)
        else:
            MongoDBCollectionError(f"Collection '{collection_name}' not found in database '{self.database}'", 404)