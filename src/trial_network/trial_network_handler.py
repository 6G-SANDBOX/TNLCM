from json import dumps, loads

from src.database.mongo_handler import MongoHandler
from src.exceptions.exceptions_handler import TrialNetworkInvalidStatusError, TrialNetworkReportNotFoundError

STATUS_TRIAL_NETWORK = ["pending", "deploying", "finished", "failed"]

class TrialNetworkHandler:

    def __init__(self, current_user, tn_id=None):
        """Constructor"""
        self.current_user = current_user
        self.tn_id = tn_id
        self.mongo_client = MongoHandler()

    def get_trial_networks(self):
        """Return all the trial networks created by a user. If the user is an administrator, it returns all the trial networks created by the user"""
        projection = {"_id": 0, "tn_id": 1}
        query = None if self.current_user == "admin" else {"user_created": self.current_user}
        trial_networks = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
        return [tn["tn_id"] for tn in trial_networks]

    def get_trial_network(self):
        """Return a trial network with a specific tn_id of a user"""
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0}
        trial_network = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
        if trial_network:
            return True
        return False

    def create_trial_network(self, tn_raw_descriptor, tn_sorted_descriptor):
        """Add trial network to database"""
        tn_status = STATUS_TRIAL_NETWORK[0]
        trial_network_doc = {
            "user_created": self.current_user,
            "tn_id": self.tn_id,
            "tn_status": tn_status,
            "tn_raw_descriptor": tn_raw_descriptor,
            "tn_sorted_descriptor": tn_sorted_descriptor
        }
        self.mongo_client.insert_data("trial_network", trial_network_doc)

    def get_descriptor_trial_network(self):
        """Return the descriptor associated with a trial network"""
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0, "tn_sorted_descriptor": 1}
        trial_network_descriptor = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
        return loads(trial_network_descriptor[0]["tn_sorted_descriptor"])

    def delete_trial_network(self):
        """Remove a specific trial network"""
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        self.mongo_client.delete_data(collection_name="trial_network", query=query)

    def get_status_trial_network(self):
        """Return the status of a trial network"""
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0, "tn_status": 1}
        trial_network_status = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
        return trial_network_status[0]["tn_status"]

    def update_status_trial_network(self, new_status):
        """Update the status of a trial network"""
        if new_status in STATUS_TRIAL_NETWORK:
            query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
            projection = {"$set": {"tn_status": new_status}}
            self.mongo_client.update_data(collection_name="trial_network", query=query, projection=projection)
        else:
            raise TrialNetworkInvalidStatusError(f"The status cannot be updated. The possible states of a trial network are: {STATUS_TRIAL_NETWORK}", 404)

    def find_component_id(self, component_id):
        """Find if the component_id has been used before because if so the pipeline will fail. OpenNebula detects that this component is already deployed and returns an error"""
        query = {"user_created": self.current_user, "component_id": component_id}
        projection = {"_id": 0, "component_id": 1}
        component_ids = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
        if component_ids:
            ids = [cid["component_id"] for cid in component_ids]
            if component_id in ids:
                return True
        return False

    def update_component_id_trial_network(self, component_id):
        """Add the component_id used for the components of the trial network"""
        query = {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"$set": {"component_id": component_id}}
        self.mongo_client.update_data(collection_name="trial_network", query=query, projection=projection)
    
    def get_report_trial_network(self):
        """Return the report associated with a trial network"""
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0, "tn_report": 1}
        tn_report = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)[0]
        if tn_report:
            return tn_report
        else:
            raise TrialNetworkReportNotFoundError(f"Trial network '{self.tn_id}' has not been deployed yet", 404)

    def save_report_trial_network(self, report_components_jenkins_content):
        """Save the report of the components deployed in the trial network"""
        with open(report_components_jenkins_content, "r") as file:
            markdown_content = file.read()
        query = {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"$set": {"tn_report": markdown_content}}
        self.mongo_client.update_data(collection_name="trial_network", query=query, projection=projection)