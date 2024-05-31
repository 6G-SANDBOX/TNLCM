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

###############################
######## Trial Network ########
###############################
@trial_network_namespace.route("")
class CreateTrialNetwork(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=False)
    parser_post.add_argument("descriptor", location="files", type=FileStorage, required=True)
    parser_post.add_argument("deployment_site", type=str, required=True)
    parser_post.add_argument("github_6g_library_branch", type=str, required=False)
    parser_post.add_argument("github_6g_library_commit_id", type=str, required=False)
    parser_post.add_argument("github_6g_library_tag", type=str, required=False)
    parser_post.add_argument("github_6g_sandbox_sites_branch", type=str, required=False)
    parser_post.add_argument("github_6g_sandbox_sites_commit_id", type=str, required=False)
    parser_post.add_argument("github_6g_sandbox_sites_tag", type=str, required=False)

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @trial_network_namespace.expect(parser_post)
    def post(self):
        """
        Create and validate trial network
        Can specify a branch, commit_id or tag of the 6G-Library. **If nothing is specified, the main branch will be used.**
        Can specify a branch, commit_id or tag of the 6G-Sandbox-Sites. **If nothing is specified, the main branch will be used.**
        The tn_id can be specified if desired. **If nothing is specified, it will return a random tn_id.**
        """
        try:
            tn_id = self.parser_post.parse_args()["tn_id"]
            tn_descriptor_file = self.parser_post.parse_args()["descriptor"]
            deployment_site = self.parser_post.parse_args()["deployment_site"]
            github_6g_library_branch = self.parser_post.parse_args()["github_6g_library_branch"]
            github_6g_library_commit_id = self.parser_post.parse_args()["github_6g_library_commit_id"]
            github_6g_library_tag = self.parser_post.parse_args()["github_6g_library_tag"]
            github_6g_sandbox_sites_branch = self.parser_post.parse_args()["github_6g_sandbox_sites_branch"]
            github_6g_sandbox_sites_commit_id = self.parser_post.parse_args()["github_6g_sandbox_sites_commit_id"]
            github_6g_sandbox_sites_tag = self.parser_post.parse_args()["github_6g_sandbox_sites_tag"]

            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel(
                user_created=current_user.username
            )
            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(branch=github_6g_sandbox_sites_branch, commit_id=github_6g_sandbox_sites_commit_id, tag=github_6g_sandbox_sites_tag)
            sixg_sandbox_sites_handler.set_deployment_site(deployment_site)
            sixg_library_handler = SixGLibraryHandler(branch=github_6g_library_branch, commit_id=github_6g_library_commit_id, tag=github_6g_library_tag, site=deployment_site)
            parts_components = sixg_library_handler.get_parts_components()
            components_available = list(parts_components.keys())
            trial_network.set_tn_id(size=3, tn_id=tn_id)
            trial_network.set_tn_state("validated")
            trial_network.set_tn_raw_descriptor(tn_descriptor_file)
            trial_network.set_tn_sorted_descriptor()
            trial_network.set_deployment_site(deployment_site)
            trial_network.check_descriptor_component_types_site(components_available)
            trial_network.set_github_6g_library_branch(github_6g_library_branch)
            trial_network.set_github_6g_sandbox_sites_branch(github_6g_sandbox_sites_branch)
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
    parser_put.add_argument("job_name", type=str, required=False)

    @trial_network_namespace.doc(security="Bearer Auth")
    @jwt_required()
    @trial_network_namespace.expect(parser_put)
    def put(self, tn_id):
        """
        Play or suspend trial network
        If nothing is specified in job_name, the 02_Trial_Network_Component job will be used.
        """
        try:
            job_name = self.parser_put.parse_args()["job_name"]
            
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if not trial_network:
                return abort(404, f"No trial network with the name '{tn_id}' created by the user '{current_user}' in the database")
            tn_state = trial_network.tn_state
            # TODO: State machine with checks
            if tn_state == "validated":
                temp_file_handler = TempFileHandler()
                callback_handler = CallbackHandler(trial_network=trial_network)
                jenkins_handler = JenkinsHandler(trial_network=trial_network, temp_file_handler=temp_file_handler, callback_handler=callback_handler)
                jenkins_handler.set_job_name(job_name)
                trial_network.set_job_name(job_name)
                jenkins_handler.trial_network_deployment()
                trial_network.set_tn_report(callback_handler.get_path_report_trial_network())
                trial_network.set_tn_state("activated")
                trial_network.save()
                return {"message": "Trial network activated"}, 200
            elif tn_state == "activated":
                trial_network.set_tn_state("suspended")
                trial_network.save()
            else: # tn_state == "suspended"
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

##############################
### Trial Network Template ###
##############################
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