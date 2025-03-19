from threading import Lock

from flask import send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Namespace, Resource, abort, reqparse
from jwt.exceptions import PyJWTError
from werkzeug.datastructures import FileStorage

from conf.jenkins import JenkinsSettings
from conf.sites import SitesSettings
from core.auth.auth import get_current_user_from_jwt
from core.exceptions.exceptions_handler import CustomException
from core.jenkins.jenkins_handler import JenkinsHandler
from core.library.library_handler import LIBRARY_REFERENCES_TYPES, LibraryHandler
from core.logs.log_handler import TrialNetworkLogger
from core.models.resource_manager import ResourceManagerModel
from core.models.trial_network import TrialNetworkModel
from core.sites.sites_handler import SitesHandler
from core.utils.file import load_file
from core.utils.os import (
    TRIAL_NETWORKS_DIRECTORY_PATH,
    exist_directory,
    is_file,
    join_path,
    remove_directory,
)
from core.utils.parser import ansible_decrypt

trial_network_namespace = Namespace(
    name="trial-network",
    description="Namespace for trial network status and management",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
        }
    },
)

tn_id_lock = Lock()
tn_resource_manager_lock = Lock()


@trial_network_namespace.route("")
class CreateValidateTrialNetwork(Resource):
    parser_post = reqparse.RequestParser()
    parser_post.add_argument(
        "tn_id",
        type=str,
        required=False,
        location="form",
        help="Trial network identifier. It is optional. If not specified, a random will be generated. If specified, it should begin with character and max length 15",
    )
    parser_post.add_argument(
        "descriptor",
        location="files",
        type=FileStorage,
        required=True,
        help="Trial network descriptor file",
    )
    parser_post.add_argument(
        "library_reference_type",
        type=str,
        required=True,
        location="form",
        choices=LIBRARY_REFERENCES_TYPES,
        help="Type of the Library reference",
    )
    parser_post.add_argument(
        "library_reference_value",
        type=str,
        required=True,
        location="form",
        help="Value of the Library reference type",
    )
    parser_post.add_argument(
        "sites_branch",
        type=str,
        required=False,
        location="form",
        help="Branch of the Sites repository",
    )
    parser_post.add_argument(
        "deployment_site",
        type=str,
        required=False,
        location="form",
        help="Directory inside the branch of the Sites repository",
    )
    parser_post.add_argument(
        "validate",
        type=str,
        required=True,
        location="args",
        choices=["True", "False"],
        help="If true, the trial network will be validated",
    )

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @trial_network_namespace.expect(parser_post)
    def post(self):
        """
        Create or validate trial network

        - If `validate=True`: **all parameters are required**.
        - If `validate=False`: `descriptor`, `library_reference_type` and `library_reference_value` are required, `tn_id` is optional.
        """
        trial_network = None
        try:
            tn_id = self.parser_post.parse_args()["tn_id"]
            descriptor_file = self.parser_post.parse_args()["descriptor"]
            library_reference_type = self.parser_post.parse_args()[
                "library_reference_type"
            ]
            library_reference_value = self.parser_post.parse_args()[
                "library_reference_value"
            ]
            sites_branch = self.parser_post.parse_args()["sites_branch"]
            deployment_site = self.parser_post.parse_args()["deployment_site"]
            validate = self.parser_post.parse_args()["validate"]

            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            if validate == "False":
                if tn_id:
                    trial_network = TrialNetworkModel.objects(
                        user_created=current_user.username, tn_id=tn_id
                    ).first()
                    if trial_network:
                        if trial_network.user_created != current_user.username:
                            return {
                                "message": f"Trial network with identifier {trial_network.tn_id} was not created by the user {current_user.username}"
                            }, 400
                        library_handler = LibraryHandler(
                            reference_type="branch",
                            reference_value="main",
                            directory_path=trial_network.directory_path,
                        )
                        library_handler.repository_handler.git_clone()
                        library_handler.repository_handler.git_checkout()
                        library_handler.repository_handler.git_pull()
                    else:
                        trial_network = TrialNetworkModel()
                        trial_network.set_user_created(
                            user_created=current_user.username
                        )
                        with tn_id_lock:
                            trial_network.set_tn_id(size=3, tn_id=tn_id)
                        trial_network.set_directory_path(
                            directory_path=join_path(
                                TRIAL_NETWORKS_DIRECTORY_PATH, trial_network.tn_id
                            )
                        )
                else:
                    trial_network = TrialNetworkModel()
                    trial_network.set_user_created(user_created=current_user.username)
                    with tn_id_lock:
                        trial_network.set_tn_id(size=3, tn_id=tn_id)
                    trial_network.set_directory_path(
                        directory_path=join_path(
                            TRIAL_NETWORKS_DIRECTORY_PATH, trial_network.tn_id
                        )
                    )
                library_handler = LibraryHandler(
                    reference_type=library_reference_type,
                    reference_value=library_reference_value,
                    directory_path=trial_network.directory_path,
                )
                library_handler.repository_handler.git_clone()
                library_handler.repository_handler.git_checkout()
                trial_network.set_library_https_url(
                    library_https_url=library_handler.library_https_url
                )
                trial_network.set_library_commit_id(
                    library_commit_id=library_handler.repository_handler.git_last_commit_id()
                )
                trial_network.set_raw_descriptor(file=descriptor_file)
                trial_network.set_state(state="created")
                trial_network.save()
                TrialNetworkLogger(tn_id=tn_id).info(
                    message="Trial network created. In this state, the trial network has not been validated and cannot be deployed"
                )
                return trial_network.to_dict_created(), 201
            else:
                if tn_id:
                    trial_network = TrialNetworkModel.objects(
                        user_created=current_user.username, tn_id=tn_id
                    ).first()
                    if trial_network:
                        if trial_network.user_created != current_user.username:
                            return {
                                "message": f"Trial network with identifier {trial_network.tn_id} was not created by the user {current_user.username}"
                            }, 400
                        library_handler = LibraryHandler(
                            reference_type="branch",
                            reference_value="main",
                            directory_path=trial_network.directory_path,
                        )
                        library_handler.repository_handler.git_clone()
                        library_handler.repository_handler.git_checkout()
                        library_handler.repository_handler.git_pull()
                    else:
                        trial_network = TrialNetworkModel()
                        trial_network.set_user_created(
                            user_created=current_user.username
                        )
                        with tn_id_lock:
                            trial_network.set_tn_id(size=3, tn_id=tn_id)
                        trial_network.set_directory_path(
                            directory_path=join_path(
                                TRIAL_NETWORKS_DIRECTORY_PATH,
                                trial_network.tn_id,
                            )
                        )
                else:
                    trial_network = TrialNetworkModel()
                    trial_network.set_user_created(user_created=current_user.username)
                    with tn_id_lock:
                        trial_network.set_tn_id(size=3)
                    trial_network.set_directory_path(
                        directory_path=join_path(
                            TRIAL_NETWORKS_DIRECTORY_PATH,
                            trial_network.tn_id,
                        )
                    )
                if not sites_branch or not deployment_site:
                    return {
                        "message": "All parameters are required when validate=True"
                    }, 400
                library_handler = LibraryHandler(
                    reference_type=library_reference_type,
                    reference_value=library_reference_value,
                    directory_path=trial_network.directory_path,
                )
                library_handler.repository_handler.git_clone()
                library_handler.repository_handler.git_checkout()
                trial_network.set_library_https_url(
                    library_https_url=library_handler.library_https_url
                )
                trial_network.set_library_commit_id(
                    library_commit_id=library_handler.repository_handler.git_last_commit_id()
                )
                trial_network.set_raw_descriptor(file=descriptor_file)
                sites_handler = SitesHandler(
                    reference_type="branch",
                    reference_value=sites_branch,
                    directory_path=trial_network.directory_path,
                )
                sites_handler.repository_handler.git_clone()
                sites_handler.repository_handler.git_fetch_prune()
                sites_handler.repository_handler.git_checkout()
                ansible_decrypt(
                    data_path=join_path(
                        sites_handler.sites_local_directory,
                        deployment_site,
                        "core.yaml",
                    ),
                    token=SitesSettings.SITES_TOKEN,
                )
                sites_handler.validate_deployment_site(deployment_site=deployment_site)
                trial_network.set_sites_https_url(
                    sites_https_url=sites_handler.sites_https_url
                )
                trial_network.set_sites_commit_id(
                    sites_commit_id=sites_handler.repository_handler.git_last_commit_id()
                )
                trial_network.set_deployment_site(deployment_site=deployment_site)
                trial_network.set_state(state="validating")
                trial_network.save()
                TrialNetworkLogger(tn_id=tn_id).info(
                    message="Trial network validating. In this transition, the trial network descriptor is going to be validated"
                )
                trial_network.validate_descriptor(
                    library_handler=library_handler, sites_handler=sites_handler
                )
                trial_network.set_sorted_descriptor()
                trial_network.set_state(state="validated")
                trial_network.save()
                TrialNetworkLogger(tn_id=tn_id).info(
                    message="Trial network validated. In this state, the trial network descriptor has been validated and is ready to be deployed"
                )
                return trial_network.to_dict_created_validated(), 201
        except CustomException as e:
            if trial_network and validate == "True":
                trial_network.set_state(state="created")
                trial_network.save()
                if sites_handler and exist_directory(
                    path=sites_handler.sites_local_directory
                ):
                    remove_directory(path=sites_handler.sites_local_directory)
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            if trial_network and validate == "True":
                trial_network.set_state(state="created")
                trial_network.save()
                if sites_handler and exist_directory(
                    path=sites_handler.sites_local_directory
                ):
                    remove_directory(path=sites_handler.sites_local_directory)
            return abort(code=500, message=str(e))


@trial_network_namespace.route("s")
class TrialNetworks(Resource):
    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self):
        """
        Retrieve all trial networks
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_networks = TrialNetworkModel.objects(
                user_created=current_user.username
            )
            if current_user.role == "admin":
                trial_networks = TrialNetworkModel.objects()
            return {
                "trial_networks": [
                    trial_network.to_dict_full() for trial_network in trial_networks
                ]
            }, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@trial_network_namespace.param(
    name="tn_id", type="str", description="Trial network identifier"
)
@trial_network_namespace.route("s/<string:tn_id>")
class SpecificTrialNetwork(Resource):
    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id: str):
        """
        Retrieve trial network
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
                }, 404
            return trial_network.to_dict_full(), 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@trial_network_namespace.param(
    name="tn_id", type="str", description="Trial network identifier"
)
@trial_network_namespace.route("s/<string:tn_id>/activate")
class ActivateTrialNetwork(Resource):
    parser_put = reqparse.RequestParser()
    parser_put.add_argument(
        "jenkins_deploy_pipeline",
        type=str,
        required=False,
        help=f"Name of the Jenkins pipeline used to deploy a trial network. It is optional. If not specified, pipeline will be created inside TNLCM folder in Jenkins with the name **{JenkinsSettings.JENKINS_DEPLOY_PIPELINE}_<tn_id>**. If specified, will be checked that it exists in Jenkins and that it has nothing queued to execute",
    )

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @trial_network_namespace.expect(parser_put)
    def put(self, tn_id: str):
        """
        Activate trial network
        """
        try:
            jenkins_deploy_pipeline = self.parser_put.parse_args()[
                "jenkins_deploy_pipeline"
            ]

            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
                }, 404
            state = trial_network.state
            if (
                state != "validated"
                and state != "failed-activation"
                and state != "destroyed"
            ):
                return {
                    "message": f"Trial network with identifier {tn_id} is not possible to activate. Only trial networks with status validated, failed-activation or destroyed can be activated. Current status: {state}"
                }, 400
            if state == "validated":
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                if not jenkins_deploy_pipeline:
                    jenkins_deploy_pipeline, jenkins_deploy_pipeline_url = (
                        jenkins_handler.clone_pipeline(
                            old_name=JenkinsSettings.JENKINS_DEPLOY_PIPELINE,
                            new_name=JenkinsSettings.JENKINS_TNLCM_DIRECTORY
                            + "/"
                            + JenkinsSettings.JENKINS_DEPLOY_PIPELINE
                            + "_"
                            + trial_network.tn_id,
                        )
                    )
                sites_handler = SitesHandler(
                    https_url=trial_network.sites_https_url,
                    reference_type="commit",
                    reference_value=trial_network.sites_commit_id,
                    directory_path=trial_network.directory_path,
                )
                site_available_components = sites_handler.get_site_available_components(
                    deployment_site=trial_network.deployment_site
                )
                resource_manager = ResourceManagerModel()
                with tn_resource_manager_lock:
                    resource_manager.apply_resource_manager(
                        trial_network, site_available_components
                    )
                trial_network.set_jenkins_deploy_pipeline(
                    jenkins_deploy_pipeline=jenkins_deploy_pipeline,
                    jenkins_deploy_pipeline_url=jenkins_deploy_pipeline_url,
                )
                trial_network.set_state(state="activating")
                trial_network.save()
                TrialNetworkLogger(tn_id=tn_id).info(
                    message="Trial network activating. In this transition, the trial network proceeds to the deployment of the components defined in the descriptor"
                )
                jenkins_handler.deploy_trial_network()
                trial_network.set_state(state="activated")
                trial_network.save()
                TrialNetworkLogger(tn_id=tn_id).info(
                    message="Trial network activated. In this state, the trial network has been deployed and is ready to be used"
                )
                return {
                    "message": f"Trial network with identifier {tn_id} activated. The trial network deployment generates a report file showing the information of the components that have been deployed"
                }, 200
            elif state == "failed-activation":
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                trial_network.set_state(state="activating")
                trial_network.save()
                TrialNetworkLogger(tn_id=tn_id).info(
                    message="Trial network activating. In this transition, the trial network proceeds to the deployment of the components"
                )
                jenkins_handler.deploy_trial_network()
                trial_network.set_state(state="activated")
                trial_network.save()
                TrialNetworkLogger(tn_id=tn_id).info(
                    message="Trial network activated. In this state, the trial network has been deployed and is ready to be used"
                )
                return {
                    "message": f"Trial network with identifier {tn_id} activated. The trial network deployment generates a report file showing the information of the components that have been deployed"
                }, 200
            elif state == "destroyed":
                sites_handler = SitesHandler(
                    https_url=trial_network.sites_https_url,
                    reference_type="commit",
                    reference_value=trial_network.sites_commit_id,
                    directory_path=trial_network.directory_path,
                )
                site_available_components = sites_handler.get_site_available_components(
                    deployment_site=trial_network.deployment_site
                )
                resource_manager = ResourceManagerModel()
                with tn_resource_manager_lock:
                    resource_manager.apply_resource_manager(
                        trial_network, site_available_components
                    )
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                trial_network.set_state(state="activating")
                trial_network.save()
                TrialNetworkLogger(tn_id=tn_id).info(
                    message="Trial network activating. In this transition, the trial network proceeds to the deployment of the components"
                )
                jenkins_handler.deploy_trial_network()
                trial_network.set_state(state="activated")
                trial_network.save()
                TrialNetworkLogger(tn_id=tn_id).info(
                    message="Trial network activated. In this state, the trial network has been deployed and is ready to be used"
                )
                return {
                    "message": f"Trial network with identifier {tn_id} re-activated. The trial network deployment generates a report file showing the information of the components that have been deployed"
                }, 200
            else:  # TODO: suspended
                return {"message": "TODO: RESTART trial network suspended"}, 400
        except CustomException as e:
            trial_network.set_state(state="failed-activation")
            trial_network.save()
            TrialNetworkLogger(tn_id=tn_id).info(
                message="Trial network failed-activation. In this state, the trial network is waiting to be deployed"
            )
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            trial_network.set_state(state="failed-activation")
            trial_network.save()
            TrialNetworkLogger(tn_id=tn_id).info(
                message="Trial network failed-activation. In this state, the trial network is waiting to be deployed"
            )
            return abort(code=500, message=str(e))


@trial_network_namespace.param(
    name="tn_id", type="str", description="Trial network identifier"
)
@trial_network_namespace.route("s/<string:tn_id>/destroy")
class DestroyTrialNetwork(Resource):
    parser_delete = reqparse.RequestParser()
    parser_delete.add_argument(
        "jenkins_destroy_pipeline",
        type=str,
        required=False,
        help=f"Name of the Jenkins pipeline used to destroy a trial network. It is optional. If not specified, pipeline will be created inside TNLCM folder in Jenkins with the name **{JenkinsSettings.JENKINS_DESTROY_PIPELINE}_<tn_id>**. If specified, will be checked that it exists in Jenkins and that it has nothing queued to execute",
    )

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @trial_network_namespace.expect(parser_delete)
    def delete(self, tn_id: str):
        """
        Destroy trial network
        """
        try:
            jenkins_destroy_pipeline = self.parser_delete.parse_args()[
                "jenkins_destroy_pipeline"
            ]

            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
                }, 404
            state = trial_network.state
            if (
                state != "activated"
                and state != "failed-activation"
                and state != "failed-destruction"
            ):
                return {
                    "message": f"Trial network with identifier {tn_id} is not possible to destroy. Only trial networks with status activated, failed-activation or failed-destruction can be destroyed. Current status: {state}"
                }, 400
            library_handler = LibraryHandler(
                https_url=trial_network.library_https_url,
                reference_type="commit",
                reference_value=trial_network.library_commit_id,
                directory_path=trial_network.directory_path,
            )
            jenkins_handler = JenkinsHandler(
                trial_network=trial_network, library_handler=library_handler
            )
            if not jenkins_destroy_pipeline:
                jenkins_destroy_pipeline, jenkins_destroy_pipeline_url = (
                    jenkins_handler.clone_pipeline(
                        old_name=JenkinsSettings.JENKINS_DESTROY_PIPELINE,
                        new_name=JenkinsSettings.JENKINS_TNLCM_DIRECTORY
                        + "/"
                        + JenkinsSettings.JENKINS_DESTROY_PIPELINE
                        + "_"
                        + trial_network.tn_id,
                    )
                )
            trial_network.set_jenkins_destroy_pipeline(
                jenkins_destroy_pipeline=jenkins_destroy_pipeline,
                jenkins_destroy_pipeline_url=jenkins_destroy_pipeline_url,
            )
            trial_network.set_state(state="destroying")
            trial_network.save()
            TrialNetworkLogger(tn_id=tn_id).info(
                message="Trial network destroying. In this transition, the trial network proceeds to the destruction of the components"
            )
            jenkins_handler.destroy_trial_network()
            trial_network.set_deployed_descriptor()
            resource_manager = ResourceManagerModel()
            with tn_resource_manager_lock:
                resource_manager.release_resource_manager(trial_network)
            trial_network.set_state("destroyed")
            trial_network.save()
            TrialNetworkLogger(tn_id=tn_id).info(
                message="Trial network destroyed. In this state, the trial network has been destroyed and ready for deploy again"
            )
            return {
                "message": f"Trial network with identifier {tn_id} destroyed. In this state, the trial network has been destroyed and ready for deploy again"
            }, 200
        except CustomException as e:
            trial_network.set_state(state="failed-destruction")
            trial_network.save()
            TrialNetworkLogger(tn_id=tn_id).info(
                message="Trial network failed-destruction. In this state, the trial network is waiting to be destroyed"
            )
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            trial_network.set_state(state="failed-destruction")
            trial_network.save()
            TrialNetworkLogger(tn_id=tn_id).info(
                message="Trial network failed-destruction. In this state, the trial network is waiting to be destroyed"
            )
            return abort(code=500, message=str(e))


@trial_network_namespace.param(
    name="tn_id", type="str", description="Trial network identifier"
)
@trial_network_namespace.route("s/<string:tn_id>/library")
class LibraryComponentsTrialNetwork(Resource):
    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id: str):
        """
        Retrieve the components associated to trial network
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
                }, 404
            library_handler = LibraryHandler(
                https_url=trial_network.library_https_url,
                reference_type="branch",
                reference_value="main",
                directory_path=trial_network.directory_path,
            )
            library_handler.repository_handler.git_checkout()
            library_handler.repository_handler.git_pull()
            library_handler.repository_handler.git_fetch_prune()
            library_handler = LibraryHandler(
                https_url=trial_network.library_https_url,
                reference_type="commit",
                reference_value=trial_network.library_commit_id,
                directory_path=trial_network.directory_path,
            )
            library_handler.repository_handler.git_checkout()
            return {"components": library_handler.get_components()}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@trial_network_namespace.param(
    name="tn_id", type="str", description="Trial network identifier"
)
@trial_network_namespace.param(
    name="component_name", type="str", description="Library component name"
)
@trial_network_namespace.route("s/<string:tn_id>/library/<string:component_name>")
class LibraryComponentTrialNetwork(Resource):
    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id: str, component_name: str):
        """
        Retrieve the component information associated to trial network
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
                }, 404
            library_handler = LibraryHandler(
                https_url=trial_network.library_https_url,
                reference_type="commit",
                reference_value=trial_network.library_commit_id,
                directory_path=trial_network.directory_path,
            )
            return {
                "component": library_handler.get_component_input(
                    component_name=component_name
                )
            }, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@trial_network_namespace.param(
    name="tn_id", type="str", description="Trial network identifier"
)
@trial_network_namespace.route("s/<string:tn_id>/log/content")
class LogTrialNetwork(Resource):
    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id):
        """
        Retrieve the content of the trial network log file
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
                }, 404
            log_path = join_path(trial_network.directory_path, f"{tn_id}.log")
            if not is_file(path=log_path):
                return {
                    "message": f"Trial network with identifier {tn_id} log file not found"
                }, 404
            log_content = load_file(file_path=log_path)
            return {"log_content": log_content}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@trial_network_namespace.param(
    name="tn_id", type="str", description="Trial network identifier"
)
@trial_network_namespace.route("s/<string:tn_id>/log/download")
class DownloadLogTrialNetwork(Resource):
    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id):
        """
        Download the content of the trial network log file
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
                }, 404
            file_name = f"{tn_id}.log"
            log_path = join_path(trial_network.directory_path, file_name)
            if not is_file(path=log_path):
                return {
                    "message": f"Trial network with identifier {tn_id} log file not found"
                }, 404
            return send_file(
                path_or_file=log_path,
                as_attachment=True,
                download_name=file_name,
                mimetype="application/octet-stream",
            )
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@trial_network_namespace.param(
    name="tn_id", type="str", description="Trial network identifier"
)
@trial_network_namespace.route("s/<string:tn_id>/purge")
class PurgeTrialNetwork(Resource):
    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def delete(self, tn_id: str):
        """
        Purge trial network
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
                }, 404
            state = trial_network.state
            if state != "validated" and state != "destroyed" and state != "created":
                return {
                    "message": f"Trial network with identifier {tn_id} is not possible to purge. Only trial networks with status validated, destroyed or created can be purged. Current status: {state}"
                }, 400
            if state == "destroyed":
                jenkins_handler = JenkinsHandler(trial_network=trial_network)
                jenkins_deploy_pipeline = trial_network.get_jenkins_deploy_pipeline()
                jenkins_handler.remove_pipeline(pipeline_name=jenkins_deploy_pipeline)
                jenkins_destroy_pipeline = trial_network.get_jenkins_destroy_pipeline()
                jenkins_handler.remove_pipeline(pipeline_name=jenkins_destroy_pipeline)
            remove_directory(path=trial_network.directory_path)
            trial_network.delete()
            return {
                "message": f"Trial network with identifier {tn_id} has been purged. In this state, the trial network has been deleted and cannot be recovered"
            }, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@trial_network_namespace.param(
    name="tn_id", type="str", description="Trial network identifier"
)
@trial_network_namespace.route("s/<string:tn_id>/report/content")
class ReportTrialNetwork(Resource):
    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id: str):
        """
        Retrieve the content of the trial network report file
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
                }, 404
            if trial_network.state != "activated":
                return {
                    "message": f"Trial network with identifier {tn_id} is not possible to retrieve the report. Only trial networks with status activated can retrieve the report. Current status: {trial_network.state}"
                }, 400
            report_path = join_path(trial_network.directory_path, f"{tn_id}.md")
            if not is_file(path=report_path):
                return {
                    "message": f"Trial network with identifier {tn_id} report file not found"
                }, 404
            report_content = load_file(file_path=report_path)
            return {"report_content": report_content}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@trial_network_namespace.param(
    name="tn_id", type="str", description="Trial network identifier"
)
@trial_network_namespace.route("s/<string:tn_id>/report/download")
class DownloadReportTrialNetwork(Resource):
    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, tn_id: str):
        """
        Download report generated after trial network deployment as markdown file
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
                }, 404
            if trial_network.state != "activated":
                return {
                    "message": f"Trial network with identifier {tn_id} is not possible to download the report. Only trial networks with status activated can download the report. Current status: {trial_network.state}"
                }, 400
            file_name = f"{trial_network.tn_id}.md"
            report_path_md = join_path(trial_network.directory_path, file_name)
            if not is_file(path=report_path_md):
                return {
                    "message": f"Trial network with identifier {tn_id} report file not found"
                }, 404
            return send_file(
                path_or_file=report_path_md,
                as_attachment=True,
                download_name=file_name,
                mimetype="application/octet-stream",
            )
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@trial_network_namespace.param(
    name="tn_id", type="str", description="Trial network identifier"
)
@trial_network_namespace.route("s/<string:tn_id>/update")
class UpdateTrialNetwork(Resource):
    parser_put = reqparse.RequestParser()
    parser_put.add_argument(
        "descriptor",
        location="files",
        type=FileStorage,
        required=True,
        help="Trial network descriptor file",
    )

    @trial_network_namespace.doc(security="Bearer Auth")
    @trial_network_namespace.errorhandler(PyJWTError)
    @trial_network_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    @trial_network_namespace.expect(parser_put)
    def put(self, tn_id: str):
        """
        Update trial network
        """
        try:
            descriptor_file = self.parser_put.parse_args()["descriptor"]

            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
                }, 404
            if trial_network.state != "created":
                return {
                    "message": f"Trial network with identifier {tn_id} is not possible to update. Only trial networks with status created can be updated. Current status: {trial_network.state}"
                }, 400
            trial_network.set_raw_descriptor(file=descriptor_file)
            trial_network.save()
            return trial_network.to_dict_created(), 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


# @trial_network_namespace.param(
#     name="tn_id", type="str", description="Trial network identifier"
# )
# @trial_network_namespace.route("s/<string:tn_id>/suspend")
# class SuspendTrialNetwork(Resource):
#     parser_put = reqparse.RequestParser()
#     parser_put.add_argument(
#         "jenkins_suspend_pipeline",
#         type=str,
#         required=False,
#         help=f"Name of the Jenkins pipeline used to suspend a trial network. It is optional. If not specified, pipeline will be created inside TNLCM folder in Jenkins with the name **{JenkinsSettings.JENKINS_SUSPEND_PIPELINE}_<tn_id>**. If specified, will be checked that it exists in Jenkins and that it has nothing queued to execute",
#     )

#     @trial_network_namespace.doc(security="Bearer Auth")
#     @trial_network_namespace.errorhandler(PyJWTError)
#     @trial_network_namespace.errorhandler(JWTExtendedException)
#     @jwt_required()
#     @trial_network_namespace.expect(parser_put)
#     def put(self, tn_id: str):
#         """
#         Suspend trial network
#         """
#         try:
#             jenkins_suspend_pipeline = self.parser_put.parse_args()[
#                 "jenkins_suspend_pipeline"
#             ]

#             current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
#             trial_network = TrialNetworkModel.objects(
#                 user_created=current_user.username, tn_id=tn_id
#             ).first()
#             if current_user.role == "admin":
#                 trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
#             if not trial_network:
#                 return {
#                     "message": f"No trial network with identifier {tn_id} created by the user {current_user.username}"
#                 }, 404
#             state = trial_network.state
#             if state != "activated":
#                 return {
#                     "message": f"Trial network with identifier {tn_id} is not possible to suspend. Only trial networks with status ACTIVATED can be suspended"
#                 }, 400
#             trial_network.set_state(state="suspending")
#             trial_network.save()
#         except CustomException as e:
#             trial_network.set_state(state="activated")
#             trial_network.save()
#             return {"message": str(e.message)}, e.status_code
#         except Exception as e:
#             trial_network.set_state(state="activated")
#             trial_network.save()
#             return abort(code=500, message=str(e))
