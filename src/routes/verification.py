import os

from flask_restx import Resource, Namespace, reqparse, abort
from flask_mail import Message
from random import randint

from src.auth.auth_handler import AuthHandler
from src.verification.mail import mail
from src.verification.verification_handler import VerificationHandler
from src.exceptions.exceptions_handler import CustomException

verification_namespace = Namespace(
    name="verification",
    description="Namespace for verification endpoints"
)

@verification_namespace.route("/request-verification-token")
class RequestVerificationToken(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("email", type=str, location="json", required=True)

    @verification_namespace.expect(parser_post)
    def post(self):
        """
        Request a verification token via email for registering a new account
        """
        verification_handler = None
        auth_handler = None
        try:
            sender_email = os.getenv("MAIL_USERNAME")
            receiver_email = self.parser_post.parse_args()["email"]
            _six_digit_random = randint(100000, 999999)

            auth_handler = AuthHandler(email=receiver_email)
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

            verification_handler = VerificationHandler(receiver_email, _six_digit_random)
            verification_handler.add_verification_token()

            return {"message": "Verification token sent by email successfully"}, 200
        except CustomException as e:
            return abort(422, str(e))
        finally:
            if auth_handler != None:
                auth_handler.mongo_client.disconnect()
            if verification_handler != None:
                verification_handler.mongo_client.disconnect()

@verification_namespace.route("/new-user-verification")
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
        verification_handler = None
        auth_handler = None
        try:
            email = self.parser_post.parse_args()["email"].lower()
            verification_token = self.parser_post.parse_args()["verification_token"]
            username = self.parser_post.parse_args()["username"].lower()
            password = self.parser_post.parse_args()["password"].lower()
            org = self.parser_post.parse_args()["org"].upper()

            auth_handler = AuthHandler(username=username, email=email, password=password, org=org)
            user = auth_handler.get_email()
            if user:
                return abort(409, "Email already exist in the database")
            user = auth_handler.get_username()
            if user:
                return abort(409, "Username already exist in the database")

            verification_handler = VerificationHandler(email, verification_token)
            latest_verification_token = verification_handler.get_verification_token()

            if latest_verification_token != verification_token:
                return {"message": "Token provided not correct"}, 401

            auth_handler.create_user()
            return {"message": "User added"}, 201
        except CustomException as e:
            return {'message': str(e)}, 422
        finally:
            if auth_handler != None:
                auth_handler.mongo_client.disconnect()
            if verification_handler != None:
                verification_handler.mongo_client.disconnect()