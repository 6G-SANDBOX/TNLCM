import sys
sys.path.append('..')
from Testbed import Testbed  # Otherwise this will use different class variables from app

from flask import jsonify
from flask_restx import Namespace, Resource, reqparse, abort
from os.path import exists
from yaml import safe_load


api = Namespace('testbed', "Testbed status and management")


@api.route("/")
class TestbedResource(Resource):
    def get(self):
        return jsonify({'trial_networks': Testbed.ListTrialNetworks()})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('descriptor', type=str, required=True)
        arguments = parser.parse_args()
        path = f"../{arguments['descriptor']}"

        if exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                descriptor = safe_load(file)

            tn = Testbed.CreateAndAddTrialNetwork(descriptor)
            return jsonify({'id': tn.Id})
        else:
            abort(404, f"Unknown descriptor '{arguments['descriptor']}'")




