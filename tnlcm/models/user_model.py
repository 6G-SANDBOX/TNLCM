from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from mongoengine import Document, EmailField, StringField

from tnlcm.exceptions.exceptions_handler import UserEmailInvalidError

class UserModel(Document):
    username = StringField(max_length=50, required=True, unique=True)
    password = StringField(max_length=255, required=True)
    email = EmailField(max_length=50, required=True, unique=True)
    org = StringField(max_length=50, required=False)

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "users"
    }

    def __init__(self, username=None, password=None, email=None, org=None, *args, **kwargs):
        """Constructor"""
        super().__init__(*args, **kwargs)
        self.username = username
        self.password = password
        if not self._is_valid_email(email):
            raise UserEmailInvalidError("Invalid email entered", 400)
        self.email = email
        self.org = org

    def set_password(self, secret):
        """Update the password to hash"""
        self.password = generate_password_hash(secret, method="pbkdf2")

    def check_password(self, secret):
        """Check the hash associated with the password"""
        value = check_password_hash(self.password, secret)
        return value

    def _is_valid_email(self, email):
        """Checks if the email entered by the user is valid"""
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