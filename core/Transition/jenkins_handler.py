import os

from jenkins import Jenkins
from requests import post

class JenkinsHandler:

    def __init__(self):
        self.jenkins_server = os.getenv("JENKINS_SERVER")
        self.jenkins_user = os.getenv("JENKINS_USER")
        self.jenkins_password = os.getenv("JENKINS_PASSWORD")
        self.jenkins_token = os.getenv("JENKINS_TOKEN")
        self.jenkins_client = Jenkins(self.jenkins_server, username=self.jenkins_user, password=self.jenkins_password)

    def get_jenkins_client(self):
        return self.jenkins_client

    def deploy_components(self, job_url, files):
        return post(job_url, auth=(self.jenkins_user, self.jenkins_token), files=files)

    def update_marketplace(self):
        # TODO: pipeline to update the TNLCM version in marketplace
        pass