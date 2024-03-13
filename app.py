from flask import Flask, current_app
from flask_restx import Api
from flask_cors import CORS
from waitress import serve

from config import Config

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

api = Api(
    app,
    title="Trial Network Lifecycle Manager",
    version="0.1.0",
    description="Repository: https://github.com/CarlosAndreo/TNLCM",
    # doc=False
)

if __name__ == "__main__":
    with app.app_context():
        flask_env = current_app.config["FLASK_ENV"]
        if flask_env == "DEVELOPMENT":
            app.run(host="0.0.0.0", port=5000, debug=True)
        elif flask_env == "PRODUCTION":
            serve(app, host="0.0.0.0", port=5000)
        else:
            app.run(host="0.0.0.0", port=5000)