from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError

from src.logs.log_handler import log_handler
from src.exceptions.exceptions_handler import UserEmailInvalidError
from src.database.mongo_handler import MongoHandler

class AuthHandler:

    def __init__(self, jwt_identity=None, username=None, email=None, password=None, org=None):
        """Constructor"""
        self.jwt_identity = jwt_identity
        self.username = username
        self.email = email
        self.password = password
        self.org = org
        self.mongo_client = MongoHandler()

    def get_current_user_from_jwt(self):
        """Return the user that is associated with the token entered"""
        query = {"username": self.jwt_identity}
        user = self.mongo_client.find_data(collection_name="users", query=query)
        return user

    def get_username(self):
        """Return the username associated with a user"""
        log_handler.info(f"Check if the user '{self.username}' is in the 'users' collection of the database")
        query = {"username": self.username}
        projection = {"_id": 0, "username": 1}
        user = self.mongo_client.find_data(collection_name="users", query=query, projection=projection)
        return user

    def get_email(self):
        """Return the email associated with an user"""
        log_handler.info(f"Check if the email '{self.email}' is in the 'users' collection of the database")
        query = {"email": self.email}
        projection = {"_id": 0, "email": 1}
        email = self.mongo_client.find_data(collection_name="users", query=query, projection=projection)
        return email

    def _get_password(self):
        """Return the password associated with an user"""
        log_handler.info(f"Check the password associated with the user '{self.username}' in the 'users' collection of the database")
        query = {"username": self.username}
        projection = {"_id": 0, "password": 1}
        password = self.mongo_client.find_data(collection_name="users", query=query, projection=projection)
        return password

    def add_user(self):
        """Store an user in the database"""
        log_handler.info(f"Add the user '{self.username}' to the database 'users' collection")
        user_doc = {
            "email": self._is_valid_email(),
            "username": self.username,
            "password": generate_password_hash(self.password, method="pbkdf2"),
            "org": self.org
        }
        self.mongo_client.insert_data("users", user_doc)

    def update_password(self):
        """Update password associated to user"""
        log_handler.info(f"Update the password associated to the user '{self.username}' in the 'users' collection of the database")
        query = {"email": self.email}
        projection = {"$set": {"password": generate_password_hash(self.password, method="pbkdf2")}}
        self.mongo_client.update_data(collection_name="users", query=query, projection=projection)

    def check_password(self):
        """Check the hash associated with the password"""
        if self.password:
            hash_password = self._get_password()[0]["password"]
            return check_password_hash(hash_password, self.password)
        return False

    def _is_valid_email(self):
        """Checks if the email entered by the user is valid"""
        log_handler.info(f"Checks if the email '{self.email}' complies with the email syntax")
        try:
            valid = validate_email(self.email)
            return valid.normalized
        except EmailNotValidError:
            raise UserEmailInvalidError("Invalid email entered", 400)