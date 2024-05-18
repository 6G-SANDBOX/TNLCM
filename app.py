import os

from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from waitress import serve

from conf import ProductionConfig, DevelopmentConfig, TestingConfig
from core.logs.log_handler import log_handler
from core.mail.mail import init_mail
from core.database.database import init_db
from core.routes import callback_namespace, sixg_library_namespace, trial_network_namespace, user_namespace, verification_token_namespace

app = Flask(__name__)
CORS(app)
JWTManager(app)

flask_env = os.getenv("FLASK_ENV").upper()
if flask_env == "PRODUCTION":
    app.config.from_object(ProductionConfig)
elif flask_env == "DEVELOPMENT":
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(TestingConfig)

init_db(app)
init_mail(app)

api = Api(
    app,
    title="Trial Network Life Cycle Manager - TNLCM",
    version="0.2.0",
    description=("""
    Welcome to the Trial Network Life Cycle Manager (TNLCM) API! This powerful tool facilitates the management and orchestration of network life cycles, designed specifically for the cutting-edge 6G Sandbox project.

    Explore our documentation and contribute to the project's development on GitHub.\n"""
    "[6G-Sandbox - TNLCM Repository](https://github.com/6G-SANDBOX/TNLCM)"),
    # doc=False
)

api.add_namespace(callback_namespace, path="/tnlcm/callback")
api.add_namespace(sixg_library_namespace, path="/tnlcm/6G-Library")
api.add_namespace(trial_network_namespace, path="/tnlcm/trial-network")
api.add_namespace(user_namespace, path="/tnlcm/user")
api.add_namespace(verification_token_namespace, path="/tnlcm/verification-token")

log_handler.info("Start Server Trial Network Life Cycle Manager (TNLCM) on http://0.0.0.0:5000")

if __name__ == "__main__":
    if flask_env == "PRODUCTION":
        serve(app, host="0.0.0.0", port=5000)
    else:
        app.run(host="0.0.0.0", port=5000)