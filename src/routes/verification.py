import os

from flask_restx import Resource, Namespace, reqparse, abort
from flask_mail import Message
from random import randint

from src.auth.auth_handler import AuthHandler
from src.verification.mail import mail
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
        # TODO: 
        """
        Request a verification token via email for registering a new account
        """
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

            return {"message": "Verification token sent by email successfully"}, 200

        except CustomException as e:
            return abort(422, str(e))