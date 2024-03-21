from flask_restx import Resource, Namespace, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token

from src.auth.auth_queries import get_current_user_from_jwt

EXP_MINUTES_ACCESS_TOKEN = 15
EXP_DAYS_REFRESH_TOKEN = 730

users_namespace = Namespace(
    name="users",
    description="Namespace for users",
    authorizations={
        "basicAuth": {
            "type": "basic"
        }
    }
)

@users_namespace.route("/")
class Users(Resource):

    @users_namespace.doc(security="apiKey")
    def get(self):
        """
        Retrieve current user
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            return current_user, 200
        except Exception as e:
            return abort(422, str(e))