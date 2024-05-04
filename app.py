import os

from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from waitress import serve
from dotenv import load_dotenv

from src.logs.log_handler import log_handler
from src.verification.mail import init_mail
from src.routes import callback_namespace, sixglibrary_namespace, sixgsandbox_sites_namespace, trial_network_namespace, users_namespace, verification_namespace

app = Flask(__name__)
CORS(app)
JWTManager(app)

load_dotenv()
flask_env = os.getenv("FLASK_ENV").upper()
if flask_env == "PRODUCTION":
    app.config.from_object("config.ProductionConfig")
elif flask_env == "DEVELOPMENT":
    app.config.from_object("config.DevelopmentConfig")
else:
    app.config.from_object("config.TestingConfig")

init_mail(app)

api = Api(
    app,
    title="Trial Network Life Cycle Manager - TNLCM",
    version="0.1.0",
    description=("""
    Welcome to the Trial Network Life Cycle Manager (TNLCM) API! This powerful tool facilitates the management and orchestration of network life cycles, designed specifically for the cutting-edge 6G Sandbox project.

    Explore our documentation and contribute to the project's development on GitHub.\n"""
    "[6G-Sandbox - TNLCM Repository](https://github.com/6G-SANDBOX/TNLCM)"),
    # doc=False
)

api.add_namespace(callback_namespace, path="/tnlcm/callback")
api.add_namespace(sixglibrary_namespace, path="/tnlcm/6glibrary")
api.add_namespace(sixgsandbox_sites_namespace, path="/tnlcm/6gsandbox_sites")
api.add_namespace(trial_network_namespace, path="/tnlcm/trial_network")
api.add_namespace(users_namespace, path="/tnlcm/user")
api.add_namespace(verification_namespace, path="/tnlcm/verification")

log_handler.info("Start Server Trial Network Life Cycle Manager (TNLCM) on http://0.0.0.0:5000")

if __name__ == "__main__":
    if flask_env == "PRODUCTION":
        serve(app, host="0.0.0.0", port=5000)
    else:
        app.run(host="0.0.0.0", port=5000)