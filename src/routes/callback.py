from flask import request
from flask_restx import Namespace, Resource, abort
from json import JSONDecodeError

from src.callback.jenkins_handler import JenkinsHandler

callback_namespace = Namespace(
    name="callback",
    description="Handling the data returned by jenkins after deploying the components"
)

@callback_namespace.route("")
class Callback(Resource):

    def __init__(self, api):
        self.api = api
        self.jenkins_handler = JenkinsHandler()

    @callback_namespace.response(200, "Success")
    @callback_namespace.response(400, "Invalid callback format")
    @callback_namespace.response(422, "Malformed or insecure callback received")
    def post(self):
        """
        Get jenkins results from deploying components
        """
        try:
            data = request.get_json()
            self.jenkins_handler.save_decoded_information(data)
            return {"message": "Stored coded information"}, 200
        except JSONDecodeError as e:
            return abort(400, 'Invalid JSON format')
        except Exception as e:
            return abort(422, 'Malformed or insecure callback received')