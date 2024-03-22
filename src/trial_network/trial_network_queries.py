from json import dumps, loads
from yaml import YAMLError

from src.database.mongo_handler import MongoHandler
from src.trial_network.trial_network_descriptor import sort_descriptor, add_component_tn_vxlan, add_component_tn_bastion, check_descriptor_extension
from src.exceptions.exceptions_handler import TrialNetworkInvalidStatusError, TrialNetworkDescriptorEmptyError, TrialNetworkDescriptorInvalidExtensionError, TrialNetworkDescriptorInvalidContentError

STATUS_TRIAL_NETWORK = ["pending", "deploying", "finished", "failed"]

def create_mongo_client():
    mongo_client = MongoHandler()
    return mongo_client

def get_trial_networks(user_created):
    mongo_client = create_mongo_client()
    projection = {"_id": 0, "tn_id": 1}
    query = None if user_created == "admin" else {"user_created": user_created}
    trial_networks = mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
    mongo_client.disconnect()
    return [tn["tn_id"] for tn in trial_networks]

def get_trial_network(user_created, tn_id):
    mongo_client = create_mongo_client()
    query = {"tn_id": tn_id} if user_created == "admin" else {"user_created": user_created, "tn_id": tn_id}
    projection = {"_id": 0}
    trial_network = mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
    mongo_client.disconnect()
    if trial_network:
        return True
    return False

def create_trial_network(user_created, tn_id, descriptor_file):
    try:
        descriptor = check_descriptor_extension(descriptor_file)
    except YAMLError:
        raise TrialNetworkDescriptorInvalidContentError("The descriptor content is not parsed correctly", 422)
    if descriptor is None:
        raise TrialNetworkDescriptorInvalidExtensionError("Invalid descriptor format. Only 'yml' or 'yaml' files will be further processed", 422)
    mongo_client = create_mongo_client()
    tn_status = STATUS_TRIAL_NETWORK[0]
    descriptor_json = dumps(descriptor)
    tn_raw_descriptor_json = loads(descriptor_json)
    if tn_raw_descriptor_json["trial_network"] is None:
        raise TrialNetworkDescriptorEmptyError("Trial network descriptor empty", 400)
    add_component_tn_vxlan(tn_raw_descriptor_json["trial_network"])
    add_component_tn_bastion(tn_raw_descriptor_json["trial_network"])
    tn_sorted_descriptor_json = dumps(sort_descriptor(tn_raw_descriptor_json))
    trial_network_doc = {
        "user_created": user_created,
        "tn_id": tn_id,
        "tn_status": tn_status,
        "tn_raw_descriptor": dumps(tn_raw_descriptor_json),
        "tn_sorted_descriptor": tn_sorted_descriptor_json
    }
    mongo_client.insert_data("trial_network", trial_network_doc)
    mongo_client.disconnect()
    return tn_id

def get_descriptor_trial_network(user_created, tn_id):
    mongo_client = create_mongo_client()
    query = {"tn_id": tn_id} if user_created == "admin" else {"user_created": user_created, "tn_id": tn_id}
    projection = {"_id": 0, "tn_sorted_descriptor": 1}
    trial_network_descriptor = mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
    mongo_client.disconnect()
    return loads(trial_network_descriptor[0]["tn_sorted_descriptor"])

def get_status_trial_network(user_created, tn_id):
    mongo_client = create_mongo_client()
    query = {"tn_id": tn_id} if user_created == "admin" else {"user_created": user_created, "tn_id": tn_id}
    projection = {"tn_status": 1, "_id": 0}
    trial_network_status = mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
    mongo_client.disconnect()
    return trial_network_status[0]

def update_status_trial_network(user_created, tn_id, new_status):
    if new_status in STATUS_TRIAL_NETWORK:
        mongo_client = create_mongo_client()
        query = {"tn_id": tn_id} if user_created == "admin" else {"user_created": user_created, "tn_id": tn_id}
        projection = {"$set": {"tn_status": new_status}}
        mongo_client.update_data(collection_name="trial_network", query=query, projection=projection)
        mongo_client.disconnect()
    else:
        raise TrialNetworkInvalidStatusError(f"The status cannot be updated. The possible states of a trial network are: {STATUS_TRIAL_NETWORK}", 404)

def delete_trial_network(user_created, tn_id):
    mongo_client = create_mongo_client()
    query = {"tn_id": tn_id} if user_created == "admin" else {"user_created": user_created, "tn_id": tn_id}
    mongo_client.delete_data(collection_name="trial_network", query=query)
    mongo_client.disconnect()

def check_component_id(user_created, component_id):
    mongo_client = create_mongo_client()
    query = {"user_created": user_created, "component_id": component_id}
    projection = {"_id": 0, "component_id": 1}
    component_ids = mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
    mongo_client.disconnect()
    if component_ids:
        ids = [cid["component_id"] for cid in component_ids]
        if component_id in ids:
            return True
    return False

def update_component_id_trial_network(user_created, tn_id, component_id):
    mongo_client = create_mongo_client()
    query = {"user_created": user_created, "tn_id": tn_id}
    projection = {"$set": {"component_id": component_id}}
    mongo_client.update_data(collection_name="trial_network", query=query, projection=projection)
    mongo_client.disconnect() 

def save_report_trial_network(user_created, tn_id, report_components_jenkins_content):
    mongo_client = create_mongo_client()
    with open(report_components_jenkins_content, "r") as file:
        markdown_content = file.read()
    query = {"user_created": user_created, "tn_id": tn_id}
    projection = {"$set": {"tn_report_jenkins": markdown_content}}
    mongo_client.update_data(collection_name="trial_network", query=query, projection=projection)
    mongo_client.disconnect()