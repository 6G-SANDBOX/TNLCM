from json import loads
from datetime import datetime, timezone
from string import ascii_lowercase, digits
from random import choice

from src.logs.log_handler import log_handler
from src.exceptions.exceptions_handler import TrialNetworkInvalidStatusError

STATUS_TRIAL_NETWORK = ["pending", "deploying", "finished", "failed", "started"]

class TrialNetworkHandler:

    def __init__(self, mongo_handler=None, current_user=None, tn_id=None):
        """Constructor"""
        self.mongo_handler = mongo_handler
        self.current_user = current_user
        self.tn_id = tn_id

    def get_trial_networks(self):
        """Return all the trial networks created by a user. If user is an administrator, it returns all the trial networks created by the users"""
        log_handler.info(f"Get all trial networks created by user '{self.current_user}' from database")
        query = None if self.current_user == "admin" else {"user_created": self.current_user}
        projection = {"_id": 0}
        trial_networks = self.mongo_handler.find_data(collection_name="trial_networks", query=query, projection=projection)
        for tn in trial_networks:
            tn["tn_raw_descriptor"] = loads(tn["tn_raw_descriptor"])
            tn["tn_sorted_descriptor"] = loads(tn["tn_sorted_descriptor"])
        return trial_networks

    def get_trial_network(self):
        """Return a trial network with a specific tn_id of a user"""
        log_handler.info(f"Get trial network '{self.tn_id}' created by user '{self.current_user}' from database")
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0}
        trial_network = self.mongo_handler.find_data(collection_name="trial_networks", query=query, projection=projection)
        return trial_network

    def get_trial_network_status(self):
        """Return the status of a trial network"""
        log_handler.info(f"Get status of trial network '{self.tn_id}' created by user '{self.current_user}'")
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0, "tn_status": 1}
        trial_network_status = self.mongo_handler.find_data(collection_name="trial_networks", query=query, projection=projection)
        return trial_network_status[0]
    
    def get_trial_network_descriptor(self):
        """Return the descriptor associated to a trial network"""
        log_handler.info(f"Get descriptor of trial network '{self.tn_id}' created by user '{self.current_user}' from database")
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0, "tn_sorted_descriptor": 1}
        trial_network_descriptor = self.mongo_handler.find_data(collection_name="trial_networks", query=query, projection=projection)
        return loads(trial_network_descriptor[0]["tn_sorted_descriptor"])

    def get_trial_network_report(self):
        """Return the report associated with a trial network"""
        log_handler.info(f"Get report of trial network '{self.tn_id}' created by user '{self.current_user}' from database")
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"_id": 0, "tn_report": 1}
        tn_report = self.mongo_handler.find_data(collection_name="trial_networks", query=query, projection=projection)
        return tn_report[0]

    def get_trial_networks_templates(self):
        """Return all the trial networks templates"""
        log_handler.info(f"Get template of trial network '{self.tn_id}' from database")
        query = None
        projection = {"_id": 0, "tn_id": 1, "tn_sorted_descriptor": 1}
        trial_networks_templates = self.mongo_handler.find_data(collection_name="trial_networks_templates", query=query, projection=projection)
        if trial_networks_templates:
            for template in trial_networks_templates:
                template["tn_sorted_descriptor"] = loads(template["tn_sorted_descriptor"])
        return trial_networks_templates

    def add_trial_network(self, tn_raw_descriptor, tn_sorted_descriptor):
        """Add trial network to database"""
        log_handler.info(f"Add trial network '{self.tn_id}' to database created by user '{self.current_user}'")
        tn_status = STATUS_TRIAL_NETWORK[0]
        tn_id = self._generate_trial_network_id(size=3)
        while self._find_trial_network_id(tn_id):
            tn_id = self._generate_trial_network_id(size=3)
        self.tn_id = tn_id
        trial_network_doc = {
            "user_created": self.current_user,
            "tn_id": self.tn_id,
            "tn_date_created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "tn_status": tn_status,
            "tn_raw_descriptor": tn_raw_descriptor,
            "tn_sorted_descriptor": tn_sorted_descriptor
        }
        self.mongo_handler.insert_data("trial_networks", trial_network_doc)

    def add_trial_network_template(self, tn_raw_descriptor, tn_sorted_descriptor):
        """Add trial network template to database"""
        log_handler.info(f"Add trial network template '{self.tn_id}' created by user '{self.current_user}' to database")
        trial_network_doc = {
            "user_created": self.current_user,
            "tn_id": self.tn_id,
            "tn_date_created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "tn_raw_descriptor": tn_raw_descriptor,
            "tn_sorted_descriptor": tn_sorted_descriptor
        }
        self.mongo_handler.insert_data("trial_networks_templates", trial_network_doc)

    def add_report_trial_network(self, report_components_jenkins_content):
        """Add the report of the trial network"""
        log_handler.info(f"Add report of trial network '{self.tn_id}' created by user '{self.current_user}' to database")
        with open(report_components_jenkins_content, "r") as file:
            markdown_content = file.read()
        query = {"user_created": self.current_user, "tn_id": self.tn_id}
        projection = {"$set": {"tn_report": markdown_content}}
        self.mongo_handler.update_data(collection_name="trial_networks", query=query, projection=projection)

    def update_trial_network_status(self, new_status):
        """Update the status of a trial network"""
        if new_status in STATUS_TRIAL_NETWORK:
            log_handler.info(f"Update status of trial network '{self.tn_id}' created by user '{self.current_user}' to '{new_status}'")
            query = {"user_created": self.current_user, "tn_id": self.tn_id}
            projection = {"$set": {"tn_status": new_status}}
            self.mongo_handler.update_data(collection_name="trial_networks", query=query, projection=projection)
        else:
            raise TrialNetworkInvalidStatusError(f"The status cannot be updated. The possible states of a trial network are: {STATUS_TRIAL_NETWORK}", 404)

    def delete_trial_network(self):
        """Remove a specific trial network"""
        log_handler.info(f"Delete trial network '{self.tn_id}' created by user '{self.current_user}' from database")
        query = {"tn_id": self.tn_id} if self.current_user == "admin" else {"user_created": self.current_user, "tn_id": self.tn_id}
        self.mongo_handler.delete_data(collection_name="trial_networks", query=query)

    def _find_trial_network_id(self, tn_id):
        """Find if the tn_id has been used before because if so the pipeline will fail. OpenNebula detects that this component is already deployed and returns an error"""
        query = {"tn_id": tn_id}
        projection = {"_id": 0, "tn_id": 1}
        id = self.mongo_handler.find_data(collection_name="trial_networks", query=query, projection=projection)
        if id:
            return True
        return False

    def _generate_trial_network_id(self, size=6, chars=ascii_lowercase + digits):
        """Generate random tn_id using [a-z][0-9]"""
        return choice(ascii_lowercase) + ''.join(choice(chars) for _ in range(size))