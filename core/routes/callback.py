from flask import request
from flask_restx import Namespace, Resource, abort

from core.models import CallbackModel, TrialNetworkModel
from core.logs.log_handler import log_handler
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
            data = request.get_json()
            callback_model = CallbackModel()
            decoded_data = callback_model.decode_data(data=data)
            
            trial_network = TrialNetworkModel.objects(tn_id=callback_model.tn_id).first()
            if not trial_network:
                return {"message": f"No trial network with the name '{callback_model.tn_id}' in database"}, 404
            
            log_handler.info(f"[{callback_model.tn_id}] - Save entity deployment results received by Jenkins")
            
            if callback_model.success != "true":
                return {"message": f"Pipeline for entity '{callback_model.entity_name}' failed"}, 500

            if not callback_model.matches_expected_output():
                return {"message": "Output keys received by Jenkins does not match output keys from the 6G-Library"}, 500
            log_handler.info(f"[{callback_model.tn_id}] - Output keys received by Jenkins match with output keys from the 6G-Library")
            
            callback_model.save_data_file(data=decoded_data)
            callback_model.save()
            return {"message": f"Results of '{callback_model.entity_name}' entity received by jenkins saved"}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            log_handler.error(f"[{callback_model.tn_id}] - {e}")
            return abort(500, str(e))