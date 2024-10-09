from datetime import datetime, timezone
from mongoengine import Document, EmailField, IntField, DateTimeField
from mongoengine.errors import ValidationError, MongoEngineException

from core.exceptions.exceptions_handler import CustomException

class VerificationTokenModel(Document):
    
    try:
        new_account_email = EmailField(max_length=50, unique=True)
        verification_token = IntField(max_length=50)
        creation_date = DateTimeField(default=datetime.now(timezone.utc))
    except ValidationError as e:
        raise CustomException(e.message, 401)
    except MongoEngineException as e:
        raise CustomException(str(e), 401)

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "verification_tokens"
    }

    def to_dict(self):
        return {
            "new_account_email": self.new_account_email,
            "verification_token": self.verification_token,
            "creation_date": self.creation_date.isoformat() if self.creation_date else None
        }

    def __repr__(self):
        return "<VerificationToken #%s: %s>" % (self.new_account_email, self.verification_token)