from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Namespace, Resource, abort, reqparse
from jwt.exceptions import PyJWTError

from core.exceptions.exceptions_handler import CustomException
from core.logs.log_handler import TrialNetworkLogger
from core.models.trial_network import TrialNetworkModel
from core.utils.file import save_file, save_json_file
from core.utils.os import TRIAL_NETWORKS_DIRECTORY_PATH, join_path
from core.utils.parser import decode_base64

callback_namespace = Namespace(
    name="callback",
    description="Namespace for handler the data returned by Jenkins after deploy a component",
)


@callback_namespace.route("")
class Callback(Resource):
    parser_post = reqparse.RequestParser()
    parser_post.add_argument(
        "tn_id",
        type=str,
        required=True,
        location="json",
        help="Trial network identifier. It is optional. If not specified, a random will be generated. If specified, it should begin with character and max length 15",
    )
    parser_post.add_argument(
        "component_type",
        type=str,
        required=True,
        location="json",
        help="Component type. It should be a string",
    )
    parser_post.add_argument(
        "custom_name",
        type=str,
        required=True,
        location="json",
        help="Custom name of the component. It should be a string",
    )
    parser_post.add_argument(
        "endpoints",
        type="str",
        required=False,
        location="json",
        help="Endpoints of the component. It should be a dictionary",
    )
    parser_post.add_argument(
        "markdown",
        type=str,
        required=True,
        location="json",
        help="Markdown of the component. It should be a string",
    )
    # parser_post.add_argument(
    #     "output",
    #     type=str,
    #     required=False,
    #     location="json",
    #     help="Output of the component. It should be a string",
    # )
    parser_post.add_argument(
        "success",
        type=str,
        required=True,
        location="json",
        help="Success of the component. It should be a string",
    )

    @callback_namespace.errorhandler(PyJWTError)
    @callback_namespace.errorhandler(JWTExtendedException)
    @callback_namespace.expect(parser_post)
    def post(self):
        """
        Save Jenkins results when deploy a component
        """
        trial_network = None
        try:
            tn_id = decode_base64(encoded_data=self.parser_post.parse_args()["tn_id"])
            component_type = decode_base64(
                encoded_data=self.parser_post.parse_args()["component_type"]
            )
            custom_name = decode_base64(
                encoded_data=self.parser_post.parse_args()["custom_name"]
            )
            endpoints = self.parser_post.parse_args()["endpoints"]
            if endpoints:
                endpoints = decode_base64(encoded_data=endpoints)
            markdown = decode_base64(
                encoded_data=self.parser_post.parse_args()["markdown"]
            )
            # output = self.parser_post.parse_args()["output"]
            success = self.parser_post.parse_args()["success"]
            entity_name = (
                f"{component_type}-{custom_name}"
                if custom_name != "None"
                else component_type
            )
            decoded_data = {
                "tn_id": tn_id,
                "component_type": component_type,
                "custom_name": custom_name,
                "endpoints": endpoints,
                "markdown": markdown,
                # "output": output,
                "success": success,
            }

            trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with the name {tn_id} in database"
                }, 404
            if success != "true":
                return {
                    "message": f"Pipeline for entity {entity_name} failed because success value received by Jenkins is {success}"
                }, 500
            trial_network.set_output(entity_name, decoded_data)
            trial_network.save()
            directory_path = join_path(TRIAL_NETWORKS_DIRECTORY_PATH, tn_id)
            save_json_file(
                data=decoded_data,
                file_path=join_path(directory_path, "output", f"{entity_name}.json"),
            )
            save_file(
                data=markdown,
                file_path=join_path(directory_path, f"{tn_id}.md"),
                mode="a",
            )
            # trial_network_logger = TrialNetworkLogger.get_logger(
            #     tn_id=trial_network.tn_id
            # )
            # trial_network_logger.info(
            #     msg=f"Results of the entity {entity_name} received by Jenkins saved successfully"
            # )
            return {
                "message": f"Results of the entity {entity_name} received by Jenkins saved successfully"
            }, 200
        except CustomException as e:
            if trial_network:
                trial_network.set_state("failed")
                trial_network.save()
            return {"message": str(e)}, e.status_code
        except Exception as e:
            if trial_network:
                trial_network.set_state("failed")
                trial_network.save()
            return abort(code=500, message=str(e))
