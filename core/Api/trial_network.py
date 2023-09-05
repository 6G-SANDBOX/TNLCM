import sys
sys.path.append('..')
from Testbed import Testbed  # Otherwise this will use different class variables from app

from uuid import UUID
from flask import jsonify, abort
from flask_restx import Namespace, Resource

api = Namespace('trial_network', "Trial Network status and management")


@api.route("/")
class ListTrialNetworks(Resource):
    def get(self):
        return jsonify({'trial_networks': Testbed.ListTrialNetworks()})


@api.route("/<uuid:tnId>")
class GetTrialNetwork(Resource):
    def get(self, tnId: UUID):
        tn = Testbed.GetTrialNetwork(tnId)
        if tn is None:
            return abort(404)
        else:
            return jsonify(tn.Serialized)


