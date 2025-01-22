from random import randint
from flask_restx import Resource, Namespace, reqparse, abort
from flask_mail import Message

from conf.mail import MailSettings
from core.mail.mail import mail
from core.models import UserModel, VerificationTokenModel
from core.exceptions.exceptions_handler import CustomException

verification_token_namespace = Namespace(
    name="verification",
    description="Namespace for verification"
)

@verification_token_namespace.route("/request-verification-token")
class RequestVerificationToken(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)

    @verification_token_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Request a verification token via email for registering a new account
        """
        try:
            sender_email = MailSettings.MAIL_USERNAME
            receiver_email = self.parser_post.parse_args()["email"]
            _six_digit_random = randint(100000, 999999)

            user = VerificationTokenModel.objects(new_account_email=receiver_email).first()
            if user:
                return {"message": "Email already exist in the database"}, 409

            verification_token = VerificationTokenModel(
                new_account_email=receiver_email,
                verification_token=_six_digit_random
            )

            with mail.connect() as conn:
                msg = Message(
                    subject="[6G-SANDBOX] TNLCM: Account verification.",
                    sender=sender_email,
                    recipients=[receiver_email]
                )
                msg.body = f"Your verification code is {_six_digit_random}."
                conn.send(msg)

            verification_token.save()

            return {"message": "Verification token sent by email successfully"}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))

@verification_token_namespace.route("/new-user-verification")
class NewUserVerification(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)
    parser_post.add_argument("verification_token", type=int, location="json", required=True)
    parser_post.add_argument("username", type=str, location="json", required=True)
    parser_post.add_argument("password", type=str, location="json", required=True)
    parser_post.add_argument("org", type=str, location="json", required=True)

    @verification_token_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Verify a new user account via email with the verification token
        """
        try:
            email = self.parser_post.parse_args()["email"]
            verification_token = self.parser_post.parse_args()["verification_token"]
            username = self.parser_post.parse_args()["username"]
            password = self.parser_post.parse_args()["password"]
            org = self.parser_post.parse_args()["org"]

            user = UserModel.objects(username=username).first()
            if user:
                return {"message": "Username already exist in the database"}, 409
            
            user = UserModel.objects(email=email).first()
            if user:
                return {"message": "Email already exist in the database"}, 409

            latest_verification_token = VerificationTokenModel.objects(new_account_email=email).order_by("-creation_date").first()
            if latest_verification_token.verification_token != verification_token:
                return {"message": "Token provided not correct"}, 401
            
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

@verification_token_namespace.route("/request-reset-token")
class RequestResetToken(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)

    @verification_token_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Request a reset token via email for changing password
        """
        try:
            sender_email = MailSettings.MAIL_USERNAME
            receiver_email = self.parser_post.parse_args()["email"]
            _six_digit_random = randint(100000, 999999)

            user = UserModel.objects(email=receiver_email).first()
            if not user:
                return {"message": "User not found"}, 404
            
            verification_token = VerificationTokenModel.objects(new_account_email=receiver_email).first()
            verification_token.verification_token = _six_digit_random
            verification_token.save()

            with mail.connect() as conn:
                msg = Message(
                    subject="[6G-SANDBOX] TNLCM: Account recovery.",
                    sender=sender_email,
                    recipients=[receiver_email]
                )
                msg.body = f"Your account recovery code is {_six_digit_random}."
                conn.send(msg)

            return {"message": "New token sent by email successfully"}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))

@verification_token_namespace.route("/change-password")
class ChangePassword(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)
    parser_post.add_argument("password", type=str, location="json", required=True)
    parser_post.add_argument("verification_token", type=int, location="json", required=True)

    @verification_token_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Change an user password with a reset token
        """
        try:
            sender_email = MailSettings.MAIL_USERNAME
            receiver_email = self.parser_post.parse_args()["email"]
            password = self.parser_post.parse_args()["password"]
            verification_token = self.parser_post.parse_args()["verification_token"]
            
            user = UserModel.objects(email=receiver_email).first()
            if not user:
                return {"message": "User not found"}, 404

            latest_verification_token = VerificationTokenModel.objects(new_account_email=receiver_email).order_by("-creation_date").first()
            if latest_verification_token.verification_token != verification_token:
                return {"message": "Token provided not correct"}, 401

            user.set_password(password)
            user.save()

            with mail.connect() as conn:
                msg = Message(
                    subject="[6G-SANDBOX] TNLCM: Password change.",
                    sender=sender_email,
                    recipients=[receiver_email]
                )
                msg.body = "Your account password has been successfully changed."
                conn.send(msg)

            return {"message": "Password change confirmation sent by email successfully"}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))