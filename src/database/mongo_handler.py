import os

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from src.exceptions.exceptions_handler import VariablesNotDefinedInEnvError, MongoDBConnectionError, MongoDBCollectionError

COLLECTIONS = ["trial_networks", "trial_networks_templates", "verification_tokens", "users"]

class MongoHandler:

    def __init__(self):
        """Constructor"""
        self.database = os.getenv("MONGO_DATABASE")
        self.uri = os.getenv("MONGO_URI")
        missing_variables = []
        if not self.database:
            missing_variables.append("MONGO_DATABASE")
        if not self.uri:
            missing_variables.append("MONGO_URI")
        if missing_variables:
            raise VariablesNotDefinedInEnvError(f"Add the value of the variables {", ".join(missing_variables)} in the .env file", 500)
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.database]
        except ConnectionFailure:
            raise MongoDBConnectionError(f"Unable to establish connection to the '{self.database}' database", 408)

    def disconnect(self):
        """Delete connection"""
        self.client.close()
    
    def find_data(self, collection_name, query=None, projection=None):
        """Find data in the database"""
        if collection_name not in COLLECTIONS:
            raise MongoDBCollectionError(f"Collection '{collection_name}' not found in database '{self.database}'", 404)
        collection = self.db[collection_name]
        return list(collection.find(query, projection))

    def insert_data(self, collection_name, doc):
        """Insert data into the database"""
        if collection_name not in COLLECTIONS:
            raise MongoDBCollectionError(f"Collection '{collection_name}' not found in database '{self.database}'", 404)
        collection = self.db[collection_name]
        collection.insert_one(doc)

    def update_data(self, collection_name, query=None, projection=None):
        """Update data in the database"""
        if collection_name not in COLLECTIONS:
            MongoDBCollectionError(f"Collection '{collection_name}' not found in database '{self.database}'", 404)
        collection = self.db[collection_name]
        collection.update_one(query, projection)
    
    def delete_data(self, collection_name, query=None, projection=None):
        """Delete data in the database"""
        if collection_name not in COLLECTIONS:
            MongoDBCollectionError(f"Collection '{collection_name}' not found in database '{self.database}'", 404)
        collection = self.db[collection_name]
        collection.delete_one(query, projection)