from uuid import uuid4
from json import dumps, loads

from src.database.mongo_handler import MongoHandler
from src.trial_network.trial_network_descriptor import sort_descriptor

STATUS_TRIAL_NETWORK = ["pending", "deploying", "finished", "failed"]

def create_mongo_client():
    mongo_client = MongoHandler()
    return mongo_client

def get_trial_networks():
    mongo_client = create_mongo_client()
    projection = {"_id": 0, "tn_id": 1}
    trial_networks = mongo_client.find_data(collection_name="trial_network", projection=projection)
    mongo_client.disconnect()
    if trial_networks:
        return [tn["tn_id"] for tn in trial_networks]
    else:
        raise ValueError(f"No trial networks stored in 'trial_network' collection in the database '{mongo_client.database}'")

def create_trial_network(descriptor):
    mongo_client = create_mongo_client()
    tn_id = str(uuid4())
    tn_status = STATUS_TRIAL_NETWORK[0]
    tn_raw_descriptor_json = dumps(descriptor)
    tn_sorted_descriptor_json = dumps(sort_descriptor(descriptor))
    trial_network_doc = {
        "tn_id": tn_id,
        "tn_status": tn_status,
        "tn_raw_descriptor": tn_raw_descriptor_json,
        "tn_sorted_descriptor": tn_sorted_descriptor_json
    }
    mongo_client.insert_data("trial_network", trial_network_doc)
    mongo_client.disconnect()
    return tn_id

def get_descriptor_trial_network(tn_id):
    mongo_client = create_mongo_client()
    query = {"tn_id": tn_id}
    projection = {"_id": 0, "tn_sorted_descriptor": 1}
    trial_network_descriptor = mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
    mongo_client.disconnect()
    if trial_network_descriptor:
        return loads(trial_network_descriptor[0]["tn_sorted_descriptor"])
    else:
        raise ValueError(f"No trial networks stored in 'trial_network' collection in the database '{mongo_client.database}' with tn_id '{tn_id}'")

def get_status_trial_network(tn_id):
    mongo_client = create_mongo_client()
    query = {"tn_id": tn_id}
    projection = {"tn_status": 1, "_id": 0}
    trial_network_status = mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
    mongo_client.disconnect()
    if trial_network_status:
        return trial_network_status[0]
    else:
        raise ValueError(f"No trial networks stored in trial_network collection in the database '{mongo_client.database}' with tn_id '{tn_id}'")

def update_status_trial_network(tn_id, new_status):
    if new_status in STATUS_TRIAL_NETWORK:
        mongo_client = create_mongo_client()
        query = {"tn_id": tn_id}
        projection = {"$set": {"tn_status": new_status}}
        mongo_client.update_data(collection_name="trial_network", query=query, projection=projection)
        mongo_client.disconnect()
    else:
        raise ValueError(f"The status cannot be updated. The possible states are: {STATUS_TRIAL_NETWORK}")