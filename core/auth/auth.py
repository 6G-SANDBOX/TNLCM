from core.models import UserModel

def get_current_user_from_jwt(jwt_identity):
    """
    Return the current user based on their JWT (JSON Web Token) identity.

    :param jwt_identity: identity of the user contained in the JWT, ``str``
    """
    return UserModel.objects(username=jwt_identity).first()