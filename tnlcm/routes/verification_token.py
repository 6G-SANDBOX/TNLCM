import os

from flask_restx import Resource, Namespace, reqparse, abort
from flask_mail import Message
from random import randint

from tnlcm.mail.mail import mail
from tnlcm.models import UserModel, VerificationTokenModel
from tnlcm.exceptions.exceptions_handler import CustomException, VariablesNotDefinedInEnvError

verification_token_namespace = Namespace(
    name="verification",
    description="Namespace for verification"
)

@verification_token_namespace.route("/request_verification_token")
class RequestVerificationToken(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)

    @verification_token_namespace.expect(parser_post)
    def post(self):
        """
        Request a verification token via email for registering a new account
        """
        try:
            sender_email = os.getenv("MAIL_USERNAME")
            if not sender_email:
                raise VariablesNotDefinedInEnvError(f"Add the value of the variable 'MAIL_USERNAME' in the .env file", 500)
            receiver_email = self.parser_post.parse_args()["email"]
            _six_digit_random = randint(100000, 999999)

            verification_token = VerificationTokenModel(
                new_account_email=receiver_email,
                verification_token=_six_digit_random
            )

            user = UserModel.objects(email=receiver_email).first()
            if user:
                return abort(409, "Email already exist in the database")

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
            return abort(e.error_code, str(e))

@verification_token_namespace.route("/new_user_verification")
class NewUserVerification(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)
    parser_post.add_argument("verification_token", type=int, location="json", required=True)
    parser_post.add_argument("username", type=str, location="json", required=True)
    parser_post.add_argument("password", type=str, location="json", required=True)
    parser_post.add_argument("org", type=str, location="json", required=True)

    @verification_token_namespace.expect(parser_post)
    def post(self):
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
                return abort(409, "Username already exist in the database")
            
            user = UserModel.objects(email=email).first()
            if user:
                return abort(409, "Email already exist in the database")

            latest_verification_token = VerificationTokenModel.objects(new_account_email=email).order_by("-creation_date").first()
            if latest_verification_token.verification_token != verification_token:
                return abort(401, "Token provided not correct")
            
            user = UserModel(
                username=username,
                email=email,
                org=org
            )

            user.set_password(password)
            user.save()

            return {"message": "User added"}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@verification_token_namespace.route("/request_reset_token")
class RequestResetToken(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)

    @verification_token_namespace.expect(parser_post)
    def post(self):
        """
        Request a reset token via email for changing password
        """
        try:
            sender_email = os.getenv("MAIL_USERNAME")
            if not sender_email:
                raise VariablesNotDefinedInEnvError(f"Add the value of the variable 'MAIL_USERNAME' in the .env file", 500)
            receiver_email = self.parser_post.parse_args()["email"]
            _six_digit_random = randint(100000, 999999)

            user = UserModel.objects(email=receiver_email).first()
            if not user:
                return abort(404, "User not found")
            
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
            return abort(e.error_code, str(e))

@verification_token_namespace.route("/change_password")
class ChangePassword(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)
    parser_post.add_argument("password", type=str, location="json", required=True)
    parser_post.add_argument("verification_token", type=int, location="json", required=True)

    @verification_token_namespace.expect(parser_post)
    def post(self):
        """
        Change an user password with a reset token
        """
        try:
            sender_email = os.getenv("MAIL_USERNAME")
            if not sender_email:
                raise VariablesNotDefinedInEnvError(f"Add the value of the variable 'MAIL_USERNAME' in the .env file", 500)
            receiver_email = self.parser_post.parse_args()["email"]
            password = self.parser_post.parse_args()["password"]
            verification_token = self.parser_post.parse_args()["verification_token"]
            
            user = UserModel.objects(email=receiver_email).first()
            if not user:
                return abort(404, "User not found")

            latest_verification_token = VerificationTokenModel.objects(new_account_email=receiver_email).order_by("-creation_date").first()
            if latest_verification_token.verification_token != verification_token:
                return abort(401, "Token provided not correct")

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
            return abort(e.error_code, str(e))