import os

from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from waitress import serve

from conf import TnlcmSettings, ProductionConfig, DevelopmentConfig, TestingConfig
from core.logs.log_handler import log_handler
from core.mail.mail import init_mail
from core.database.database import init_db
from core.routes import callback_namespace, jenkins_namespace, sixg_library_namespace, sixg_sandbox_sites_namespace, trial_network_namespace, user_namespace, verification_token_namespace

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
    app=app,
    title=TnlcmSettings.TITLE,
    version=TnlcmSettings.VERSION,
    description=TnlcmSettings.DESCRIPTION,
    # doc=TnlcmSettings.DOC
)

api.add_namespace(callback_namespace, path="/tnlcm/callback")
api.add_namespace(jenkins_namespace, path="/tnlcm/jenkins")
api.add_namespace(sixg_library_namespace, path="/tnlcm/6G-Library")
api.add_namespace(sixg_sandbox_sites_namespace, path="/tnlcm/6G-Sandbox-Sites")
api.add_namespace(trial_network_namespace, path="/tnlcm/trial-network")
api.add_namespace(user_namespace, path="/tnlcm/user")
api.add_namespace(verification_token_namespace, path="/tnlcm/verification-token")

log_handler.info(f"Start Server Trial Network Life Cycle Manager (TNLCM) on http://0.0.0.0:{TnlcmSettings.TNLCM_PORT}")

if __name__ == "__main__":
    if flask_env == "PRODUCTION":
        serve(app, host="0.0.0.0", port=TnlcmSettings.TNLCM_PORT)
    else:
        app.run(host="0.0.0.0", port=TnlcmSettings.TNLCM_PORT)