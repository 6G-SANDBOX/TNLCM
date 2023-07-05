from flask import jsonify
from flask_restx import Namespace, Resource

api = Namespace('trial_network', "Trial Network status and management")


@api.route("/")
class ListTrialNetworks(Resource):
    def get(self):
        return jsonify(["1", "2", "3"])
