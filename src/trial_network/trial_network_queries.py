from uuid import uuid4
from json import dumps, loads

from src.database.mysql_handler import MysqlHandler
from src.trial_network.trial_network_descriptor import sort_descriptor

STATUS_TRIAL_NETWORK = ["pending", "deploying", "finished"]

def create_mysql_client():
    mysql_client = MysqlHandler()
    return mysql_client

def get_trial_networks():
    mysql_client = create_mysql_client()
    query = "SELECT tn_id FROM trial_network"
    trial_networks = mysql_client.execute_query(query)
    mysql_client.close()
    return trial_networks

def create_trial_network(descriptor):
    mysql_client = create_mysql_client()
    tn_id = str(uuid4())
    status = STATUS_TRIAL_NETWORK[0]
    raw_descriptor_json = dumps(descriptor)
    sorted_descriptor_json = dumps(sort_descriptor(descriptor))
    query = "INSERT INTO trial_network (tn_id, status, raw_descriptor, sorted_descriptor) VALUES (%s, %s, %s, %s)"
    params = (tn_id, status, raw_descriptor_json, sorted_descriptor_json)
    mysql_client.execute_query(query, params)
    mysql_client.commit()
    mysql_client.close()
    return tn_id

def get_descriptor_trial_network(tn_id):
    mysql_client = create_mysql_client()
    query = "SELECT sorted_descriptor FROM trial_network WHERE tn_id = %s"
    params = (tn_id,)
    sorted_descriptor = mysql_client.execute_query(query, params)
    mysql_client.close()
    if not sorted_descriptor:
        raise ValueError("Trial Network not found")
    else:
        return loads(sorted_descriptor[0][0])

def update_status_trial_network(tn_id, new_status):
    mysql_client = create_mysql_client()
    query = "UPDATE trial_network SET status = %s WHERE tn_id = %s"
    params = (new_status, tn_id)
    mysql_client.execute_query(query, params)
    mysql_client.commit()
    mysql_client.close()