import os

from shutil import rmtree
from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.datastructures import FileStorage
from threading import Lock
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError

from conf import TnlcmSettings, SixGLibrarySettings, SixGSandboxSitesSettings
from core.auth.auth import get_current_user_from_jwt
from core.jenkins.jenkins_handler import JenkinsHandler
from core.logs.log_handler import log_handler
from core.models import TrialNetworkModel, ResourceManagerModel
from core.sixg_library.sixg_library_handler import SixGLibraryHandler
from core.sixg_sandbox_sites.sixg_sandbox_sites_handler import SixGSandboxSitesHandler
from core.exceptions.exceptions_handler import CustomException

trial_network_namespace = Namespace(
    name="trial-network",
    description="Namespace for trial network status and management",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        }
    }
)

#########################################
############ Mutual exclusion ###########
#########################################
tn_id_lock = Lock()
tn_resource_manager_lock = Lock()

#########################################
############# Trial Network #############
#########################################
@trial_network_namespace.route("")
class CreateTrialNetwork(Resource):

    parser_post = reqparse.RequestParser()
    parser_post.add_argument("tn_id", type=str, required=False)
    parser_post.add_argument("descriptor", location="files", type=FileStorage, required=True)
    parser_post.add_argument("deployment_site", type=str, required=True)
    parser_post.add_argument("github_6g_library_https_url", type=str, required=True, default=SixGLibrarySettings.GITHUB_6G_LIBRARY_HTTPS_URL)
    parser_post.add_argument("github_6g_library_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_post.add_argument("github_6g_library_reference_value", type=str, required=True)
    parser_post.add_argument("github_6g_sandbox_sites_https_url", type=str, required=True, default=SixGSandboxSitesSettings.GITHUB_6G_SANDBOX_SITES_HTTPS_URL)
    parser_post.add_argument("github_6g_sandbox_sites_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_post.add_argument("github_6g_sandbox_sites_reference_value", type=str, required=True)

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @trial_network_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Create and validate trial network
        Can specify a branch, commit or tag of the 6G-Library
        Can specify a branch, commit or tag of the 6G-Sandbox-Sites
        The tn_id can be specified if desired. **If the value is specified, it should begin with character. If nothing is specified, it will return a random tn_id**
        """
        try:
            tn_id = self.parser_post.parse_args()["tn_id"]
            descriptor_file = self.parser_post.parse_args()["descriptor"]
            deployment_site = self.parser_post.parse_args()["deployment_site"]
            github_6g_library_https_url = self.parser_post.parse_args()["github_6g_library_https_url"]
            github_6g_library_reference_type = self.parser_post.parse_args()["github_6g_library_reference_type"]
            github_6g_library_reference_value = self.parser_post.parse_args()["github_6g_library_reference_value"]
            github_6g_sandbox_sites_https_url = self.parser_post.parse_args()["github_6g_sandbox_sites_https_url"]
            github_6g_sandbox_sites_reference_type = self.parser_post.parse_args()["github_6g_sandbox_sites_reference_type"]
            github_6g_sandbox_sites_reference_value = self.parser_post.parse_args()["github_6g_sandbox_sites_reference_value"]

            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel()
            if tn_id and trial_network.verify_tn_id(tn_id):
                return {"message": f"Trial network with tn_id '{tn_id}' already exists in database"}, 409
            trial_network.set_user_created(user_created=current_user.username)
            with tn_id_lock:
                trial_network.set_tn_id(size=3, tn_id=tn_id)
                log_handler.info(f"Trial network created with identifier '{trial_network.tn_id}'")
            directory_path = os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, f"{trial_network.tn_id}")
            trial_network.set_directory_path(directory_path=directory_path)
            log_handler.info(f"[{trial_network.tn_id}] - Create directory '{trial_network.tn_id}' in the path '{trial_network.directory_path}' to store the directories and files generated by the trial network")
            trial_network.set_raw_descriptor(file=descriptor_file)
            log_handler.info(f"[{trial_network.tn_id}] - Trial network descriptor raw saved")
            log_handler.info(f"[{trial_network.tn_id}] - Apply the sorting algorithm according to the dependencies of the components specified in the trial network descriptor")
            trial_network.set_sorted_descriptor()
            log_handler.info(f"[{trial_network.tn_id}] - Trial network descriptor sorted")
            sixg_sandbox_sites_handler = SixGSandboxSitesHandler(https_url=github_6g_sandbox_sites_https_url, reference_type=github_6g_sandbox_sites_reference_type, reference_value=github_6g_sandbox_sites_reference_value, directory_path=directory_path)
            sixg_sandbox_sites_handler.git_clone()
            log_handler.info(f"[{trial_network.tn_id}] - Git clone '{sixg_sandbox_sites_handler.github_6g_sandbox_sites_repository_name}' repository into '{trial_network.directory_path}'")
            sixg_sandbox_sites_handler.git_checkout()
            log_handler.info(f"[{trial_network.tn_id}] - Git checkout '{sixg_sandbox_sites_handler.github_6g_sandbox_sites_repository_name}' repository into '{trial_network.directory_path}' to '{sixg_sandbox_sites_handler.github_6g_sandbox_sites_reference_type}' with value '{sixg_sandbox_sites_handler.github_6g_sandbox_sites_reference_value}'")
            sixg_sandbox_sites_handler.git_switch()
            log_handler.info(f"[{trial_network.tn_id}] - Git switch '{sixg_sandbox_sites_handler.github_6g_sandbox_sites_repository_name}' repository into '{trial_network.directory_path}' with HEAD pointing to commit '{sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id}'")
            log_handler.info(f"[{trial_network.tn_id}] - Validate deployment site '{deployment_site}'")
            sixg_sandbox_sites_handler.validate_site(deployment_site)
            trial_network.set_deployment_site(deployment_site)
            log_handler.info(f"[{trial_network.tn_id}] - Deployment site '{trial_network.deployment_site}' is valid")
            tn_components_types = trial_network.get_components_types()
            log_handler.info(f"[{trial_network.tn_id}] - Validate if the components that make up the descriptor are available on the deployment site '{trial_network.deployment_site}'")
            sixg_sandbox_sites_handler.validate_components_site(tn_id=trial_network.tn_id, deployment_site=trial_network.deployment_site, tn_components_types=tn_components_types)
            log_handler.info(f"[{trial_network.tn_id}] - Descriptor components are available on the deployment site '{trial_network.deployment_site}'")
            sixg_library_handler = SixGLibraryHandler(https_url=github_6g_library_https_url, reference_type=github_6g_library_reference_type, reference_value=github_6g_library_reference_value, directory_path=directory_path)
            sixg_library_handler.git_clone()
            log_handler.info(f"[{trial_network.tn_id}] - Git clone '{sixg_library_handler.github_6g_library_repository_name}' repository into '{trial_network.directory_path}'")
            sixg_library_handler.git_checkout()
            log_handler.info(f"[{trial_network.tn_id}] - Git checkout '{sixg_library_handler.github_6g_library_repository_name}' repository into '{trial_network.directory_path}' to '{sixg_library_handler.github_6g_library_reference_type}' with value '{sixg_library_handler.github_6g_library_reference_value}'")
            sixg_library_handler.git_switch()
            log_handler.info(f"[{trial_network.tn_id}] - Git switch '{sixg_library_handler.github_6g_library_repository_name}' repository into '{trial_network.directory_path}' with HEAD pointing to commit '{sixg_library_handler.github_6g_library_commit_id}'")
            tn_component_inputs = sixg_library_handler.get_tn_components_parts(parts=["input"], tn_components_types=tn_components_types)["input"]
            log_handler.info(f"[{trial_network.tn_id}] - Validate trial network descriptor")
            trial_network.validate_descriptor(tn_components_types, tn_component_inputs)
            log_handler.info(f"[{trial_network.tn_id}] - Trial network descriptor valid")
            trial_network.set_github_6g_sandbox_sites_https_url(sixg_sandbox_sites_handler.github_6g_sandbox_sites_https_url)
            trial_network.set_github_6g_sandbox_sites_commit_id(sixg_sandbox_sites_handler.github_6g_sandbox_sites_commit_id)
            trial_network.set_github_6g_library_https_url(sixg_library_handler.github_6g_library_https_url)
            trial_network.set_github_6g_library_commit_id(sixg_library_handler.github_6g_library_commit_id)
            trial_network.set_state("validated")
            trial_network.save()
            log_handler.info(f"[{trial_network.tn_id}] - Trial network update to status '{trial_network.state}'")
            return trial_network.to_dict(), 201
        except CustomException as e:
            if trial_network.directory_path:
                rmtree(trial_network.directory_path)
            return {"message": str(e)}, e.error_code
        except Exception as e:
            if trial_network.directory_path:
                rmtree(trial_network.directory_path)
            log_handler.error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))

@trial_network_namespace.route("/<string:tn_id>")
class TrialNetwork(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id: str) -> tuple[dict, int]:
        """
        Get trial network
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            
            if not trial_network:
                return {"message": f"No trial network with the name '{tn_id}' created by the user '{current_user.username}'"}, 404

            return trial_network.to_dict_full(), 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            log_handler.error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))
    
    parser_put = reqparse.RequestParser()
    parser_put.add_argument("jenkins_deploy_pipeline", type=str, required=False)

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @trial_network_namespace.expect(parser_put)
    def put(self, tn_id: str) -> tuple[dict, int]:
        """
        Activate or suspend trial network
        If nothing is specified in *jenkins_deploy_pipeline*, a pipeline will be created inside TNLCM folder in Jenkins with the name **TN_DEPLOY_<tn_id>**
        If a deployment pipeline is specified, it will be checked that it exists in Jenkins and that it has nothing queued to execute
        """
        try:
            jenkins_deploy_pipeline = self.parser_put.parse_args()["jenkins_deploy_pipeline"]

            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            
            if not trial_network:
                return {"message": f"No trial network with the name '{tn_id}' created by the user '{current_user.username}'"}, 404

            state = trial_network.state
            if state == "validated":
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                jenkins_deploy_pipeline = jenkins_handler.generate_jenkins_deploy_pipeline(jenkins_deploy_pipeline)
                trial_network.set_jenkins_deploy_pipeline(jenkins_deploy_pipeline)
                trial_network.save()
                sixg_sandbox_sites_handler = SixGSandboxSitesHandler(https_url=trial_network.github_6g_sandbox_sites_https_url, reference_type="commit", reference_value=trial_network.github_6g_sandbox_sites_commit_id, directory_path=trial_network.directory_path)
                site_available_components = sixg_sandbox_sites_handler.get_site_available_components(deployment_site=trial_network.deployment_site)
                log_handler.info(f"[{trial_network.tn_id}] - Apply resource manager")
                resource_manager = ResourceManagerModel()
                with tn_resource_manager_lock:
                    resource_manager.apply_resource_manager(trial_network, site_available_components)
                    log_handler.info(f"[{trial_network.tn_id}] - Resource manager is applied")
                log_handler.info(f"[{trial_network.tn_id}] - Start deployment of the trial network using Jenkins")
                jenkins_handler.trial_network_deployment()
                log_handler.info(f"[{trial_network.tn_id}] - End deployment of the trial network using Jenkins")
                report_path = os.path.join(f"{trial_network.directory_path}", f"{trial_network.tn_id}.md")
                trial_network.set_report(report_path)
                trial_network.set_state("activated")
                trial_network.save()
                log_handler.info(f"[{trial_network.tn_id}] - Trial network update to status '{trial_network.state}'")
                return {"message": f"Trial network ACTIVATED. Report of the trial network can be found in the directory '{report_path}'"}, 200
            elif state == "failed":
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                deployed_descriptor = trial_network.deployed_descriptor["trial_network"]
                first_key = next(iter(deployed_descriptor))
                log_handler.info(f"[{trial_network.tn_id}] - Deployment of the trial network continues in the entity_name '{first_key}'")
                jenkins_handler.trial_network_deployment()
                log_handler.info(f"[{trial_network.tn_id}] - End deployment of the trial network using Jenkins")
                report_path = os.path.join(f"{trial_network.directory_path}", f"{trial_network.tn_id}.md")
                trial_network.set_report(report_path)
                trial_network.set_state("activated")
                trial_network.save()
                log_handler.info(f"[{trial_network.tn_id}] - Trial network update to status '{trial_network.state}'")
                return {"message": f"Trial network ACTIVATED. Report of the trial network can be found in the directory '{report_path}'"}, 200
            elif state == "destroyed":
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                sixg_sandbox_sites_handler = SixGSandboxSitesHandler(https_url=trial_network.github_6g_sandbox_sites_https_url, reference_type="commit", reference_value=trial_network.github_6g_sandbox_sites_commit_id, directory_path=trial_network.directory_path)
                site_available_components = sixg_sandbox_sites_handler.get_site_available_components(deployment_site=trial_network.deployment_site)
                log_handler.info(f"[{trial_network.tn_id}] - Apply resource manager")
                resource_manager = ResourceManagerModel()
                with tn_resource_manager_lock:
                    resource_manager.apply_resource_manager(trial_network, site_available_components)
                    log_handler.info(f"[{trial_network.tn_id}] - Resource manager is applied")
                log_handler.info(f"[{trial_network.tn_id}] - Start again deployment of the trial network using Jenkins")
                jenkins_handler.trial_network_deployment()
                log_handler.info(f"[{trial_network.tn_id}] - End deployment of the trial network using Jenkins")
                report_path = os.path.join(f"{trial_network.directory_path}", f"{trial_network.tn_id}.md")
                trial_network.set_report(report_path)
                trial_network.set_state("activated")
                trial_network.save()
                log_handler.info(f"[{trial_network.tn_id}] - Trial network update to status '{trial_network.state}'")
                return {"message": f"Trial network RE-ACTIVATED. Report of the trial network can be found in the directory '{report_path}'"}, 200
            elif state == "activated":
                # TODO: see what to do with trial network resources
                return {"message": "TODO: SUSPEND trial network"}, 400
            else: # state == "suspended"
                # TODO:
                return {"message": "TODO: RESTART trial network suspended"}, 400
        except CustomException as e:
            trial_network.set_state("failed")
            trial_network.save()
            return {"message": str(e)}, e.error_code
        except Exception as e:
            trial_network.set_state("failed")
            trial_network.save()
            log_handler.error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))

    parser_delete = reqparse.RequestParser()
    parser_delete.add_argument("jenkins_destroy_pipeline", type=str, required=False)

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @trial_network_namespace.expect(parser_delete)
    def delete(self, tn_id: str) -> tuple[dict, int]:
        """
        Destroy trial network
        If nothing is specified in *jenkins_destroy_pipeline*, a pipeline will be created inside TNLCM folder in Jenkins with the name **TN_DESTROY_<tn_id>**
        If a destroy pipeline is specified, it will be checked that it exists in Jenkins and that it has nothing queued to execute
        """
        try:
            jenkins_destroy_pipeline = self.parser_delete.parse_args()["jenkins_destroy_pipeline"]

            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            
            if not trial_network:
                return {"message": f"No trial network with the name '{tn_id}' created by the user '{current_user.username}'"}, 404
            
            if trial_network.state != "activated" and trial_network.state != "failed":
                return {"message": "Trial network cannot be destroyed because the current status of Trial Network is different to ACTIVATED or FAILED"}, 400
            
            sixg_library_handler = SixGLibraryHandler(https_url=trial_network.github_6g_library_https_url, reference_type="commit", reference_value=trial_network.github_6g_library_commit_id, directory_path=trial_network.directory_path)
            jenkins_handler = JenkinsHandler(trial_network=trial_network, sixg_library_handler=sixg_library_handler)
            jenkins_destroy_pipeline = jenkins_handler.generate_jenkins_destroy_pipeline(jenkins_destroy_pipeline=jenkins_destroy_pipeline)
            trial_network.set_jenkins_destroy_pipeline(jenkins_destroy_pipeline)
            trial_network.save()
            log_handler.info(f"[{trial_network.tn_id}] - Pipeline for destroy trial network '{trial_network.jenkins_destroy_pipeline}' is valid")
            log_handler.info(f"[{trial_network.tn_id}] - Start destroy of the trial network using Jenkins")
            jenkins_handler.trial_network_destroy(jenkins_destroy_pipeline=trial_network.jenkins_destroy_pipeline)
            log_handler.info(f"[{trial_network.tn_id}] - End destroy of the trial network using Jenkins")
            log_handler.info(f"[{trial_network.tn_id}] - Apply release resource manager")
            resource_manager = ResourceManagerModel()
            with tn_resource_manager_lock:
                resource_manager.release_resource_manager(trial_network)
                log_handler.info(f"[{trial_network.tn_id}] - Release resource manager is applied")
            trial_network.set_deployed_descriptor()
            trial_network.set_state("destroyed")
            trial_network.save()
            log_handler.info(f"[{trial_network.tn_id}] - Trial network update to status '{trial_network.state}'")
            return {"message": f"The trial network with identifier '{tn_id}' has been DESTROYED"}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            log_handler.error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))

@trial_network_namespace.route("/purge/<string:tn_id>")
class PurgeTrialNetwork(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def delete(self, tn_id: str) -> tuple[dict, int]:
        """
        Purge trial network
        """
        try:          
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            
            if not trial_network:
                return {"message": f"No trial network with the name '{tn_id}' created by the user '{current_user.username}'"}, 404
            
            if trial_network.state != "validated" and trial_network.state != "destroyed":
                return {"message": "Trial network cannot be purge because the current status of Trial Network is different to VALIDATED and DESTROYED"}, 400
            
            if trial_network.state == "destroyed":
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                jenkins_handler.delete_pipeline(trial_network.jenkins_deploy_pipeline)
                jenkins_handler.delete_pipeline(trial_network.jenkins_destroy_pipeline)
            rmtree(trial_network.directory_path)
            log_handler.info(f"[{trial_network.tn_id}] - Deleted trial network directory '{trial_network.directory_path}'")
            log_handler.info(f"[{trial_network.tn_id}] - Trial network update to state 'purge'")
            trial_network.delete()
            return {"message": f"The trial network with identifier '{tn_id}' has been PURGE"}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            log_handler.error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))

@trial_network_namespace.route("/report/<string:tn_id>")
class ReportTrialNetwork(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id: str) -> tuple[dict, int]:
        """
        Report generated after trial network deployment
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            
            if not trial_network:
                return {"message": f"No trial network with the name '{tn_id}' created by the user '{current_user.username}'"}, 404

            return {"report": trial_network.report}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            log_handler.error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))