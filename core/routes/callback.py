from flask import request
from flask_restx import Namespace, Resource, abort

from core.callback.callback_handler import CallbackHandler
from core.models import TrialNetworkModel
from core.logs.log_handler import TnLogHandler
from core.exceptions.exceptions_handler import CustomException

callback_namespace = Namespace(
    name="callback",
    description="Namespace for handler the data returned by Jenkins after deploying the components"
)

@callback_namespace.route("")
class Callback(Resource):
    
    def post(self) -> tuple[dict, int]:
        """
        Save Jenkins results from deploying components
        """
        try:
            encoded_data = request.get_json()
            callback_handler = CallbackHandler(encoded_data=encoded_data)
            trial_network = TrialNetworkModel.objects(tn_id=callback_handler.tn_id).first()
            if not trial_network:
                return {"message": f"No trial network with the name {callback_handler.tn_id} in database"}, 404
            
            if callback_handler.success != "true":
                return {"message": f"Pipeline for entity {callback_handler.entity_name} failed"}, 500
            
            # if not callback_handler.matches_expected_output():
            #     return {"message": "Output keys received by Jenkins does not match output keys from the Library"}, 500
            # TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Output keys received by Jenkins match with output keys from the Library")
            
            trial_network.set_output(callback_handler.entity_name, callback_handler.decoded_data)
            trial_network.save()
            callback_handler.save_data_file()
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Save entity deployment results received by Jenkins")
            return {"message": f"Results of {callback_handler.entity_name} entity received by jenkins saved"}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))