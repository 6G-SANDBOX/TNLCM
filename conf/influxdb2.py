from core.exceptions.exceptions import UndefinedEnvVarError
from core.logs.log_handler import console_logger
from core.utils.os import get_dotenv_var


class InfluxDB2Settings:
    """
    InfluxDB Settings
    """

    INFLUXDB_HOST = get_dotenv_var(key="INFLUXDB_HOST")
    INFLUXDB_PORT = get_dotenv_var(key="INFLUXDB_PORT")
    INFLUXDB_URL = get_dotenv_var(key="INFLUXDB_URL")
    INFLUXDB_ORGANIZATION = get_dotenv_var(key="INFLUXDB_ORGANIZATION")
    INFLUXDB_TOKEN = get_dotenv_var(key="INFLUXDB_TOKEN")
    INFLUXDB_BUCKET = get_dotenv_var(key="INFLUXDB_BUCKET")

    missing_variables = []
    if not INFLUXDB_HOST:
        missing_variables.append("INFLUXDB_HOST")
    if not INFLUXDB_ORGANIZATION:
        missing_variables.append("INFLUXDB_ORGANIZATION")
    if not INFLUXDB_TOKEN:
        missing_variables.append("INFLUXDB_TOKEN")
    if not INFLUXDB_BUCKET:
        missing_variables.append("INFLUXDB_BUCKET")
    if missing_variables:
        raise UndefinedEnvVarError(missing_variables=missing_variables)

    config_dict = {
        "INFLUXDB_HOST": INFLUXDB_HOST,
        "INFLUXDB_PORT": INFLUXDB_PORT,
        "INFLUXDB_URL": INFLUXDB_URL,
        "INFLUXDB_ORGANIZATION": INFLUXDB_ORGANIZATION,
        "INFLUXDB_TOKEN": INFLUXDB_TOKEN,
        "INFLUXDB_BUCKET": INFLUXDB_BUCKET,
    }
    console_logger.info(message=f"Load InfluxDB configuration: {config_dict}")
