import sys
import os
import json
sys.path.append('..')

from flask import request, jsonify
from flask_restx import Namespace, Resource, abort
from json import JSONDecodeError

api = Namespace('callback', "Handling the data returned by jenkins after deploying the components")

callback_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Callback')

@api.route("")
class CallbackResource(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Invalid callback format')
    @api.response(422, 'Malformed or insecure callback received')
    def post(self):
        """
        Get jenkins results from deploying components
        """
        try:
            data = request.get_json()
            os.makedirs(callback_directory, exist_ok=True)
            file_path = os.path.join(callback_directory, "data.json")
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)

            return jsonify({'content': data, 'savedTo': file_path})
        except JSONDecodeError as e:
            return abort(400, 'Invalid JSON format')
        except Exception as e:
            return abort(422, 'Malformed or insecure callback received')