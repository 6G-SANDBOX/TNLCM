from core.models.user import UserModel


def get_current_user_from_jwt(jwt_identity: str) -> UserModel:
    """
    Function to know the current user based on their JWT (JSON Web Token) identity

    :param jwt_identity: identity of the user contained in the JWT, ``str``
    :return: current user model, ``UserModel``
    """
    return UserModel.objects(username=jwt_identity).first()
