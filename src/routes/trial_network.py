from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.datastructures import FileStorage

from src.callback.jenkins_handler import JenkinsHandler
from src.trial_network.trial_network_descriptor import TrialNetworkDescriptorHandler
from src.trial_network.trial_network_handler import TrialNetworkHandler
from src.exceptions.exceptions_handler import CustomException

trial_network_namespace = Namespace(
    name="trial_network",
    description="Trial network status and management",
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
        Create and add a trial network to database
        """
        trial_network_handler = None
        try:
            descriptor = self.parser_post.parse_args()["descriptor"]

            current_user = get_jwt_identity()
            trial_network_descriptor_handler = TrialNetworkDescriptorHandler(current_user, descriptor)
            trial_network_handler = TrialNetworkHandler(current_user)
            if not trial_network_handler.get_trial_network():
                trial_network_descriptor_handler.check_descriptor()
                trial_network_descriptor_handler.add_entity_mandatory_tn_vxlan()
                trial_network_descriptor_handler.add_entity_mandatory_tn_bastion()
                tn_raw_descriptor, tn_sorted_descriptor = trial_network_descriptor_handler.sort_descriptor()
                trial_network_handler.create_trial_network(tn_raw_descriptor, tn_sorted_descriptor)
                tn_id = trial_network_handler.tn_id
                return {"tn_id": tn_id}, 201
            else:
                return abort(409, f"Trial network with the name '{tn_id}' created earlier by user '{current_user}' in the trial_network collection in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if trial_network_handler is not None:
                trial_network_handler.mongo_client.disconnect()

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
        trial_network_handler = None
        try:
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(current_user, tn_id)
            if trial_network_handler.get_trial_network():
                sorted_descriptor = trial_network_handler.get_descriptor_trial_network()
                return {"tn_descriptor": sorted_descriptor}, 200
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the trial_network collection in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if trial_network_handler is not None:
                trial_network_handler.mongo_client.disconnect()

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @trial_network_namespace.expect(parser_put)
    def put(self, tn_id):
        """
        Trial network entities deployment begins
        **Can specify a branch or a commit_id of the 6G-Library. If nothing is specified, the main branch will be used**
        """
        trial_network_handler = None
        try:
            branch = self.parser_put.parse_args()["branch"]
            commit_id = self.parser_put.parse_args()["commit_id"]
            
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(current_user, tn_id)
            if trial_network_handler.get_trial_network():
                self.jenkins_handler = JenkinsHandler(trial_network_handler)
                self.jenkins_handler.deploy_trial_network(branch=branch, commit_id=commit_id)
                return {"message": "Trial network deployed with jenkins"}, 200
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the trial_network collection in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if trial_network_handler is not None:
                trial_network_handler.mongo_client.disconnect()
    
    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def delete(self, tn_id):
        """
        Delete a trial network specified in tn_id
        """
        trial_network_handler = None
        try:
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(current_user, tn_id)
            if trial_network_handler.get_trial_network():
                trial_network_handler.delete_trial_network()
                return {"message": f"The trial network with identifier '{tn_id}' has been removed from the database"}, 200
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the trial_network collection in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if trial_network_handler is not None:
                trial_network_handler.mongo_client.disconnect()

@trial_network_namespace.route("/status/<string:tn_id>") 
class StatusSpecificTrialNetwork(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self, tn_id):
        """
        Return the status of the trial network specified in tn_id
        """
        trial_network_handler = None
        try:
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(current_user, tn_id)
            if trial_network_handler.get_trial_network():
                status_trial_network = trial_network_handler.get_status_trial_network()
                return {"tn_status": status_trial_network}, 200
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the trial_network collection in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if trial_network_handler is not None:
                trial_network_handler.mongo_client.disconnect()
    
    parser_put = reqparse.RequestParser()
    parser_put.add_argument("new_status", type=str, required=True)

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @trial_network_namespace.expect(parser_put)
    def put(self, tn_id):
        """
        Update the status of the trial network specified in tn_id
        """
        trial_network_handler = None
        try:
            new_status = self.parser_put.parse_args()["new_status"]

            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(current_user, tn_id)
            if trial_network_handler.get_trial_network():
                trial_network_handler.update_status_trial_network(new_status)
                return {"message": f"The status of the trial network with identifier '{tn_id}' has been updated to '{new_status}'"}, 200
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the trial_network collection in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if trial_network_handler is not None:
                trial_network_handler.mongo_client.disconnect()

@trial_network_namespace.route("/report/<string:tn_id>") 
class ReportTrialNetwork(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self, tn_id):
        """Return the report generated after the execution of the entities of a trial network"""
        trial_network_handler = None
        try:
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(current_user, tn_id)
            if trial_network_handler.get_trial_network():
                tn_report = trial_network_handler.get_report_trial_network()
                if tn_report:
                    return {"tn_report": tn_report}, 200
                else:
                    abort(404, f"Trial network '{tn_id}' has not been deployed yet")
            else:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the trial_network collection in the database '{trial_network_handler.mongo_client.database}'")
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if trial_network_handler is not None:
                trial_network_handler.mongo_client.disconnect()

@trial_network_namespace.route("s/") 
class TrialNetworks(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self):
        """
        Return all the trial networks stored in database
        """
        trial_network_handler = None
        try:
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(current_user)
            trial_networks = trial_network_handler.get_trial_networks()
            return {"tn_ids": trial_networks}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if trial_network_handler is not None:
                trial_network_handler.mongo_client.disconnect()

@trial_network_namespace.route("s/status/") 
class StatusTrialNetwork(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self):
        """
        Return the status of the trial networks
        """
        trial_network_handler = None
        try:
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(current_user)
            status_trial_networks = trial_network_handler.get_status_trial_networks()
            return {"trial_networks_status": status_trial_networks}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if trial_network_handler is not None:
                trial_network_handler.mongo_client.disconnect()

@trial_network_namespace.route("s/templates/")
class TemplatesTrialNetworks(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self):
        """
        Return trial networks templates
        """
        trial_network_handler = None
        try:
            current_user = get_jwt_identity()
            trial_network_handler = TrialNetworkHandler(current_user)
            trial_networks_templates = trial_network_handler.get_trial_networks_templates()
            return {"trial_networks_templates": trial_networks_templates}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if trial_network_handler is not None:
                trial_network_handler.mongo_client.disconnect()
    
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
        trial_network_handler = None
        try:
            tn_id = self.parser_post.parse_args()["tn_id"]
            descriptor = self.parser_post.parse_args()["descriptor"]

            current_user = get_jwt_identity()
            trial_network_descriptor_handler = TrialNetworkDescriptorHandler(current_user, descriptor)
            trial_network_handler = TrialNetworkHandler(current_user, tn_id)
            trial_network_descriptor_handler.check_descriptor()
            trial_network_descriptor_handler.add_entity_mandatory_tn_vxlan()
            trial_network_descriptor_handler.add_entity_mandatory_tn_bastion()
            tn_raw_descriptor, tn_sorted_descriptor = trial_network_descriptor_handler.sort_descriptor()
            trial_network_handler.create_trial_network_template(tn_raw_descriptor, tn_sorted_descriptor)
            return {"tn_id": tn_id}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))
        finally:
            if trial_network_handler is not None:
                trial_network_handler.mongo_client.disconnect()