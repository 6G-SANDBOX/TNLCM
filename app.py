from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from conf import TnlcmSettings, FlaskConf
from core.logs.log_handler import log_handler
from core.mail.mail import init_mail
from core.database.database import init_db
from core.routes import callback_namespace, debug_namespace, trial_network_namespace, user_namespace, verification_token_namespace

app = Flask(__name__)
CORS(app)
JWTManager(app)

app.config.from_object(FlaskConf)

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
api.add_namespace(debug_namespace, path="/tnlcm/debug")
api.add_namespace(trial_network_namespace, path="/tnlcm/trial-network")
api.add_namespace(user_namespace, path="/tnlcm/user")
api.add_namespace(verification_token_namespace, path="/tnlcm/verification-token")

log_handler.info(f"Start Trial Network Lifecycle Manager (TNLCM) v{TnlcmSettings.VERSION} on http://0.0.0.0:{TnlcmSettings.TNLCM_PORT}")