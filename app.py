from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from conf import TnlcmSettings, FlaskConf, MailSettings
from core.logs.log_handler import tnlcm_log_handler
from core.mail.mail import init_mail
from core.database.database import init_db
from core.routes import callback_namespace, debug_namespace, library_namespace, trial_network_namespace, user_no_two_factor_namespace, user_namespace, verification_token_namespace
from core.utils.file_handler import loads_toml
from core.utils.os_handler import current_directory, join_path

app = Flask(__name__)
CORS(app=app)
JWTManager(app=app)

app.config.from_object(obj=FlaskConf)

init_db(app=app)
if MailSettings.TWO_FACTOR_AUTH:
    init_mail(app=app)
__version__ = loads_toml(file_path=join_path(current_directory(), "pyproject.toml"))["tool"]["poetry"]["version"]

api = Api(
    app=app,
    title=TnlcmSettings.TITLE,
    version=__version__,
    description=TnlcmSettings.DESCRIPTION,
    # doc=TnlcmSettings.DOC
)

api.add_namespace(callback_namespace, path="/tnlcm/callback")
if FlaskConf.FLASK_ENV == "development":
    api.add_namespace(debug_namespace, path="/tnlcm/debug")
api.add_namespace(library_namespace, path="/tnlcm/library")
api.add_namespace(trial_network_namespace, path="/tnlcm/trial-network")
api.add_namespace(user_namespace, path="/tnlcm/user")
if not MailSettings.TWO_FACTOR_AUTH:
    api.add_namespace(user_no_two_factor_namespace, path="/tnlcm/user")
else:
    api.add_namespace(verification_token_namespace, path="/tnlcm/verification-token")
tnlcm_log_handler.info(f"Start Trial Network Lifecycle Manager (TNLCM) {__version__} on http://0.0.0.0:{TnlcmSettings.TNLCM_PORT}")