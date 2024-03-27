from flask import request
from datetime import timedelta
from flask_restx import Resource, Namespace, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token

from src.auth.auth_handler import AuthHandler
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
        try:
            auth_handler = None
            jwt_identity = get_jwt_identity()
            auth_handler = AuthHandler(jwt_identity=jwt_identity)
            current_user = auth_handler.get_current_user_from_jwt()
            return {"username": current_user}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if auth_handler is not None:
                auth_handler.mongo_client.disconnect()

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, required=True)
    parser_post.add_argument("username", type=str, required=True)
    parser_post.add_argument("password", type=str, required=True)
    parser_post.add_argument("org", type=str, required=True)

    @users_namespace.expect(parser_post)
    def post(self):
        """
        Add an user
        """
        try:
            auth_handler = None
            email = self.parser_post.parse_args()["email"]
            username = self.parser_post.parse_args()["username"]
            password = self.parser_post.parse_args()["password"]
            org = self.parser_post.parse_args()["org"]

            auth_handler = AuthHandler(username=username, email=email, password=password, org=org)
            user = auth_handler.get_email()
            if user:
                return abort(409, "Email already created in the database")
            user = auth_handler.get_username()
            if user:
                return abort(409, "Username already created in the database")
            auth_handler.create_user()
            return {"message": "User added"}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if auth_handler is not None:
                auth_handler.mongo_client.disconnect()

@users_namespace.route("/login")
class UserLogin(Resource):

    @users_namespace.doc(security="basicAuth")
    def post(self):
        """
        Login for user and return tokens
        """
        try:
            auth_handler = None
            auth = request.authorization

            if not auth or not auth.username or not auth.password:
                return abort(401, f"Could not verify the user {auth.username}")

            auth_handler = AuthHandler(username=auth.username, password=auth.password)
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
                }, 200
            return abort(401, f"Could not verify user {auth.username}")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if auth_handler is not None:
                auth_handler.mongo_client.disconnect()

@users_namespace.route("/refresh")
class UserTokenRefresh(Resource):

    @users_namespace.doc(security="Bearer Auth")
    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh tokens for user
        """
        auth_handler = None
        jwt_identity = get_jwt_identity()
        auth_handler = AuthHandler(jwt_identity=jwt_identity)
        current_user = auth_handler.get_current_user_from_jwt()
        try:
            new_access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=EXP_MINUTES_ACCESS_TOKEN))
            return {"access_token": new_access_token}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if auth_handler is not None:
                auth_handler.mongo_client.disconnect()