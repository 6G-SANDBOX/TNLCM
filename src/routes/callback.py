from flask import request
from flask_restx import Namespace, Resource, abort

from src.callback.jenkins_handler import JenkinsHandler
from src.exceptions.exceptions_handler import CustomException

callback_namespace = Namespace(
    name="callback",
    description="Handling the data returned by jenkins after deploying the components"
)

@callback_namespace.route("")
class Callback(Resource):
    
    def post(self):
        """
        Save jenkins results from deploying components
        """
        try:
            data = request.get_json()
            jenkins_handler = JenkinsHandler()
            jenkins_handler.save_decoded_information(data)
            return {"message": "Stored coded information"}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))