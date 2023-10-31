import sys
sys.path.append('..')
from Testbed import Testbed  # Otherwise this will use different class variables from app

from uuid import UUID
from flask import jsonify
from flask_restx import Namespace, Resource, abort, reqparse
from shared.data import TrialNetwork

api = Namespace('trial_network', "Trial Network status and management")

parser = reqparse.RequestParser()
parser.add_argument('target', type=str, required=True,
                    choices=tuple(c.name for c in TrialNetwork.Status if c not in [TrialNetwork.Status.Null,
                                                                                   TrialNetwork.Status.Transitioning]))


@api.response(200, 'Success')
@api.response(404, 'Trial Network not found')
@api.route("/<uuid:tnId>")
class TrialNetworkResource(Resource):
    def get(self, tnId: UUID):
        tn = Testbed.GetTrialNetwork(tnId)
        if tn is None:
            return abort(404)
        else:
            return jsonify(tn.Serialized)

    @api.expect(parser)
    @api.response(409, 'Trial Network is currently transitioning or already in the target status')
    def put(self, tnId: UUID):
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

    @api.response(409, 'Trial Network cannot currently be deleted (is transitioning or already marked for destruction)')
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
