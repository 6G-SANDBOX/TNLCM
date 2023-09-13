import sys
sys.path.append('..')
from Testbed import Testbed  # Otherwise this will use different class variables from app

from uuid import UUID
from flask import jsonify
from flask_restx import Namespace, Resource, abort, reqparse
from shared.data import TrialNetwork

api = Namespace('trial_network', "Trial Network status and management")


@api.route("/")
class ListTrialNetworks(Resource):
    def get(self):
        return jsonify({'trial_networks': Testbed.ListTrialNetworks()})


@api.route("/<uuid:tnId>")
class TrialNetworkResource(Resource):
    def get(self, tnId: UUID):
        tn = Testbed.GetTrialNetwork(tnId)
        if tn is None:
            return abort(404)
        else:
            return jsonify(tn.Serialized)

    def put(self, tnId: UUID):
        parser = reqparse.RequestParser()
        parser.add_argument('target', type=str, choices=(c.name for c in TrialNetwork.Status), required=True,
                            help="Invalid 'target': {error_msg}")
        arguments = parser.parse_args()
        target = arguments['target']
        tn = Testbed.GetTrialNetwork(tnId)
        if tn is None:
            return abort(404)
        else:
            maybeError = tn.MarkForTransition(TrialNetwork.Status[target])
            if maybeError is None:
                return jsonify({'message': f"Trial Network marked for transition to '{target}'"})
            else:
                return abort(409, maybeError)

    def delete(self, tnId: UUID):
        tn = Testbed.GetTrialNetwork(tnId)
        if tn is None:
            return abort(404)
        else:
            maybeError = tn.MarkForTransition(TrialNetwork.Status.Destroyed)
            if maybeError is None:
                return jsonify({'message': 'Trial Network marked for destruction'})
            else:
                return abort(409, maybeError)

