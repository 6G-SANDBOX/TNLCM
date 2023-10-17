import sys
sys.path.append('..')


from shared import Log
from Library import Library

Log.Initialize(outFolder='.', logName='Inventory', consoleLevel='DEBUG', fileLevel='DEBUG', app=None)
Library.Initialize()


from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from Api import playbook_api

app = Flask(__name__)
CORS(app)

api = Api(version='0.1')

api.add_namespace(playbook_api, path="/playbook")
api.init_app(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
