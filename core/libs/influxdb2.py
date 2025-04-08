from typing import List

from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import Point


class InfluxDBWrapper:
    """
    InfluxDB client
    """

    def __init__(self, url: str, token: str, org: str):
        self.url = url
        self.token = token
        self.org = org
        self.client = InfluxDBClient(url=url, token=token, org=org)

    def close_client(self):
        """
        Close the InfluxDB client
        """
        self.client.close()

    def create_bucket(self, bucket: str) -> str:
        """
        Create a bucket in the InfluxDB client

        :param bucket: name of the bucket to create, ``str``
        :return: name of the created bucket, ``str``
        """
        buckets_api = self.client.buckets_api()
        bucket = buckets_api.create_bucket(bucket_name=bucket)
        return bucket

    def get_all_buckets(self) -> List[str]:
        """
        Get all buckets from the InfluxDB client

        :return: list of bucket names, ``List[str]``
        """
        return [
            bucket.name for bucket in self.client.buckets_api().find_buckets().buckets
        ]

    def get_all_measurements(self, bucket: str) -> List[str]:
        """
        Get all measurements from the InfluxDB client

        :param bucket: name of the bucket to get measurements from, ``str``
        :return: list of measurement names, ``List[str]``
        """
        query = f'import "influxdata/influxdb/schema" schema.measurements(bucket: "{bucket}")'
        tables = self.query_data(query=query)
        return [record.get_value() for table in tables for record in table.records]

    def transfer_measurement(
        self,
        tables: List,
        destination_bucket: str,
    ) -> None:
        """
        Transfer data to the InfluxDB client

        :param tables: list of tables to transfer, ``List[Table]``
        :param destination_bucket: name of the destination bucket, ``str``
        :param measurement: name of the measurement to transfer, ``str``
        """
        for table in tables:
            for record in table.records:
                dict_structure = {}
                dict_structure["measurement"] = record.get_measurement()
                dict_structure["field"] = record.get_field()
                dict_structure["value"] = record.get_value()
                dict_structure["time"] = record.get_time()
                point = (
                    Point(dict_structure["measurement"])
                    .field(dict_structure["field"], dict_structure["value"])
                    .time(dict_structure["time"])
                )
                self.write_data(
                    bucket=destination_bucket,
                    org=self.org,
                    point=point,
                )

    def query_data(self, query: str) -> List[str]:
        """
        Create a query in the InfluxDB client

        :param query: query to execute
        :return: query results
        """
        return self.client.query_api().query(query=query)

    def write_data(self, bucket: str, org: str, point: Point) -> None:
        """
        Write data to the InfluxDB client

        :param bucket: name of the bucket to write to, ``str``
        :param org: name of the organization, ``str``
        :param point: point to write, ``Point``
        """
        self.client.write_api().write(
            bucket=bucket,
            org=org,
            record=point,
        )
