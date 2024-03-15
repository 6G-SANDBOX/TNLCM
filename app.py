import os

from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from waitress import serve

from config import Config
from src.routes import trial_network_namespace, callback_namespace
from logs.log_handler import LogHandler
from src.repository.repository_handler import RepositoryHandler
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
load_dotenv()

api = Api(
    app,
    title="Trial Network Lifecycle Manager",
    version="0.1.0",
    description="Repository: https://github.com/CarlosAndreo/TNLCM",
    # doc=False
)

api.add_namespace(trial_network_namespace, path="/api/trial_network")
api.add_namespace(callback_namespace, path="/api/callback")

if __name__ == "__main__":
    LogHandler()
    sixg_repository = RepositoryHandler(os.getenv("6GLIBRARY_REPOSITORY_HTTPS"))
    sixg_repository.clone_repository("6glibrary", "main")
    flask_env = os.getenv("FLASK_ENV")
    if flask_env == "DEVELOPMENT":
        app.run(host="0.0.0.0", port=5000, debug=True)
    elif flask_env == "PRODUCTION":
        serve(app, host="0.0.0.0", port=5000)
    else:
        app.run(host="0.0.0.0", port=5000)