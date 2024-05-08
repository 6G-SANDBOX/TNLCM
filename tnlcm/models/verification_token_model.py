from datetime import datetime, timezone
from mongoengine import Document, EmailField, IntField, DateTimeField

class VerificationTokenModel(Document):
    new_account_email = EmailField(max_length=50, required=True)
    verification_token = IntField(max_length=50, required=True)
    creation_date = DateTimeField(required=True, default=datetime.now(timezone.utc))

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "verification_tokens"
    }

    def to_dict(self):
        return {
            "new_account_email": self.new_account_email,
            "verification_token": self.verification_token,
            "creation_date": self.creation_date.strftime("%Y-%m-%d %H:%M:%S") if self.creation_date is not None else None
        }

    def __repr__(self):
        return "<VerificationToken #%s: %s>" % (self.new_account_email, self.verification_token)