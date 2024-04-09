from datetime import datetime, timezone

from src.database.mongo_handler import MongoHandler

class VerificationHandler:

    def __init__(self, new_account_email, verification_token):
        """Constructor"""
        self.new_account_email = new_account_email
        self.verification_token = verification_token
        self.creation_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.mongo_client = MongoHandler()
    
    def add_verification_token(self):
        """Add verification token to database"""
        verification_token_doc = {
            "new_account_email": self.new_account_email,
            "verification_token": self.verification_token,
            "creation_date": self.creation_date
        }
        self.mongo_client.insert_data("verification_tokens", verification_token_doc)
    
    def update_verification_token(self):
        """Update verification token"""
        query = {"new_account_email": self.new_account_email}
        projection = {"$set": {"verification_token": self.verification_token, "creation_date": self.creation_date}}
        self.mongo_client.update_data(collection_name="verification_tokens", query=query, projection=projection)

    def get_verification_token(self):
        """Return verification token associated an email of user"""
        query = {"new_account_email": self.new_account_email, "verification_token": self.verification_token}
        projection = {"_id": 0, "verification_token": 1}
        verification_token = self.mongo_client.find_data(collection_name="verification_tokens", query=query, projection=projection)
        return verification_token