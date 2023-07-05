from flask_restx import Api


from .trial_network import api as trial_network_api
from .testbed import api as testbed_api

api = Api(
    version='0.1'
)

api.add_namespace(trial_network_api, path="/trial_network")
api.add_namespace(testbed_api, path="/testbed")

