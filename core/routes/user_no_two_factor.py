from datetime import timedelta
from flask import request
from flask_restx import Resource, Namespace, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError

from core.auth.auth import get_current_user_from_jwt
from core.models import UserModel
from core.exceptions.exceptions_handler import CustomException

EXP_MINUTES_ACCESS_TOKEN = 1440
EXP_DAYS_REFRESH_TOKEN = 730

user_no_two_factor_namespace = Namespace(
    name="user",
    description="Namespace for user",
    authorizations={
        "basicAuth": {
            "type": "basic"
        },
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        }
    }
)

@user_no_two_factor_namespace.route("")
class User(Resource):

    @user_no_two_factor_namespace.doc(security="Bearer Auth")
    @user_no_two_factor_namespace.errorhandler(PyJWTError)
    @user_no_two_factor_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self) -> tuple[dict, int]:
        """
        Retrieve current user
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            return current_user.to_dict(), 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))

@user_no_two_factor_namespace.route("/register")
class NewUserVerification(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)
    parser_post.add_argument("username", type=str, location="json", required=True)
    parser_post.add_argument("password", type=str, location="json", required=True)
    parser_post.add_argument("org", type=str, location="json", required=True)

    @user_no_two_factor_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Verify a new user account via email with the verification token
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

            user = UserModel(
                username=username,
                email=email,
                org=org
            )
            user.set_password(password)
            user.set_email(email)
            user.save()

            return {"message": "User added"}, 201
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))

@user_no_two_factor_namespace.route("/login")
class UserLogin(Resource):

    @user_no_two_factor_namespace.doc(security="basicAuth")
    def post(self) -> tuple[dict, int]:
        """
        Login for user and return tokens
        """
        try:
            auth = request.authorization

            if not auth or not auth.username or not auth.password:
                return {"message": f"Could not verify user '{auth.username}'"}, 401

            user = UserModel.objects(username=auth.username).first()
            if not user:
                return {"message": "User not found"}, 404
            
            if user.verify_password(auth.password):
                access_token = create_access_token(identity=user.username, expires_delta=timedelta(minutes=EXP_MINUTES_ACCESS_TOKEN))
                refresh_token = create_refresh_token(identity=user.username, expires_delta=timedelta(days=EXP_DAYS_REFRESH_TOKEN))
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, 201
            
            return {"message": f"Could not verify user '{auth.username}'"}, 401
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))

@user_no_two_factor_namespace.route("/change-password")
class ChangePassword(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)
    parser_post.add_argument("password", type=str, location="json", required=True)

    @user_no_two_factor_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Change an user password with a reset token
        """
        try:
            receiver_email = self.parser_post.parse_args()["email"]
            password = self.parser_post.parse_args()["password"]
            
            user = UserModel.objects(email=receiver_email).first()
            if not user:
                return {"message": "User not found"}, 404

            user.set_password(password)
            user.save()

            return {"message": "Password change confirmation sent by email successfully"}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))

@user_no_two_factor_namespace.route("/refresh")
class UserTokenRefresh(Resource):

    @user_no_two_factor_namespace.doc(security="Bearer Auth")
    @user_no_two_factor_namespace.errorhandler(PyJWTError)
    @user_no_two_factor_namespace.errorhandler(JWTExtendedException)
    @jwt_required(refresh=True)
    def post(self) -> tuple[dict, int]:
        """
        Refresh tokens for user
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            if not current_user:
                return {"message": "User not found"}, 404
            
            new_access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=EXP_MINUTES_ACCESS_TOKEN))
            return {"access_token": new_access_token}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))