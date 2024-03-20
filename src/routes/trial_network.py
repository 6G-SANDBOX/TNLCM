from flask_restx import Namespace, Resource, reqparse, abort
from werkzeug.datastructures import FileStorage

from src.trial_network.trial_network_queries import get_trial_networks, create_trial_network, get_descriptor_trial_network, get_status_trial_network, update_status_trial_network, delete_trial_network
from src.callback.jenkins_handler import JenkinsHandler
from src.exceptions.exceptions_handler import CustomException

trial_network_namespace = Namespace(
    name="trial_network",
    description="Trial network status and management"
)

@trial_network_namespace.route("")
class CreateTrialNetwork(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("descriptor", location="files", type=FileStorage, required=True)

    @trial_network_namespace.expect(parser)
    def post(self):
        """
        Create and add a trial network to database
        """
        try:
            descriptor_file = self.parser.parse_args()["descriptor"]
            tn_id = create_trial_network(descriptor_file)
            return {"tn_id": tn_id}, 201
        except CustomException as e:
            return abort(e.error_code, str(e))

@trial_network_namespace.route("/<string:tn_id>")
class TrialNetwork(Resource):

    parser_put = reqparse.RequestParser()
    parser_put.add_argument("branch", type=str, required=False)
    parser_put.add_argument("commit_id", type=str, required=False)

    def get(self, tn_id):
        """
        Returns the descriptor of the trial network specified in tn_id
        """
        try:
            sorted_descriptor = get_descriptor_trial_network(tn_id)
            return sorted_descriptor, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

    @trial_network_namespace.expect(parser_put)
    def put(self, tn_id):
        """
        Trial network component deployment begins
        **Can specify a branch or a commit_id of the 6G-Library. If nothing is specified, the main branch will be used**
        """
        try:
            branch = self.parser_put.parse_args()["branch"]
            commit_id = self.parser_put.parse_args()["commit_id"]

            self.jenkins_handler = JenkinsHandler()
            self.jenkins_handler.deploy_trial_network(tn_id, branch=branch, commit_id=commit_id)
            return {"message": "Trial network start deployment with jenkins"}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
    
    def delete(self, tn_id):
        """
        Delete a trial network specified in tn_id
        """
        try:
            delete_trial_network(tn_id)
            return {"message": f"The trial network with identifier '{tn_id}' has been removed from the database"}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))

@trial_network_namespace.route("s/") 
class TrialNetworks(Resource):

    def get(self):
        """
        Returns all the trial networks stored in database
        """
        try:
            trial_networks = get_trial_networks()
            if trial_networks:
                return {"tn_ids": trial_networks}, 200
            else:
                return abort(404, "No trial networks stored in 'trial_network' collection in the database tnlcm-database")
        except CustomException as e:
            return abort(e.error_code, str(e))

@trial_network_namespace.route("/status/<string:tn_id>") 
class StatusTrialNetwork(Resource):

    def get(self, tn_id):
        """
        Returns the status of the Trial network specified in tn_id
        """
        try:
            status_trial_network = get_status_trial_network(tn_id)
            return status_trial_network, 200
        except CustomException as e:
            return abort(e.error_code, str(e))
    
    parser_put = reqparse.RequestParser()
    parser_put.add_argument("new_status", type=str, required=True)

    @trial_network_namespace.expect(parser_put)
    def put(self, tn_id):
        """
        Update the status of the Trial network specified in tn_id
        """
        try:
            new_status = self.parser_put.parse_args()["new_status"]
            update_status_trial_network(tn_id, new_status)
            return {"message": f"The status of the trial network with identifier '{tn_id}' has been updated to '{new_status}'"}, 200
        except CustomException as e:
            return abort(e.error_code, str(e))