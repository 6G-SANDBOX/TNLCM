import os

from jenkins import Jenkins
from requests import post

class JenkinsHandler:

    def __init__(self):
        self.jenkins_server = os.getenv("JENKINS_SERVER")
        self.jenkins_user = os.getenv("JENKINS_USER")
        self.jenkins_password = os.getenv("JENKINS_PASSWORD")
        self.jenkins_token = os.getenv("JENKINS_TOKEN")
        self.jenkins_job_name = os.getenv("JENKINS_JOB_NAME")
        self.jenkins_client = Jenkins(self.jenkins_server, username=self.jenkins_user, password=self.jenkins_password)

    def get_jenkins_client(self):
        return self.jenkins_client

    def get_job_name(self):
        return self.jenkins_job_name

    def deploy_component(self, job_url, file):
        return post(job_url, auth=(self.jenkins_user, self.jenkins_token), files=file)

    def update_marketplace(self):
        # TODO: pipeline to update the TNLCM version in marketplace
        pass