from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from mongoengine import Document, EmailField, StringField

from core.exceptions.exceptions_handler import InvalidEmailError

class UserModel(Document):
    username = StringField(max_length=50, unique=True)
    password = StringField(max_length=255)
    email = EmailField(max_length=50, unique=True)
    org = StringField(max_length=50)

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "users"
    }

    def set_password(self, secret):
        """Update the password to hash"""
        self.password = generate_password_hash(secret, method="pbkdf2")

    def check_password(self, secret):
        """Check the hash associated with the password"""
        value = check_password_hash(self.password, secret)
        return value

    def set_email(self, email):
        """Update the email"""
        if not self._is_valid_email(email):
            raise InvalidEmailError("Invalid email entered", 400)
        self.email = email
        
    def _is_valid_email(self, email):
        """Check if the email entered by the user is valid"""
        try:
            valid = validate_email(email)
            email = valid.email
            return True
        except EmailNotValidError:
            return False

    def to_dict(self):
        return {
            "email": self.email,
            "username": self.username,
            "org": self.org
        }

    def __repr__(self):
        return "<User #%s: %s>" % (self.username, self.email)