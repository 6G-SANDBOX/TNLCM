from core.models import UserModel

def get_current_user_from_jwt(jwt_identity):
    return UserModel.objects(username=jwt_identity).first()