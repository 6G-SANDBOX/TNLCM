from flask import request
from datetime import timedelta
from flask_restx import Resource, Namespace, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from jwt.exceptions import PyJWTError

from src.auth.auth_queries import get_current_user_from_jwt, get_username, get_email, create_user, check_password
from src.exceptions.exceptions_handler import CustomException

EXP_MINUTES_ACCESS_TOKEN = 15
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
            current_user = get_current_user_from_jwt(get_jwt_identity())
            return current_user[0], 200
        except PyJWTError as e:
            return abort(404, str(e))
        except CustomException as e:
            return abort(e.error_code, str(e))

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, required=True)
    parser_post.add_argument("username", type=str, required=True)
    parser_post.add_argument("password", type=str, required=True)

    @users_namespace.expect(parser_post)
    def post(self):
        """
        Add an user
        """
        try:
            email = self.parser_post.parse_args()["email"]
            username = self.parser_post.parse_args()["username"]
            password = self.parser_post.parse_args()["password"]
            user = get_email(email)
            if user:
                return abort(409, "Duplicated email")
            user = get_username(username)
            if user:
                return abort(409, "Duplicated username")
            create_user(email, username, password)
            return {"message": "User added"}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@users_namespace.route("/login")
class UserLogin(Resource):

    @users_namespace.doc(security="basicAuth")
    def post(self):
        """
        Login for user and return tokens
        """
        try:
            auth = request.authorization

            if not auth or not auth.username or not auth.password:
                return abort(401, "Could not verify")

            username = get_username(auth.username)
            if not username:
                return abort(404, "User not found")
            username = username[0]["username"]
            if check_password(username, auth.password):
                access_token = create_access_token(identity=username, expires_delta=timedelta(minutes=EXP_MINUTES_ACCESS_TOKEN))
                refresh_token = create_refresh_token(identity=username, expires_delta=timedelta(days=EXP_DAYS_REFRESH_TOKEN))
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, 200
            return abort(401, "Could not verify")
        except CustomException as e:
            return abort(e.error_code, str(e))

@users_namespace.route("/refresh")
class UserTokenRefresh(Resource):

    @users_namespace.doc(security="Bearer Auth")
    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh tokens for user
        """
        current_user = get_current_user_from_jwt(get_jwt_identity())
        current_user = current_user[0]["username"]
        try:
            new_access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=EXP_MINUTES_ACCESS_TOKEN))
            return {"access_token": new_access_token}, 201
        except PyJWTError as e:
            return abort(404, str(e))
        except CustomException as e:
            return abort(e.error_code, str(e))