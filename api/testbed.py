from flask import jsonify
from flask_restx import Namespace, Resource

api = Namespace('testbed', "Testbed status and management")


@api.route("/")
class ListTestbed(Resource):
    def get(self):
        return jsonify(["A", "S", "D"])
