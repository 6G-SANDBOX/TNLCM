from flask import Flask
from api import api
from shared import Log

app = Flask(__name__)
api.init_app(app)

Log.Initialize(outFolder='.', logName='API', consoleLevel='DEBUG', fileLevel='DEBUG', app=app)

if __name__ == "__main__":
    app.run()
