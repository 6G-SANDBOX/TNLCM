from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.datastructures import FileStorage

from src.jenkins.jenkins_handler import JenkinsHandler
from src.database.mongo_handler import MongoHandler
from src.sixglibrary.sixglibrary_handler import SixGLibraryHandler
from src.sixgsandbox_sites.sixgsandbox_sites_handler import SixGSandboxSitesHandler
from src.temp.temp_file_handler import TempFileHandler
from src.callback.callback_handler import CallbackHandler
from src.trial_network.trial_network_descriptor import TrialNetworkDescriptorHandler
from src.trial_network.trial_network_handler import TrialNetworkHandler
from src.exceptions.exceptions_handler import CustomException

trial_network_namespace = Namespace(
    name="trial_network",
    description="Namespace for trial network status and management",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        }
    }
)

@trial_network_namespace.route("")
class CreateTrialNetwork(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("descriptor", location="files", type=FileStorage, required=True)

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @trial_network_namespace.expect(parser_post)
    def post(self):
        """
        Add a trial network to database
        """
        mongo_handler = None
        try:
            descriptor = self.parser_post.parse_args()["descriptor"]

            mongo_handler = MongoHandler()
            current_user = get_jwt_identity()
            trial_network_descriptor_handler = TrialNetworkDescriptorHandler(current_user=current_user, descriptor=descriptor)
            trial_network_handler = TrialNetworkHandler(mongo_handler=mongo_handler, current_user=current_user)
            if not trial_network_handler.get_trial_network():
                trial_network_descriptor_handler.check_descriptor()
                trial_network_descriptor_handler.add_entity_mandatory_tn_vxlan()
                trial_network_descriptor_handler.add_entity_mandatory_tn_bastion()
                tn_raw_descriptor, tn_sorted_descriptor = trial_network_descriptor_handler.sort_descriptor()
                trial_network_handler.add_trial_network(tn_raw_descriptor, tn_sorted_descriptor)
                tn_id = trial_network_handler.tn_id
                return {"tn_id": tn_id}, 201
            else:
                return abort(409, f"Trial network with the name '{tn_id}' created earlier by user '{current_user}' in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()

@trial_network_namespace.route("/<string:tn_id>")
class TrialNetwork(Resource):

    parser_put = reqparse.RequestParser()
    parser_put.add_argument("branch", type=str, required=False)
    parser_put.add_argument("commit_id", type=str, required=False)

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self, tn_id):
        """
        Return the descriptor of the trial network specified in tn_id
        """
        mongo_handler = None
        try:
            mongo_handler = MongoHandler()
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(mongo_handler=mongo_handler, current_user=current_user, tn_id=tn_id)
            if trial_network_handler.get_trial_network():
                tn_sorted_descriptor = trial_network_handler.get_trial_network_descriptor()
                return tn_sorted_descriptor, 200
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @trial_network_namespace.expect(parser_put)
    def put(self, tn_id):
        """
        Trial network entities deployment begins
        **Can specify a branch or a commit_id of the 6G-Library. If nothing is specified, the main branch will be used**
        """
        mongo_handler = None
        try:
            branch = self.parser_put.parse_args()["branch"]
            commit_id = self.parser_put.parse_args()["commit_id"]
            
            mongo_handler = MongoHandler()
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(mongo_handler=mongo_handler, current_user=current_user, tn_id=tn_id)
            if trial_network_handler.get_trial_network():
                sixglibrary_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
                temp_file_handler = TempFileHandler()
                sixgsandbox_sites_handler = SixGSandboxSitesHandler()
                callback_handler = CallbackHandler(trial_network_handler=trial_network_handler, sixgsandbox_sites_handler=sixgsandbox_sites_handler)
                jenkins_handler = JenkinsHandler(trial_network_handler=trial_network_handler, sixglibrary_handler=sixglibrary_handler, temp_file_handler=temp_file_handler, callback_handler=callback_handler)
                jenkins_handler.trial_network_deployment()
                return {"message": "Trial network deployed with jenkins"}, 200
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()
    
    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def delete(self, tn_id):
        """
        Delete a trial network specified in tn_id
        """
        mongo_handler = None
        try:
            mongo_handler = MongoHandler()
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(mongo_handler=mongo_handler, current_user=current_user, tn_id=tn_id)
            if trial_network_handler.get_trial_network():
                trial_network_handler.delete_trial_network()
                return {"message": f"The trial network with identifier '{tn_id}' has been removed from the database"}, 200
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()

@trial_network_namespace.route("/status/<string:tn_id>") 
class SpecificTrialNetworkStatus(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self, tn_id):
        """
        Return the status of the trial network specified in tn_id
        """
        mongo_handler = None
        try:
            mongo_handler = MongoHandler()
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(mongo_handler=mongo_handler, current_user=current_user, tn_id=tn_id)
            if trial_network_handler.get_trial_network():
                trial_network_status = trial_network_handler.get_trial_network_status()
                return trial_network_status, 200
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()
    
    parser_put = reqparse.RequestParser()
    parser_put.add_argument("new_status", type=str, required=True)

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @trial_network_namespace.expect(parser_put)
    def put(self, tn_id):
        """
        Update the status of the trial network specified in tn_id
        """
        mongo_handler = None
        try:
            new_status = self.parser_put.parse_args()["new_status"]

            mongo_handler = MongoHandler()
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(mongo_handler=mongo_handler, current_user=current_user, tn_id=tn_id)
            if trial_network_handler.get_trial_network():
                trial_network_handler.update_trial_network_status(new_status)
                return {"message": f"The status of the trial network with identifier '{tn_id}' has been updated to '{new_status}'"}, 200
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()

@trial_network_namespace.route("/report/<string:tn_id>") 
class TrialNetworkReport(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self, tn_id):
        """Return the report generated after the execution of the entities of a trial network"""
        mongo_handler = None
        try:
            mongo_handler = MongoHandler()
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(mongo_handler=mongo_handler, current_user=current_user, tn_id=tn_id)
            if trial_network_handler.get_trial_network():
                tn_report = trial_network_handler.get_trial_network_report()
                if tn_report:
                    return tn_report, 200
                else:
                    abort(404, f"Trial network '{tn_id}' has not been deployed yet")
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()

@trial_network_namespace.route("s/") 
class TrialNetworks(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self):
        """
        Return information of all trial networks stored in database
        """
        mongo_handler = None
        try:
            mongo_handler = MongoHandler()
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(mongo_handler=mongo_handler, current_user=current_user)
            trial_networks = trial_network_handler.get_trial_networks()
            return {"trial_networks": trial_networks}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()

@trial_network_namespace.route("s/templates/")
class TrialNetworksTemplates(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self):
        """
        Return trial networks templates
        """
        mongo_handler = None
        try:
            mongo_handler = MongoHandler()
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(mongo_handler=mongo_handler, current_user=current_user)
            trial_networks_templates = trial_network_handler.get_trial_networks_templates()
            return {"trial_networks_templates": trial_networks_templates}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()
    
    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=True)
    parser_post.add_argument("descriptor", location="files", type=FileStorage, required=True)

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @trial_network_namespace.expect(parser_post)
    def post(self):
        """
        Create and add a trial network template to database
        """
        mongo_handler = None
        try:
            tn_id = self.parser_post.parse_args()["tn_id"]
            descriptor = self.parser_post.parse_args()["descriptor"]

            mongo_handler = MongoHandler()
            current_user = get_jwt_identity()
            trial_network_descriptor_handler = TrialNetworkDescriptorHandler(current_user=current_user, descriptor=descriptor)
            trial_network_handler = TrialNetworkHandler(mongo_handler=mongo_handler, current_user=current_user, tn_id=tn_id)
            trial_network_descriptor_handler.check_descriptor()
            trial_network_descriptor_handler.add_entity_mandatory_tn_vxlan()
            trial_network_descriptor_handler.add_entity_mandatory_tn_bastion()
            tn_raw_descriptor, tn_sorted_descriptor = trial_network_descriptor_handler.sort_descriptor()
            trial_network_handler.add_trial_network_template(tn_raw_descriptor, tn_sorted_descriptor)
            return {"tn_id": tn_id}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if mongo_handler is not None:
                mongo_handler.disconnect()