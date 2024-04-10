from json import loads
from string import ascii_lowercase, digits
from random import choice

from src.database.mongo_handler import MongoHandler
from src.exceptions.exceptions_handler import TrialNetworkInvalidStatusError

STATUS_TRIAL_NETWORK = ["pending", "deploying", "finished", "failed", "started"]

class TrialNetworkHandler:

    def __init__(self, current_user, tn_id=None):
        """Constructor"""
        self.current_user = current_user
        self.tn_id = tn_id
        self.mongo_client = MongoHandler()

    def get_trial_networks(self):
        """Return all the trial networks created by a user. If user is an administrator, it returns all the trial networks created by the users"""
        query = None if self.current_user == "admin" else {"user_created": self.current_user}
        projection = {"_id": 0, "tn_id": 1}
        trial_networks = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
        return [tn["tn_id"] for tn in trial_networks]

    def get_trial_network(self):
        """Return a trial network with a specific tn_id of a user"""
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0}
        trial_network = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
        return trial_network

    def find_trial_network_id(self, tn_id):
        """Find if the tn_id has been used before because if so the pipeline will fail. OpenNebula detects that this component is already deployed and returns an error"""
        query = {"tn_id": tn_id}
        projection = {"_id": 0, "tn_id": 1}
        id = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
        if id:
            return True
        return False

    def generate_trial_network_id(self, size=6, chars=ascii_lowercase + digits):
        """Generate random tn_id using [a-z][0-9]"""
        return choice(ascii_lowercase) + ''.join(choice(chars) for _ in range(size))

    def create_trial_network(self, tn_raw_descriptor, tn_sorted_descriptor):
        """Add trial network to database"""
        tn_status = STATUS_TRIAL_NETWORK[0]
        tn_id = self.generate_trial_network_id(size=3)
        while self.find_trial_network_id(tn_id):
            tn_id = self.generate_trial_network_id(size=3)
        self.tn_id = tn_id
        trial_network_doc = {
            "user_created": self.current_user,
            "tn_id": self.tn_id,
            "tn_status": tn_status,
            "tn_raw_descriptor": tn_raw_descriptor,
            "tn_sorted_descriptor": tn_sorted_descriptor
        }
        self.mongo_client.insert_data("trial_network", trial_network_doc)

    def get_trial_network_descriptor(self):
        """Return the descriptor associated to a trial network"""
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0, "tn_sorted_descriptor": 1}
        trial_network_descriptor = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
        return loads(trial_network_descriptor[0]["tn_sorted_descriptor"])

    def delete_trial_network(self):
        """Remove a specific trial network"""
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        self.mongo_client.delete_data(collection_name="trial_network", query=query)

    def get_trial_network_status(self):
        """Return the status of a trial network"""
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0, "tn_status": 1}
        trial_network_status = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
        return trial_network_status[0]["tn_status"]
    
    def get_trial_networks_status(self):
        """Return the status of the trial networks"""
        query = None if self.current_user == "admin" else {"user_created": self.current_user}
        projection = {"_id": 0, "tn_id": 1, "tn_status": 1}
        trial_network_status = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)
        return trial_network_status

    def update_trial_network_status(self, new_status):
        """Update the status of a trial network"""
        if new_status in STATUS_TRIAL_NETWORK:
            query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user}
            projection = {"$set": {"tn_status": new_status}}
            self.mongo_client.update_data(collection_name="trial_network", query=query, projection=projection)
        else:
            raise TrialNetworkInvalidStatusError(f"The status cannot be updated. The possible states of a trial network are: {STATUS_TRIAL_NETWORK}", 404)
    
    def get_trial_network_report(self):
        """Return the report associated with a trial network"""
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0, "tn_report": 1}
        tn_report = self.mongo_client.find_data(collection_name="trial_network", query=query, projection=projection)[0]
        return tn_report

    def save_report_trial_network(self, report_components_jenkins_content):
        """Save the report of the trial network"""
        with open(report_components_jenkins_content, "r") as file:
            markdown_content = file.read()
        query = {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"$set": {"tn_report": markdown_content}}
        self.mongo_client.update_data(collection_name="trial_network", query=query, projection=projection)
    
    def get_trial_networks_templates(self):
        """Return all the trial networks templates"""
        query = None
        projection = {"_id": 0, "tn_id": 1, "tn_sorted_descriptor": 1}
        trial_networks_templates = self.mongo_client.find_data(collection_name="trial_networks_templates", query=query, projection=projection)
        if trial_networks_templates:
            for template in trial_networks_templates:
                template["tn_sorted_descriptor"] = loads(template["tn_sorted_descriptor"])
        return trial_networks_templates

    def create_trial_network_template(self, tn_raw_descriptor, tn_sorted_descriptor):
        """Add trial network template to database"""
        trial_network_doc = {
            "user_created": self.current_user,
            "tn_id": self.tn_id,
            "tn_raw_descriptor": tn_raw_descriptor,
            "tn_sorted_descriptor": tn_sorted_descriptor
        }
        self.mongo_client.insert_data("trial_networks_templates", trial_network_doc)