from flask import request
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Namespace, Resource, abort, reqparse
from jwt.exceptions import PyJWTError

from conf.jenkins import JenkinsSettings
from core.exceptions.exceptions_handler import CustomException
from core.logs.log_handler import TrialNetworkLogger
from core.models.trial_network import TrialNetworkModel
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
    # parser_post.add_argument(
    #     "endpoints",
    #     type="str",
    #     required=False,
    #     location="json",
    #     help="Endpoints of the component. It should be a dictionary",
    # )
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

    @callback_namespace.errorhandler(PyJWTError)
    @callback_namespace.errorhandler(JWTExtendedException)
    @callback_namespace.expect(parser_post)
    def post(self):
        """
        Save Jenkins results when deploy a component
        """
        trial_network = None
        try:
            client_ip = request.remote_addr
            if client_ip != JenkinsSettings.JENKINS_HOST:
                return {
                    "message": "Invalid host. Request not allowed. Only Jenkins host is allowed"
                }, 403
            tn_id = decode_base64(encoded_data=self.parser_post.parse_args()["tn_id"])
            component_type = decode_base64(
                encoded_data=self.parser_post.parse_args()["component_type"]
            )
            custom_name = decode_base64(
                encoded_data=self.parser_post.parse_args()["custom_name"]
            )
            # endpoints = self.parser_post.parse_args()["endpoints"]
            # if endpoints:
            #     endpoints = decode_base64(encoded_data=endpoints)
            markdown = decode_base64(
                encoded_data=self.parser_post.parse_args()["markdown"]
            )
            # output = self.parser_post.parse_args()["output"]
            entity_name = (
                f"{component_type}-{custom_name}"
                if custom_name != "None"
                else component_type
            )

            trial_network = TrialNetworkModel.objects(tn_id=tn_id).first()
            if not trial_network:
                return {
                    "message": f"No trial network with the name {tn_id} in database"
                }, 404
            report = trial_network.report
            report += markdown
            trial_network.set_report(report=report)
            trial_network.save()
            TrialNetworkLogger(tn_id=trial_network.tn_id).info(
                message=f"Results of the entity {entity_name} received by Jenkins saved successfully"
            )
            return {
                "message": f"Results of the entity {entity_name} received by Jenkins saved successfully"
            }, 200
        except CustomException as e:
            return {"message": str(e)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))
