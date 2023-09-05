import sys
sys.path.append('..')
from Testbed import Testbed  # Otherwise this will use different class variables from app

from flask import jsonify
from flask_restx import Namespace, Resource



api = Namespace('testbed', "Testbed status and management")


@api.route("/")
class ListTestbed(Resource):
    def get(self):
        return jsonify({'trial_networks': Testbed.ListTrialNetworks()})
