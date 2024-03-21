from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from src.exceptions.exceptions_handler import UserEmailInvalidError

from src.database.mongo_handler import MongoHandler

def create_mongo_client():
    mongo_client = MongoHandler()
    return mongo_client

def get_current_user_from_jwt(jwt_identity):
    mongo_client = create_mongo_client()
    query = {"username": jwt_identity}
    projection = {"_id": 0, "username": 1}
    user = mongo_client.find_data(collection_name="trial_network_user", query=query, projection=projection)
    mongo_client.disconnect()
    return user

def get_username(username):
    mongo_client = create_mongo_client()
    query = {"username": username}
    projection = {"_id": 0, "username": 1}
    user = mongo_client.find_data(collection_name="trial_network_user", query=query, projection=projection)
    mongo_client.disconnect()
    return user

def get_email(email):
    mongo_client = create_mongo_client()
    query = {"email": email}
    projection = {"_id": 0, "email": 1}
    email = mongo_client.find_data(collection_name="trial_network_user", query=query, projection=projection)
    mongo_client.disconnect()
    return email

def is_valid_email(email):
    try:
        valid = validate_email(email)
        return valid.normalized
    except EmailNotValidError:
        raise UserEmailInvalidError("Invalid email entered", 400)

def create_user(email, username, password):
    mongo_client = create_mongo_client()
    user_doc = {
        "email": is_valid_email(email),
        "username": username,
        "password": generate_password_hash(password, method='pbkdf2')
    }
    mongo_client.insert_data("trial_network_user", user_doc)
    mongo_client.disconnect()

def get_password(username):
    mongo_client = create_mongo_client()
    query = {"username": username}
    projection = {"_id": 0, "password": 1}
    password = mongo_client.find_data(collection_name="trial_network_user", query=query, projection=projection)
    mongo_client.disconnect()
    return password

def check_password(username, password):
    if password:
        hash_password = get_password(username)[0]["password"]
        return check_password_hash(hash_password, password)
    return False