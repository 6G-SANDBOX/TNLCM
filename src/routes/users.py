from flask import request
from datetime import timedelta
from flask_restx import Resource, Namespace, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token

from src.auth.auth_handler import AuthHandler
from src.database.mongo_handler import MongoHandler
from src.exceptions.exceptions_handler import CustomException

EXP_MINUTES_ACCESS_TOKEN = 45
EXP_DAYS_REFRESH_TOKEN = 730

users_namespace = Namespace(
    name="users",
    description="Namespace for users",
    authorizations={
        "basicAuth": {
            "type": "basic"
        },
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        }
    }
)

@users_namespace.route("")
class Users(Resource):

    @users_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self):
        """
        Retrieve current user
        """
        mongo_handler = None
        try:
            mongo_handler = MongoHandler()
            jwt_identity = get_jwt_identity()
            auth_handler = AuthHandler(mongo_handler=mongo_handler, jwt_identity=jwt_identity)
            current_user = auth_handler.get_current_user_from_jwt()
            return {"username": current_user[0]["username"]}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler:
                mongo_handler.disconnect()

@users_namespace.route("/login")
class UserLogin(Resource):

    @users_namespace.doc(security="basicAuth")
    def post(self):
        """
        Login for user and return tokens
        """
        mongo_handler = None
        try:
            auth = request.authorization

            if not auth or not auth.username or not auth.password:
                return abort(401, f"Could not verify the user {auth.username}")

            mongo_handler = MongoHandler()
            auth_handler = AuthHandler(mongo_handler=mongo_handler, username=auth.username, password=auth.password)
            username = auth_handler.get_username()
            if not username:
                return abort(404, f"User {auth.username} not found")
            username = username[0]["username"]
            if auth_handler.check_password():
                access_token = create_access_token(identity=username, expires_delta=timedelta(minutes=EXP_MINUTES_ACCESS_TOKEN))
                refresh_token = create_refresh_token(identity=username, expires_delta=timedelta(days=EXP_DAYS_REFRESH_TOKEN))
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, 201
            return abort(401, f"Could not verify user {auth.username}")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler:
                mongo_handler.disconnect()

@users_namespace.route("/refresh")
class UserTokenRefresh(Resource):

    @users_namespace.doc(security="Bearer Auth")
    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh tokens for user
        """
        mongo_handler = None
        try:
            mongo_handler = MongoHandler()
            jwt_identity = get_jwt_identity()
            auth_handler = AuthHandler(mongo_handler=mongo_handler, jwt_identity=jwt_identity)
            current_user = auth_handler.get_current_user_from_jwt()
            if not current_user:
                abort(404, "User not found")
            current_user = current_user[0]["username"]
            new_access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=EXP_MINUTES_ACCESS_TOKEN))
            return {"access_token": new_access_token}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler:
                mongo_handler.disconnect()