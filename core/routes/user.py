from flask import request
from datetime import timedelta
from flask_restx import Resource, Namespace, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from mongoengine.errors import ValidationError, MongoEngineException

from core.auth.auth import get_current_user_from_jwt
from core.models import UserModel
from core.exceptions.exceptions_handler import CustomException

EXP_MINUTES_ACCESS_TOKEN = 1440
EXP_DAYS_REFRESH_TOKEN = 730

user_namespace = Namespace(
    name="user",
    description="Namespace for user",
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

@user_namespace.route("")
class User(Resource):

    @user_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self) -> tuple[dict, int]:
        """
        Retrieve current user
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            return current_user.to_dict(), 200
        except ValidationError as e:
            return abort(401, e.message)
        except MongoEngineException as e:
            return abort(401, str(e))
        except CustomException as e:
            return abort(e.error_code, str(e))

@user_namespace.route("/login")
class UserLogin(Resource):

    @user_namespace.doc(security="basicAuth")
    def post(self) -> tuple[dict, int]:
        """
        Login for user and return tokens
        """
        try:
            auth = request.authorization

            if not auth or not auth.username or not auth.password:
                return abort(401, f"Could not verify user '{auth.username}'")

            user = UserModel.objects(username=auth.username).first()
            if not user:
                return abort(404, "User not found")
            if user.check_password(auth.password):
                access_token = create_access_token(identity=user.username, expires_delta=timedelta(minutes=EXP_MINUTES_ACCESS_TOKEN))
                refresh_token = create_refresh_token(identity=user.username, expires_delta=timedelta(days=EXP_DAYS_REFRESH_TOKEN))
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, 201
            return abort(401, f"Could not verify user '{auth.username}'")
        except ValidationError as e:
            return abort(401, e.message)
        except MongoEngineException as e:
            return abort(401, str(e))
        except CustomException as e:
            return abort(e.error_code, str(e))

@user_namespace.route("/refresh")
class UserTokenRefresh(Resource):

    @user_namespace.doc(security="Bearer Auth")
    @jwt_required(refresh=True)
    def post(self) -> tuple[dict, int]:
        """
        Refresh tokens for user
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            if not current_user:
                abort(404, "User not found")
            new_access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=EXP_MINUTES_ACCESS_TOKEN))
            return {"access_token": new_access_token}, 200
        except ValidationError as e:
            return abort(401, e.message)
        except MongoEngineException as e:
            return abort(401, str(e))
        except CustomException as e:
            return abort(e.error_code, str(e))