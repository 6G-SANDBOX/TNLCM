from flask import request
from flask_restx import Namespace, Resource, abort

from src.callback.callback_handler import CallbackHandler
from src.exceptions.exceptions_handler import CustomException

callback_namespace = Namespace(
    name="callback",
    description="Namespace for handler the data returned by Jenkins after deploying the components"
)

@callback_namespace.route("")
class Callback(Resource):
    
    def post(self):
        """
        Save Jenkins results from deploying components
        """
        try:
            data = request.get_json()
            callback_handler = CallbackHandler(data)
            callback_handler.save_decoded_results()
            return {"message": "Save results received by Jenkins"}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))