from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.datastructures import FileStorage

from core.auth.auth import get_current_user_from_jwt
from core.callback.callback_handler import CallbackHandler
from core.jenkins.jenkins_handler import JenkinsHandler
from core.models import TrialNetworkModel, TrialNetworkTemplateModel
from core.sixg_library.sixg_library_handler import SixGLibraryHandler
from core.sixg_sandbox_sites.sixg_sandbox_sites_handler import SixGSandboxSitesHandler
from core.temp.temp_file_handler import TempFileHandler

from core.exceptions.exceptions_handler import CustomException

trial_network_namespace = Namespace(
    name="trial-network",
    description="Namespace for trial network status and management",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        }
    }
)

##### ------ Trial Network ------ #####
@trial_network_namespace.route("")
class CreateTrialNetwork(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=False)
    parser_post.add_argument("descriptor", location="files", type=FileStorage, required=True)

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @trial_network_namespace.expect(parser_post)
    def post(self):
        """
        Create and validate trial network
        """
        try:
            tn_id = self.parser_post.parse_args()["tn_id"]
            tn_descriptor_file = self.parser_post.parse_args()["descriptor"]

            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel(
                user_created=current_user.username
            )
            trial_network.set_tn_id(size=3, tn_id=tn_id)
            trial_network.set_tn_state("suspended") # FIX: add validate state before suspend
            trial_network.set_tn_raw_descriptor(tn_descriptor_file)
            trial_network.set_tn_sorted_descriptor()
            trial_network.save()
            return trial_network.to_dict(), 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@trial_network_namespace.route("/<string:tn_id>")
class TrialNetwork(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self, tn_id):
        """
        Return trial network
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if not trial_network:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the database")
            return trial_network.to_dict_full(), 200
        except CustomException as e:
            return abort(e.error_code, str(e))
    
    parser_put = reqparse.RequestParser()
    parser_put.add_argument("branch", type=str, required=False)
    parser_put.add_argument("commit_id", type=str, required=False)

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @trial_network_namespace.expect(parser_put)
    def put(self, tn_id):
        """
        Play or suspend trial network
        Can specify a branch or a commit_id of the 6G-Library. **If nothing is specified, the main branch will be used.**
        """
        try:
            branch = self.parser_put.parse_args()["branch"]
            commit_id = self.parser_put.parse_args()["commit_id"]
            
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if not trial_network:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the database")
            tn_state = trial_network.tn_state
            # TODO: State machine with checks
            if tn_state == "suspended":
                sixg_library_handler = SixGLibraryHandler(branch=branch, commit_id=commit_id)
                temp_file_handler = TempFileHandler()
                sixg_sandbox_sites_handler = SixGSandboxSitesHandler()
                callback_handler = CallbackHandler(trial_network=trial_network, sixg_sandbox_sites_handler=sixg_sandbox_sites_handler)
                jenkins_handler = JenkinsHandler(trial_network=trial_network, sixg_library_handler=sixg_library_handler, sixg_sandbox_sites_handler=sixg_sandbox_sites_handler, temp_file_handler=temp_file_handler, callback_handler=callback_handler)
                jenkins_handler.trial_network_deployment()
                trial_network.set_tn_report(callback_handler.get_path_report_trial_network())
                trial_network.set_tn_state("active")
                return {"message": "Trial network deployed with jenkins"}, 200
            elif tn_state == "active":
                pass
            else:
                pass
        except CustomException as e:
            return abort(e.error_code, str(e))

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def delete(self, tn_id):
        """
        Delete trial network
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if not trial_network:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the database")
            trial_network.delete()
            return {"message": f"The trial network with identifier '{tn_id}' has been removed from the database"}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@trial_network_namespace.route("/report/<string:tn_id>") 
class TrialNetworkReport(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self, tn_id):
        """Return the report generated after the execution of the entities of a trial network"""
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if not trial_network:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the database")
            return {"tn_report": trial_network.tn_report}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@trial_network_namespace.route("s/") 
class TrialNetworks(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self):
        """
        Return information of all trial networks stored in database created by user identified
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_networks = TrialNetworkModel.objects(user_created=current_user.username)
            return {'trial_networks': [tn.to_dict_full() for tn in trial_networks]}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

##### ------ Trial Network Template ------ #####
@trial_network_namespace.route("/template/<string:tn_id>")
class CreateTrialNetworkTemplate(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("descriptor", location="files", type=FileStorage, required=True)

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @trial_network_namespace.expect(parser_post)
    def post(self, tn_id):
        """
        Add a trial network template
        """
        try:
            tn_descriptor_file = self.parser_post.parse_args()["descriptor"]

            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network_template = TrialNetworkTemplateModel(
                user_created=current_user.username
            )
            trial_network_template.set_tn_id(tn_id=tn_id)
            trial_network_template.set_tn_raw_descriptor(tn_descriptor_file)
            trial_network_template.set_tn_sorted_descriptor()
            trial_network_template.save()
            return trial_network_template.to_dict(), 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@trial_network_namespace.route("s/templates/")
class TrialNetworksTemplates(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self):
        """
        Return trial networks templates
        """
        try:
            trial_networks = TrialNetworkTemplateModel.objects()
            return {'trial_networks_templates': [tn.to_dict_full() for tn in trial_networks]}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))