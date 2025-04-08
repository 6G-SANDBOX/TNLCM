from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Namespace, Resource, abort
from jwt.exceptions import PyJWTError

from conf.influxdb2 import InfluxDB2Settings
from core.auth.auth import get_current_user_from_jwt
from core.exceptions.exceptions import CustomException
from core.libs.influxdb2 import InfluxDBWrapper
from core.models.trial_network import TrialNetworkModel

influxdb2_namespace = Namespace(
    name="influxdb2",
    description="Namespace for InfluxDB2 management",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
        }
    },
)


@influxdb2_namespace.route("/buckets")
class Buckets(Resource):
    @influxdb2_namespace.doc(security="Bearer Auth")
    @influxdb2_namespace.errorhandler(PyJWTError)
    @influxdb2_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self):
        """
        Get InfluxDB2 buckets
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            client = InfluxDBWrapper(
                url=InfluxDB2Settings.INFLUXDB_URL,
                token=InfluxDB2Settings.INFLUXDB_TOKEN,
                org=InfluxDB2Settings.INFLUXDB_ORGANIZATION,
            )
            if current_user.role != "admin":
                trial_networks = TrialNetworkModel.objects(
                    user_created=current_user.username
                )
                buckets = []
                for trial_network in trial_networks:
                    if trial_network.tn_id in client.get_all_buckets():
                        buckets.append(trial_network.tn_id)
                return {"buckets": buckets}, 200
            else:
                return {"buckets": client.get_all_buckets()}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))


@influxdb2_namespace.param(
    name="bucket",
    type="str",
    description="Name of the bucket",
)
@influxdb2_namespace.route("/buckets/<string:bucket>/measurements")
class Measurements(Resource):
    @influxdb2_namespace.doc(security="Bearer Auth")
    @influxdb2_namespace.errorhandler(PyJWTError)
    @influxdb2_namespace.errorhandler(JWTExtendedException)
    @jwt_required()
    def get(self, bucket: str):
        """
        Get InfluxDB2 measurements
        """
        try:
            current_user = get_current_user_from_jwt(jwt_identity=get_jwt_identity())
            client = InfluxDBWrapper(
                url=InfluxDB2Settings.INFLUXDB_URL,
                token=InfluxDB2Settings.INFLUXDB_TOKEN,
                org=InfluxDB2Settings.INFLUXDB_ORGANIZATION,
            )
            if current_user.role != "admin":
                trial_networks = TrialNetworkModel.objects(
                    user_created=current_user.username
                )
                if bucket not in [
                    trial_network.tn_id for trial_network in trial_networks
                ]:
                    return {"message": "Unauthorized"}, 403
                if bucket not in client.get_all_buckets():
                    return {"message": f"Bucket {bucket} not found"}, 404
                return {"measurements": client.get_all_measurements(bucket=bucket)}, 200
            else:
                if bucket not in client.get_all_buckets():
                    return {"message": f"Bucket {bucket} not found"}, 404
                return {"measurements": client.get_all_measurements(bucket=bucket)}, 200
        except CustomException as e:
            return {"message": str(e.message)}, e.status_code
        except Exception as e:
            return abort(code=500, message=str(e))
