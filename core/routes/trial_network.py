import os

from shutil import rmtree
from flask import send_file
from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.datastructures import FileStorage
from threading import Lock
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError

from conf.tnlcm import TnlcmSettings
from conf.library import LibrarySettings
from conf.sites import SitesSettings
from conf.flask_conf import FlaskConf
from core.utils.file_handler import load_file
from core.auth.auth import get_current_user_from_jwt
from core.jenkins.jenkins_handler import JenkinsHandler
from core.logs.log_handler import TnLogHandler
from core.models import TrialNetworkModel, ResourceManagerModel
from core.library.library_handler import LibraryHandler
from core.sites.sites_handler import SitesHandler
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
    if FlaskConf.FLASK_ENV == "development":
        parser_post.add_argument("library_https_url", type=str, required=True, default=LibrarySettings.LIBRARY_HTTPS_URL)
    parser_post.add_argument("library_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_post.add_argument("library_reference_value", type=str, required=True)
    if FlaskConf.FLASK_ENV == "development":
        parser_post.add_argument("sites_https_url", type=str, required=True, default=SitesSettings.SITES_HTTPS_URL)
    parser_post.add_argument("sites_reference_type", type=str, required=True, choices=("branch", "commit", "tag"))
    parser_post.add_argument("sites_reference_value", type=str, required=True)

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @trial_network_namespace.expect(parser_post)
    def post(self) -> tuple[dict, int]:
        """
        Create and validate trial network
        Can specify a branch, commit or tag of the Library
        Can specify a branch, commit or tag of the Sites
        The tn_id can be specified if desired. **If the value is specified, it should begin with character. If nothing is specified, it will return a random tn_id**
        """
        tn_log_handler = None
        trial_network = TrialNetworkModel()
        try:
            tn_id = self.parser_post.parse_args()["tn_id"]
            descriptor_file = self.parser_post.parse_args()["descriptor"]
            deployment_site = self.parser_post.parse_args()["deployment_site"]
            library_https_url = None
            if FlaskConf.FLASK_ENV == "development":
                library_https_url = self.parser_post.parse_args()["library_https_url"]
            library_reference_type = self.parser_post.parse_args()["library_reference_type"]
            library_reference_value = self.parser_post.parse_args()["library_reference_value"]
            sites_https_url = None
            if FlaskConf.FLASK_ENV == "development":
                sites_https_url = self.parser_post.parse_args()["sites_https_url"]
            sites_reference_type = self.parser_post.parse_args()["sites_reference_type"]
            sites_reference_value = self.parser_post.parse_args()["sites_reference_value"]

            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network.set_user_created(user_created=current_user.username)
            with tn_id_lock:
                trial_network.set_tn_id(size=3, tn_id=tn_id)
            trial_network.set_directory_path(directory_path=os.path.join(TnlcmSettings.TRIAL_NETWORKS_DIRECTORY, trial_network.tn_id))
            tn_log_handler = TnLogHandler(tn_id=trial_network.tn_id)
            tn_log_handler.info(f"[{trial_network.tn_id}] - Create directory {trial_network.tn_id} in the path {trial_network.directory_path} to store the directories and files generated by the trial network")
            trial_network.set_raw_descriptor(file=descriptor_file)
            sites_handler = SitesHandler(https_url=sites_https_url, reference_type=sites_reference_type, reference_value=sites_reference_value, directory_path=trial_network.directory_path)
            sites_handler.git_clone()
            tn_log_handler.info(f"[{trial_network.tn_id}] - Git clone {sites_handler.sites_repository_name} repository into {trial_network.directory_path}")
            sites_handler.git_checkout()
            tn_log_handler.info(f"[{trial_network.tn_id}] - Git checkout {sites_handler.sites_repository_name} repository into {trial_network.directory_path} to {sites_handler.sites_reference_type} with value {sites_handler.sites_reference_value}")
            sites_handler.git_switch()
            tn_log_handler.info(f"[{trial_network.tn_id}] - Git switch {sites_handler.sites_repository_name} repository into {trial_network.directory_path} with HEAD pointing to commit {sites_handler.sites_commit_id}")
            trial_network.set_sites_https_url(sites_handler.sites_https_url)
            trial_network.set_sites_commit_id(sites_handler.sites_commit_id)
            tn_log_handler.info(f"[{trial_network.tn_id}] - Validate deployment site {deployment_site}")
            sites_handler.validate_site(deployment_site)
            trial_network.set_deployment_site(deployment_site)
            tn_log_handler.info(f"[{trial_network.tn_id}] - Deployment site {trial_network.deployment_site} is valid")
            library_handler = LibraryHandler(https_url=library_https_url, reference_type=library_reference_type, reference_value=library_reference_value, directory_path=trial_network.directory_path)
            library_handler.git_clone()
            tn_log_handler.info(f"[{trial_network.tn_id}] - Git clone {library_handler.library_repository_name} repository into {trial_network.directory_path}")
            library_handler.git_checkout()
            tn_log_handler.info(f"[{trial_network.tn_id}] - Git checkout {library_handler.library_repository_name} repository into {trial_network.directory_path} to {library_handler.library_reference_type} with value {library_handler.library_reference_value}")
            library_handler.git_switch()
            tn_log_handler.info(f"[{trial_network.tn_id}] - Git switch {library_handler.library_repository_name} repository into {trial_network.directory_path} with HEAD pointing to commit {library_handler.library_commit_id}")
            trial_network.set_library_https_url(library_handler.library_https_url)
            trial_network.set_library_commit_id(library_handler.library_commit_id)
            tn_log_handler.info(f"[{trial_network.tn_id}] - Validate trial network descriptor")
            trial_network.validate_descriptor(library_handler, sites_handler)
            tn_log_handler.info(f"[{trial_network.tn_id}] - Trial network descriptor valid")
            trial_network.set_sorted_descriptor()
            trial_network.set_state("validated")
            trial_network.save()
            tn_log_handler.info(f"[{trial_network.tn_id}] - Trial network update to status {trial_network.state}")
            return trial_network.to_dict(), 201
        except CustomException as e:
            if trial_network and trial_network.directory_path:
                rmtree(trial_network.directory_path)
            return {"message": str(e)}, e.error_code
        except Exception as e:
            if trial_network and trial_network.directory_path:
                rmtree(trial_network.directory_path)
            if tn_log_handler:
                tn_log_handler.error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))

@trial_network_namespace.route("/<string:tn_id>")
class TrialNetwork(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id: str) -> tuple[dict, int]:
        """
        Retrieve trial network
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            
            if not trial_network:
                return {"message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"}, 404

            return trial_network.to_dict_full(), 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).error(f"[{trial_network.tn_id}] - {e}")
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
        If a deployment pipeline is specified, it will be checked if it exists in Jenkins and if it has nothing queued to execute
        """
        try:
            jenkins_deploy_pipeline = self.parser_put.parse_args()["jenkins_deploy_pipeline"]

            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            
            if not trial_network:
                return {"message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"}, 404

            state = trial_network.state
            if state == "validated":
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                jenkins_deploy_pipeline = jenkins_handler.generate_jenkins_deploy_pipeline(jenkins_deploy_pipeline)
                trial_network.set_jenkins_deploy_pipeline(jenkins_deploy_pipeline)
                trial_network.save()
                sites_handler = SitesHandler(https_url=trial_network.sites_https_url, reference_type="commit", reference_value=trial_network.sites_commit_id, directory_path=trial_network.directory_path)
                site_available_components = sites_handler.get_site_available_components(deployment_site=trial_network.deployment_site)
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Apply resource manager")
                resource_manager = ResourceManagerModel()
                with tn_resource_manager_lock:
                    resource_manager.apply_resource_manager(trial_network, site_available_components)
                    TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Resource manager is applied")
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Start deployment of the trial network using Jenkins")
                jenkins_handler.trial_network_deployment()
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - End deployment of the trial network using Jenkins")
                report_path = os.path.join(trial_network.directory_path, f"{trial_network.tn_id}.md")
                trial_network.set_report(report_path)
                trial_network.set_state("activated")
                trial_network.save()
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Trial network update to status {trial_network.state}")
                return {"message": f"Trial network ACTIVATED. Report of the trial network can be found in the directory {report_path}"}, 200
            elif state == "failed":
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                deployed_descriptor = trial_network.deployed_descriptor["trial_network"]
                first_key = next(iter(deployed_descriptor))
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Deployment of the trial network continues in the entity_name {first_key}")
                jenkins_handler.trial_network_deployment()
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - End deployment of the trial network using Jenkins")
                report_path = os.path.join(trial_network.directory_path, f"{trial_network.tn_id}.md")
                trial_network.set_report(report_path)
                trial_network.set_state("activated")
                trial_network.save()
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Trial network update to status {trial_network.state}")
                return {"message": f"Trial network ACTIVATED. Report of the trial network can be found in the directory {report_path}"}, 200
            elif state == "destroyed":
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                sites_handler = SitesHandler(https_url=trial_network.sites_https_url, reference_type="commit", reference_value=trial_network.sites_commit_id, directory_path=trial_network.directory_path)
                site_available_components = sites_handler.get_site_available_components(deployment_site=trial_network.deployment_site)
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Apply resource manager")
                resource_manager = ResourceManagerModel()
                with tn_resource_manager_lock:
                    resource_manager.apply_resource_manager(trial_network, site_available_components)
                    TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Resource manager is applied")
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Start again deployment of the trial network using Jenkins")
                jenkins_handler.trial_network_deployment()
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - End deployment of the trial network using Jenkins")
                report_path = os.path.join(trial_network.directory_path, f"{trial_network.tn_id}.md")
                trial_network.set_report(report_path)
                trial_network.set_state("activated")
                trial_network.save()
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Trial network update to status {trial_network.state}")
                return {"message": f"Trial network RE-ACTIVATED. Report of the trial network can be found in the directory {report_path}"}, 200
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
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).error(f"[{trial_network.tn_id}] - {e}")
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
                return {"message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"}, 404
            
            if trial_network.state != "activated" and trial_network.state != "failed":
                return {"message": "Trial network cannot be destroyed because the current status of Trial Network is different to ACTIVATED or FAILED"}, 400
            
            library_handler = LibraryHandler(https_url=trial_network.library_https_url, reference_type="commit", reference_value=trial_network.library_commit_id, directory_path=trial_network.directory_path)
            jenkins_handler = JenkinsHandler(trial_network=trial_network, library_handler=library_handler)
            jenkins_destroy_pipeline = jenkins_handler.generate_jenkins_destroy_pipeline(jenkins_destroy_pipeline=jenkins_destroy_pipeline)
            trial_network.set_jenkins_destroy_pipeline(jenkins_destroy_pipeline)
            trial_network.save()
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Pipeline for destroy trial network {trial_network.jenkins_destroy_pipeline} is valid")
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Start destroy of the trial network using Jenkins")
            jenkins_handler.trial_network_destroy(jenkins_destroy_pipeline=trial_network.jenkins_destroy_pipeline)
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - End destroy of the trial network using Jenkins")
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Apply release resource manager")
            resource_manager = ResourceManagerModel()
            with tn_resource_manager_lock:
                resource_manager.release_resource_manager(trial_network)
                TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Release resource manager is applied")
            trial_network.set_deployed_descriptor()
            trial_network.set_state("destroyed")
            trial_network.save()
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Trial network update to status {trial_network.state}")
            return {"message": f"The trial network with identifier {tn_id} has been DESTROYED"}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).error(f"[{trial_network.tn_id}] - {e}")
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
                return {"message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"}, 404
            
            if trial_network.state != "validated" and trial_network.state != "destroyed":
                return {"message": "Trial network cannot be purge because the current status of Trial Network is different to VALIDATED and DESTROYED"}, 400
            
            if trial_network.state == "destroyed":
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                jenkins_handler.remove_pipeline(trial_network.jenkins_deploy_pipeline)
                jenkins_handler.remove_pipeline(trial_network.jenkins_destroy_pipeline)
            rmtree(trial_network.directory_path)
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Deleted trial network directory {trial_network.directory_path}")
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).info(f"[{trial_network.tn_id}] - Trial network purge")
            trial_network.delete()
            return {"message": f"The trial network with identifier {tn_id} has been PURGE"}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            TnLogHandler.get_logger(tn_id=trial_network.tn_id).error(f"[{trial_network.tn_id}] - {e}")
            return abort(500, str(e))

@trial_network_namespace.route("s/<string:tn_id>.md")
class DownloadReportTrialNetwork(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id: str):
        """
        Download report generated after trial network deployment
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            
            if not trial_network:
                return {"message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"}, 404

            if trial_network.state != "activated":
                return {"message": "Trial network report can only be downloaded when the status of the trial network is ACTIVATED"}, 400
            
            if trial_network.report == "":
                return {"message": "Trial network report is empty"}, 404
            
            file_name = f"{trial_network.tn_id}.md"
            report_path_md = os.path.join(trial_network.directory_path, file_name)

            if not os.path.exists(report_path_md):
                return {"message": f"Report file {file_name} not found in {report_path_md}"}, 404
            
            return send_file(
                report_path_md,
                as_attachment=True,
                download_name=file_name,
                mimetype="application/octet-stream"
            )
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))

@trial_network_namespace.route("s/<string:tn_id>.log")
class TrialNetworkLog(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id):
        """
        Retrieve trial network log
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_network = TrialNetworkModel.objects(user_created=current_user.username, tn_id=tn_id).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            
            if not trial_network:
                return {"message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"}, 404

            log_path = os.path.join(trial_network.directory_path, f"{tn_id}.log")

            if not os.path.exists(log_path):
                return {"message": f"Trial network log file with identifier {tn_id} not found"}, 404
            
            log_content = load_file(file_path=log_path)
            return {"log": log_content}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:          
            return abort(500, str(e))

@trial_network_namespace.route("s")
class TrialNetwors(Resource):

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self):
        """
        Retrieve all trial networks
        """
        try:
            current_user = get_current_user_from_jwt(get_jwt_identity())
            trial_networks = TrialNetworkModel.objects(user_created=current_user.username)
            if current_user.role == "admin":
                trial_networks = TrialNetworkModel.objects()
            return {"trial_networks": [trial_network.to_dict() for trial_network in trial_networks]}, 200
        except CustomException as e:
            return {"message": str(e)}, e.error_code
        except Exception as e:
            return abort(500, str(e))