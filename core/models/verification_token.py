from datetime import datetime, timezone
from mongoengine import DateTimeField, Document, EmailField, IntField

class VerificationTokenModel(Document):
    
    new_account_email = EmailField(max_length=50, unique=True)
    verification_token = IntField(max_length=50)
    creation_date = DateTimeField(default=datetime.now(timezone.utc))

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "verification_token",
        "description": "This collection stores verification tokens used for user authentication and account verification"
    }

    def to_dict(self) -> dict:
        return {
            "new_account_email": self.new_account_email,
            "verification_token": self.verification_token,
            "creation_date": self.creation_date.isoformat() if self.creation_date else None
        }

    def __repr__(self) -> str:
        return "<VerificationToken #%s: %s>" % (self.new_account_email, self.verification_token)