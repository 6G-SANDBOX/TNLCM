from flask_restx import Namespace, Resource, reqparse, abort
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from yaml import safe_load, YAMLError

from src.trial_network.trial_network_queries import get_trial_networks, create_trial_network, get_descriptor_trial_network
from src.callback.jenkins_functions import deploy_trial_network

trial_network_namespace = Namespace(
    name="trial_network",
    description="Trial Network status and management"
)

@trial_network_namespace.route("")
class CreateTrialNetwork(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("descriptor", location="files", type=FileStorage, required=True)

    @trial_network_namespace.expect(parser)
    def post(self):
        """
        Create and add a Trial Network
        """
        descriptor_file = self.parser.parse_args()["descriptor"]
        filename = secure_filename(descriptor_file.filename)
        if '.' in filename and filename.split('.')[-1].lower() in ['yml', 'yaml']:
            try:
                descriptor = safe_load(descriptor_file.stream)
            except YAMLError as e:
                return abort(422, f"Malformed or insecure descriptor received: '{e}'.")
            tn_id = create_trial_network(descriptor)
            return {'id': tn_id}, 200
        else:
            return abort(400, "Invalid descriptor format, only 'yml' or 'yaml' files will be further processed.")

@trial_network_namespace.route("/<string:tn_id>")
class DeployTrialNetwork(Resource):

    def get(self, tn_id):
        """
        Returns the descriptor of the Trial Network specified in tn_id
        """
        try:
            sorted_descriptor = get_descriptor_trial_network(tn_id)
            return sorted_descriptor, 200
        except ValueError as e:
            return abort(404, e)
        except Exception as e:
            return abort(422, e)

    def put(self, tn_id):
        """
        Trial Network component deployment begins
        """
        try:
            deploy_trial_network(tn_id)
            return {"message": "Trial Network start deployment with jenkins"}, 200
        except ValueError as e:
            return abort(404, e)
        except Exception as e:
            return abort(422, e)

@trial_network_namespace.route("s/") 
class TrialNetworks(Resource):

    def get(self):
        """
        Returns all the Trial Networks stored
        """
        try:
            trial_networks = get_trial_networks()
            return {"tn_ids": trial_networks}, 200
        except ValueError as e:
            return abort(404, e)
        except Exception as e:
            return abort(422, e)