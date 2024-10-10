from flask_restx import Namespace, reqparse, Resource, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import ValidationError, MongoEngineException

from core.auth.auth import get_current_user_from_jwt
from core.models import TrialNetworkModel
from core.jenkins.jenkins_handler import JenkinsHandler
from core.exceptions.exceptions_handler import CustomException

debug_namespace = Namespace(
    name="debug",
    description="Namespace for debug only for developers",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        }
    }
)

@debug_namespace.route("/trial-network/6G-Library/commit")
class UpdateCommitSixGLibrary(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=True)
    parser_post.add_argument("commit_id", type=str, required=True)

    @debug_namespace.doc(security="Bearer Auth")
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
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            else:
                trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            trial_network.set_github_6g_library_commit_id(commit_id)
            trial_network.save()
            return {"message": "Commit successfully modified"}, 201
        except ValidationError as e:
            return abort(401, e.message)
        except MongoEngineException as e:
            return abort(401, str(e))
        except CustomException as e:
            return abort(e.error_code, str(e))

@debug_namespace.route("/trial-network/6G-Sandbox-Sites/commit")
class UpdateCommitSixGSandboxSites(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=True)
    parser_post.add_argument("commit_id", type=str, required=True)

    @debug_namespace.doc(security="Bearer Auth")
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
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            else:
                trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            trial_network.set_github_6g_sandbox_sites_commit_id(commit_id)
            trial_network.save()
            return {"message": "Commit successfully modified"}, 201
        except ValidationError as e:
            return abort(401, e.message)
        except MongoEngineException as e:
            return abort(401, str(e))
        except CustomException as e:
            return abort(e.error_code, str(e))

@debug_namespace.route("/trial-network/add-debug-entity-name")
class AddDebugEntityName(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=True)
    parser_post.add_argument("entity_name", type=str, required=True)

    @debug_namespace.doc(security="Bearer Auth")
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
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            else:
                trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            tn_raw_descriptor = trial_network.json_to_descriptor(trial_network.tn_raw_descriptor)
            tn_sorted_descriptor = trial_network.json_to_descriptor(trial_network.tn_sorted_descriptor)
            tn_deployed_descriptor = trial_network.json_to_descriptor(trial_network.tn_deployed_descriptor)
            tn_raw_descriptor["trial_network"][entity_name]["debug"] = True
            tn_sorted_descriptor["trial_network"][entity_name]["debug"] = True
            tn_deployed_descriptor["trial_network"][entity_name]["debug"] = True
            trial_network.tn_raw_descriptor = trial_network.descriptor_to_json(tn_raw_descriptor)
            trial_network.tn_sorted_descriptor = trial_network.descriptor_to_json(tn_sorted_descriptor)
            trial_network.tn_deployed_descriptor = trial_network.descriptor_to_json(tn_deployed_descriptor)
            trial_network.save()
            return {"message": f"Successfully added debug into '{entity_name}' entity name of the Trial Network '{tn_id}'"}, 201
        except ValidationError as e:
            return abort(401, e.message)
        except MongoEngineException as e:
            return abort(401, str(e))
        except CustomException as e:
            return abort(e.error_code, str(e))

@debug_namespace.route("/trial-network/delete-debug-entity-name")
class DeleteDebugEntityName(Resource):
    
    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=True)
    parser_post.add_argument("entity_name", type=str, required=True)

    @debug_namespace.doc(security="Bearer Auth")
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
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            else:
                trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            tn_raw_descriptor = trial_network.json_to_descriptor(trial_network.tn_raw_descriptor)
            tn_sorted_descriptor = trial_network.json_to_descriptor(trial_network.tn_sorted_descriptor)
            tn_deployed_descriptor = trial_network.json_to_descriptor(trial_network.tn_deployed_descriptor)
            del tn_raw_descriptor["trial_network"][entity_name]["debug"]
            del tn_sorted_descriptor["trial_network"][entity_name]["debug"]
            del tn_deployed_descriptor["trial_network"][entity_name]["debug"]
            trial_network.tn_raw_descriptor = trial_network.descriptor_to_json(tn_raw_descriptor)
            trial_network.tn_sorted_descriptor = trial_network.descriptor_to_json(tn_sorted_descriptor)
            trial_network.tn_deployed_descriptor = trial_network.descriptor_to_json(tn_deployed_descriptor)
            trial_network.save()
            return {"message": f"Successfully deleted debug into '{entity_name}' entity name of the Trial Network '{tn_id}'"}, 201
        except ValidationError as e:
            return abort(401, e.message)
        except MongoEngineException as e:
            return abort(401, str(e))
        except CustomException as e:
            return abort(e.error_code, str(e))

@debug_namespace.route("/jenkins/pipelines/")
class JenkinsPipelines(Resource):

    @debug_namespace.doc(security="Bearer Auth")
    @jwt_required()
    def get(self) -> tuple[dict, int]:
        """
        Return pipelines stored in Jenkins
        """
        try:
            jenkins_handler = JenkinsHandler()
            return {"all_pipelines": jenkins_handler.get_all_pipelines()}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))