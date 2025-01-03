from flask_restx import Namespace, reqparse, Resource, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError

from core.auth.auth import get_current_user_from_jwt
from core.logs.log_handler import log_handler
from core.models import TrialNetworkModel
from core.sixg_library.sixg_library_handler import SixGLibraryHandler
from core.sixg_sandbox_sites.sixg_sandbox_sites_handler import SixGSandboxSitesHandler
from core.jenkins.jenkins_handler import JenkinsHandler
from core.exceptions.exceptions_handler import CustomException

debug_namespace = Namespace(
    name="debug",
    description="Namespace for debug only for developers",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        }
    }
)

@debug_namespace.route("/trial-network/6G-Library/commit")
class UpdateCommitSixGLibrary(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=True)
    parser_post.add_argument("commit_id", type=str, required=True)

    @debug_namespace.doc(security="Bearer Auth")
    @debug_namespace.errorhandler(PyJWTError)
    @debug_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @debug_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Update the 6G-Library commit associated with the trial network 
        """
        try:
            tn_id = self.parser_post.parse_args()["tn_id"]
            commit_id = self.parser_post.parse_args()["commit_id"]
            
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            
            sixg_library_handler = SixGLibraryHandler(https_url=trial_network.github_6g_library_https_url, reference_type="commit", reference_value=trial_network.github_6g_library_commit_id, directory_path=trial_network.directory_path)
            sixg_library_handler.git_switch()
            trial_network.set_github_6g_library_commit_id(commit_id)
            trial_network.save()
            return {"message": "Commit successfully modified"}, 201
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            log_handler.error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))

@debug_namespace.route("/trial-network/6G-Sandbox-Sites/commit")
class UpdateCommitSixGSandboxSites(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=True)
    parser_post.add_argument("commit_id", type=str, required=True)

    @debug_namespace.doc(security="Bearer Auth")
    @debug_namespace.errorhandler(PyJWTError)
    @debug_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @debug_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Update the 6G-Sandbox-Sites commit associated with the trial network 
        """
        try:
            tn_id = self.parser_post.parse_args()["tn_id"]
            commit_id = self.parser_post.parse_args()["commit_id"]
            
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            
            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(https_url=trial_network.github_6g_sandbox_sites_https_url, reference_type="commit", reference_value=trial_network.github_6g_library_commit_id, directory_path=trial_network.directory_path)
            sixg_sandbox_sites_handler.git_switch()
            trial_network.set_github_6g_sandbox_sites_commit_id(commit_id)
            trial_network.save()
            return {"message": "Commit successfully modified"}, 201
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            log_handler.error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))

@debug_namespace.route("/trial-network/add-debug-entity-name")
class AddDebugEntityName(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=True)
    parser_post.add_argument("entity_name", type=str, required=True)

    @debug_namespace.doc(security="Bearer Auth")
    @debug_namespace.errorhandler(PyJWTError)
    @debug_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @debug_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Add debug: true to the specified entity name 
        """
        try:
            tn_id = self.parser_post.parse_args()["tn_id"]
            entity_name = self.parser_post.parse_args()["entity_name"]
            
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            raw_descriptor = trial_network.raw_descriptor
            sorted_descriptor = trial_network.sorted_descriptor
            deployed_descriptor = trial_network.deployed_descriptor
            raw_descriptor["trial_network"][entity_name]["debug"] = True
            sorted_descriptor["trial_network"][entity_name]["debug"] = True
            deployed_descriptor["trial_network"][entity_name]["debug"] = True
            trial_network.raw_descriptor = raw_descriptor
            trial_network.sorted_descriptor = sorted_descriptor
            trial_network.deployed_descriptor = deployed_descriptor
            trial_network.save()
            return {"message": f"Successfully added debug into '{entity_name}' entity name of the Trial Network '{tn_id}'"}, 201
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            log_handler.error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))

@debug_namespace.route("/trial-network/delete-debug-entity-name")
class DeleteDebugEntityName(Resource):
    
    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=True)
    parser_post.add_argument("entity_name", type=str, required=True)

    @debug_namespace.doc(security="Bearer Auth")
    @debug_namespace.errorhandler(PyJWTError)
    @debug_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @debug_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Delete debug: true to the specified entity name 
        """
        try:
            tn_id = self.parser_post.parse_args()["tn_id"]
            entity_name = self.parser_post.parse_args()["entity_name"]
            
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            raw_descriptor = trial_network.raw_descriptor["trial_network"]
            sorted_descriptor = trial_network.sorted_descriptor["trial_network"]
            deployed_descriptor = trial_network.deployed_descriptor["trial_network"]
            del raw_descriptor[entity_name]["debug"]
            del sorted_descriptor[entity_name]["debug"]
            del deployed_descriptor[entity_name]["debug"]
            trial_network.raw_descriptor = raw_descriptor
            trial_network.sorted_descriptor = sorted_descriptor
            trial_network.deployed_descriptor = deployed_descriptor
            trial_network.save()
            return {"message": f"Successfully deleted debug into '{entity_name}' entity name of the Trial Network '{tn_id}'"}, 201
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            log_handler.error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))

@debug_namespace.route("/jenkins/pipelines/")
class JenkinsPipelines(Resource):

    @debug_namespace.doc(security="Bearer Auth")
    @debug_namespace.errorhandler(PyJWTError)
    @debug_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self) -> tuple[dict, int]:
        """
        Return pipelines stored in Jenkins
        """
        try:
            jenkins_handler = JenkinsHandler()
            return {"pipelines": jenkins_handler.get_all_pipelines()}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code