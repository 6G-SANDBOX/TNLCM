from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Namespace, Resource, abort
from jwt.exceptions import PyJWTError

from core.auth.auth import get_current_user_from_jwt
from core.exceptions.exceptions_handler import CustomException
from core.library.library_handler import LibraryHandler
from core.models.trial_network import TrialNetworkModel
from core.sites.sites_handler import SitesHandler

debug_namespace = Namespace(
    name="debug",
    description="Namespace for debug only for developers",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
        }
    },
)


@debug_namespace.param(name="tn_id", type="str", description="Trial network identifier")
@debug_namespace.param(
    name="commit_id",
    type="str",
    description="New commit of library that will be used for deploy the trial network",
)
@debug_namespace.route(
    "/trial-networks/<string:tn_id>/library/commits/<string:commit_id>"
)
class UpdateCommitLibrary(Resource):
    @debug_namespace.doc(security="Bearer Auth")
    @debug_namespace.errorhandler(PyJWTError)
    @debug_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def post(self, tn_id: str, commit_id: str):
        """
        Update the Library commit associated with the trial network
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            trial_network.set_library_commit_id(library_commit_id=commit_id)
            trial_network.save()
            library_handler = LibraryHandler(
                https_url=trial_network.library_https_url,
                reference_type="commit",
                reference_value=trial_network.library_commit_id,
                directory_path=trial_network.directory_path,
            )
            library_handler.repository_handler.git_checkout()
            return trial_network.to_dict_debug_commit_id(), 201
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@debug_namespace.param(name="tn_id", type="str", description="Trial network identifier")
@debug_namespace.param(
    name="commit_id",
    type="str",
    description="New commit of sites that will be used for deploy the trial network",
)
@debug_namespace.route(
    "/trial-networks/<string:tn_id>/sites/commits/<string:commit_id>"
)
class UpdateCommitSites(Resource):
    @debug_namespace.doc(security="Bearer Auth")
    @debug_namespace.errorhandler(PyJWTError)
    @debug_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def post(self, tn_id: str, commit_id: str):
        """
        Update the Sites commit associated with the trial network
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
            if current_user.role == "admin":
                trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            trial_network.set_sites_commit_id(commit_id)
            trial_network.save()
            sites_handler = SitesHandler(
                https_url=trial_network.sites_https_url,
                reference_type="commit",
                reference_value=trial_network.library_commit_id,
                directory_path=trial_network.directory_path,
            )
            sites_handler.repository_handler.git_checkout()
            return trial_network.to_dict_debug_commit_id(), 201
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@debug_namespace.param(name="tn_id", type="str", description="Trial network identifier")
@debug_namespace.param(
    name="entity_name",
    type="str",
    description="Entity name of the descriptor that will be added debug: true",
)
@debug_namespace.route(
    "/trial-networks/<string:tn_id>/descriptor/add-debug/<string:entity_name>"
)
class AddDebugEntityName(Resource):
    @debug_namespace.doc(security="Bearer Auth")
    @debug_namespace.errorhandler(PyJWTError)
    @debug_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def post(self, tn_id: str, entity_name: str):
        """
        Add debug: true to the specified entity name
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
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
            return trial_network.to_dict_debug_entity_name(), 201
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@debug_namespace.param(name="tn_id", type="str", description="Trial network identifier")
@debug_namespace.param(
    name="entity_name",
    type="str",
    description="Entity name of the descriptor that will be removed debug: true",
)
@debug_namespace.route(
    "/trial-networks/<string:tn_id>/descriptor/remove-debug/<string:entity_name>"
)
class RemoveDebugEntityName(Resource):
    @debug_namespace.doc(security="Bearer Auth")
    @debug_namespace.errorhandler(PyJWTError)
    @debug_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def post(self, tn_id: str, entity_name: str):
        """
        REmove debug: true to the specified entity name
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            trial_network = TrialNetworkModel.objects(
                user_created=current_user.username, tn_id=tn_id
            ).first()
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
            return trial_network.to_dict_debug_entity_name(), 201
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))
