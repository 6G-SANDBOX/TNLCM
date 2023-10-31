import sys
sys.path.append('..')

from uuid import UUID
from flask import jsonify
from flask_restx import Namespace, Resource, abort, reqparse
from shared import Library

api = Namespace('playbook', "Component's playbook and 6G-Library handling")


@api.route("/<string:text>")
class TestbedResource(Resource):
    def get(self, text: str):
        return jsonify({'text': text})
