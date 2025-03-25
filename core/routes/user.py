from datetime import timedelta

from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Namespace, Resource, abort, reqparse
from jwt.exceptions import PyJWTError

from core.auth.auth import get_current_user_from_jwt
from core.exceptions.exceptions import CustomException
from core.models.user import UserModel

EXP_MINUTES_ACCESS_TOKEN = 10080  # one week
EXP_DAYS_REFRESH_TOKEN = 730

user_namespace = Namespace(
    name="user",
    description="Namespace for user",
    authorizations={
        "basicAuth": {"type": "basic"},
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
        },
    },
)


@user_namespace.route("")
class User(Resource):
    @user_namespace.doc(security="Bearer Auth")
    @user_namespace.errorhandler(PyJWTError)
    @user_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self):
        """
        Retrieve current user
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            return current_user.to_dict(), 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@user_namespace.route("/change-password")
class ChangePassword(Resource):
    parser_post = reqparse.RequestParser()
    parser_post.add_argument("username", type=str, location="json", required=True)
    parser_post.add_argument("old_password", type=str, location="json", required=True)
    parser_post.add_argument("new_password", type=str, location="json", required=True)

    @user_namespace.expect(parser_post)
    def post(self):
        """
        Change current user password
        """
        try:
            username = self.parser_post.parse_args()["username"]
            old_password = self.parser_post.parse_args()["old_password"]
            new_password = self.parser_post.parse_args()["new_password"]

            user = UserModel.objects(username=username).first()
            if not user:
                return {"message": "User not found"}, 404
            if not user.verify_password(secret=old_password):
                return {"message": "Old password is incorrect"}, 401
            if user.verify_password(secret=new_password):
                return {"message": "New password is the same as the old password"}, 400
            user.set_password(secret=new_password)
            user.save()
            return {"message": "Password changed"}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@user_namespace.route("/login")
class Login(Resource):
    @user_namespace.doc(security="basicAuth")
    def post(self):
        """
        Login for user and return tokens
        """
        try:
            auth = request.authorization

            if not auth or not auth.username or not auth.password:
                return {"message": f"Could not verify user {auth.username}"}, 401
            user = UserModel.objects(username=auth.username).first()
            if not user:
                return {"message": "User not found"}, 404
            if user.verify_password(secret=auth.password):
                access_token = create_access_token(
                    identity=user.username,
                    expires_delta=timedelta(minutes=EXP_MINUTES_ACCESS_TOKEN),
                )
                refresh_token = create_refresh_token(
                    identity=user.username,
                    expires_delta=timedelta(days=EXP_DAYS_REFRESH_TOKEN),
                )
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }, 201
            return {"message": f"Could not verify user {auth.username}"}, 401
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@user_namespace.route("/refresh")
class TokenRefresh(Resource):
    @user_namespace.doc(security="Bearer Auth")
    @user_namespace.errorhandler(PyJWTError)
    @user_namespace.errorhandler(JWTExtendedException)
    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh tokens for user
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            if not current_user:
                return {"message": "User not found"}, 404
            new_access_token = create_access_token(
                identity=current_user.username,
                expires_delta=timedelta(minutes=EXP_MINUTES_ACCESS_TOKEN),
            )
            return {"access_token": new_access_token}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@user_namespace.route("/register")
class Register(Resource):
    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)
    parser_post.add_argument("username", type=str, location="json", required=True)
    parser_post.add_argument("password", type=str, location="json", required=True)
    parser_post.add_argument("org", type=str, location="json", required=True)

    @user_namespace.expect(parser_post)
    def post(self):
        """
        Register a new user
        """
        try:
            email = self.parser_post.parse_args()["email"]
            username = self.parser_post.parse_args()["username"]
            password = self.parser_post.parse_args()["password"]
            org = self.parser_post.parse_args()["org"]

            user = UserModel.objects(username=username).first()
            if user:
                return {"message": "Username already exist in the database"}, 409
            user = UserModel.objects(email=email).first()
            if user:
                return {"message": "Email already exist in the database"}, 409
            user = UserModel(username=username, email=email, org=org)
            user.set_password(secret=password)
            user.set_email(email=email)
            user.save()
            return {"message": "User added"}, 201
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))
