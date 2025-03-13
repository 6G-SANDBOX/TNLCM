from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api

from conf.flask_conf import FlaskConf
from core.database.database import init_db
from core.routes import (
    callback_namespace,
    debug_namespace,
    library_namespace,
    sites_namespace,
    trial_network_namespace,
    user_namespace,
)
from core.utils.os import (
    TEMP_DIRECTORY_PATH,
    TRIAL_NETWORKS_DIRECTORY_PATH,
    make_directory,
)

app = Flask(__name__)
CORS(app=app)
JWTManager(app=app)

app.config.from_object(obj=FlaskConf)

init_db()

api = Api(
    app=app,
    description="[[6G-SANDBOX] TNLCM](https://github.com/6G-SANDBOX/TNLCM)",
    doc="/",
    title="Trial Network Lifecycle Manager - TNLCM",
    version="1.0",
)

make_directory(path=TEMP_DIRECTORY_PATH)
make_directory(path=TRIAL_NETWORKS_DIRECTORY_PATH)

api.add_namespace(ns=callback_namespace, path="/api/v1/callback")
if FlaskConf.FLASK_ENV == "development":
    api.add_namespace(ns=debug_namespace, path="/api/v1/debug")
api.add_namespace(ns=library_namespace, path="/api/v1/library")
api.add_namespace(ns=sites_namespace, path="/api/v1/sites")
api.add_namespace(ns=trial_network_namespace, path="/api/v1/trial-network")
api.add_namespace(ns=user_namespace, path="/api/v1/user")
