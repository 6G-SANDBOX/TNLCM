import os

from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from waitress import serve
from dotenv import load_dotenv

from config import Config
from src.routes import trial_network_namespace, callback_namespace, sixglibrary_namespace, users_namespace
from src.logs.log_handler import LogHandler

app = Flask(__name__)
CORS(app)
JWTManager(app)

app.config.from_object(Config)
load_dotenv()

api = Api(
    app,
    title="Trial Network Lifecycle Manager",
    version="0.2.0",
    description="Repository: https://github.com/6G-SANDBOX/TNLCM",
    # doc=False
)

api.add_namespace(trial_network_namespace, path="/tnlcm/trial_network")
api.add_namespace(callback_namespace, path="/tnlcm/callback")
api.add_namespace(sixglibrary_namespace, path="/tnlcm/6glibrary")
api.add_namespace(users_namespace, path="/tnlcm/user")

LogHandler()

if __name__ == "__main__":
    flask_env = os.getenv("FLASK_ENV")
    if flask_env == "DEVELOPMENT":
        app.run(host="0.0.0.0", port=5000)
    elif flask_env == "PRODUCTION":
        serve(app, host="0.0.0.0", port=5000)
    else:
        app.run(host="0.0.0.0", port=5000)