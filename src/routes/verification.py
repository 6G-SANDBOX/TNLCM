import os

from flask_restx import Resource, Namespace, reqparse, abort
from flask_mail import Message
from random import randint

from src.verification.mail import mail
from src.auth.auth_handler import AuthHandler
from src.database.mongo_handler import MongoHandler
from src.verification.verification_handler import VerificationHandler
from src.exceptions.exceptions_handler import CustomException, VariablesNotDefinedInEnvError

verification_namespace = Namespace(
    name="verification",
    description="Namespace for verification"
)

@verification_namespace.route("/request_verification_token")
class RequestVerificationToken(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)

    @verification_namespace.expect(parser_post)
    def post(self):
        """
        Request a verification token via email for registering a new account
        """
        mongo_handler = None
        try:
            sender_email = os.getenv("MAIL_USERNAME")
            if sender_email is None:
                raise VariablesNotDefinedInEnvError(f"Add the value of the variable 'MAIL_USERNAME' in the .env file", 500)
            receiver_email = self.parser_post.parse_args()["email"]
            _six_digit_random = randint(100000, 999999)

            mongo_handler = MongoHandler()
            auth_handler = AuthHandler(mongo_handler=mongo_handler, email=receiver_email)
            user = auth_handler.get_email()
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

            verification_handler = VerificationHandler(mongo_handler=mongo_handler, new_account_email=receiver_email, verification_token=_six_digit_random)
            verification_handler.add_verification_token()

            return {"message": "Verification token sent by email successfully"}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()

@verification_namespace.route("/new_user_verification")
class NewUserVerification(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)
    parser_post.add_argument("verification_token", type=int, location="json", required=True)
    parser_post.add_argument("username", type=str, location="json", required=True)
    parser_post.add_argument("password", type=str, location="json", required=True)
    parser_post.add_argument("org", type=str, location="json", required=True)

    @verification_namespace.expect(parser_post)
    def post(self):
        """
        Verify a new user account via email with the verification token
        """
        mongo_handler = None
        try:
            email = self.parser_post.parse_args()["email"]
            verification_token = self.parser_post.parse_args()["verification_token"]
            username = self.parser_post.parse_args()["username"]
            password = self.parser_post.parse_args()["password"]
            org = self.parser_post.parse_args()["org"]

            mongo_handler = MongoHandler()
            auth_handler = AuthHandler(mongo_handler=mongo_handler, username=username, email=email, password=password, org=org)
            user = auth_handler.get_email()
            if user:
                return abort(409, "Email already exist in the database")
            user = auth_handler.get_username()
            if user:
                return abort(409, "Username already exist in the database")

            verification_handler = VerificationHandler(mongo_handler=mongo_handler, new_account_email=email, verification_token=verification_token)
            latest_verification_token = verification_handler.get_verification_token()

            if not latest_verification_token:
                return abort(401, "Token provided not correct")

            auth_handler.add_user()
            return {"message": "User added"}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()

@verification_namespace.route("/request_reset_token")
class RequestResetToken(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)

    @verification_namespace.expect(parser_post)
    def post(self):
        """
        Request a reset token via email for changing password
        """
        mongo_handler = None
        try:
            sender_email = os.getenv("MAIL_USERNAME")
            if sender_email is None:
                raise VariablesNotDefinedInEnvError(f"Add the value of the variable 'MAIL_USERNAME' in the .env file", 500)
            receiver_email = self.parser_post.parse_args()["email"]
            _six_digit_random = randint(100000, 999999)

            mongo_handler = MongoHandler()
            auth_handler = AuthHandler(mongo_handler=mongo_handler, email=receiver_email)
            user = auth_handler.get_email()
            if not user:
                return abort(404, "User not found")

            with mail.connect() as conn:
                msg = Message(
                    subject="[6G-SANDBOX] TNLCM: Account recovery.",
                    sender=sender_email,
                    recipients=[receiver_email]
                )
                msg.body = f"Your account recovery code is {_six_digit_random}."
                conn.send(msg)

            verification_handler = VerificationHandler(mongo_handler=mongo_handler, new_account_email=receiver_email, verification_token=_six_digit_random)
            verification_handler.update_verification_token()

            return {"message": "Reset token sent by email successfully"}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()

@verification_namespace.route('/change_password')
class ChangePassword(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)
    parser_post.add_argument("password", type=str, location="json", required=True)
    parser_post.add_argument("reset_token", type=int, location="json", required=True)

    @verification_namespace.expect(parser_post)
    def post(self):
        """
        Change an user password with a reset token
        """
        mongo_handler = None
        try:
            sender_email = os.getenv("MAIL_USERNAME")
            if sender_email is None:
                raise VariablesNotDefinedInEnvError(f"Add the value of the variable 'MAIL_USERNAME' in the .env file", 500)
            receiver_email = self.parser_post.parse_args()["email"]
            password = self.parser_post.parse_args()["password"]
            reset_token = self.parser_post.parse_args()["reset_token"]
            
            mongo_handler = MongoHandler()
            auth_handler = AuthHandler(mongo_handler=mongo_handler, email=receiver_email, password=password)
            user = auth_handler.get_email()
            if not user:
                return abort(404, "User not found")
            
            verification_handler = VerificationHandler(mongo_handler=mongo_handler, new_account_email=receiver_email, verification_token=reset_token)
            latest_verification_token = verification_handler.get_verification_token()

            if not latest_verification_token:
                return abort(401, "Token provided not correct")
            
            auth_handler.update_password()

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
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()