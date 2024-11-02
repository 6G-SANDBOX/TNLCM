from werkzeug.security import generate_password_hash, check_password_hash
from mongoengine import Document, EmailField, StringField

class UserModel(Document):
        
    username = StringField(max_length=50, unique=True)
    password = StringField(max_length=255)
    email = EmailField(max_length=50, unique=True)
    role = StringField(max_length=20, default="user")
    org = StringField(max_length=50)

    meta = {
        "db_alias": "tnlcm-database-alias",
        "collection": "user",
        "description": "This collection stores user information"
    }

    def set_password(self, secret: str) -> None:
        """
        Set the password to hash
        
        :param secret: password value, ``str``
        """
        self.password = generate_password_hash(secret, method="pbkdf2")

    def verify_password(self, secret: str) -> bool:
        """
        Verify the hash associated with the password
        
        :param secret: password value, ``str``
        :return: True if the provided password matches the stored hash. Otherwise False, ``bool``
        """
        return check_password_hash(self.password, secret)

    def set_email(self, email: str) -> None:
        """
        Set the email
        
        :param email: email address to set, ``str``
        """
        self.email = email

    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "username": self.username,
            "org": self.org
        }

    def __repr__(self) -> str:
        return "<User #%s: %s>" % (self.username, self.email)