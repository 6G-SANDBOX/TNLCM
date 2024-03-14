import os

from json import load, loads
from base64 import b64decode
from time import sleep
from src.temp.temp_file_handler import TempFileHandler
from src.trial_network.trial_network_descriptor import get_component_public
from src.trial_network.trial_network_queries import get_descriptor_trial_network, update_status_trial_network
from src.callback.jenkins_handler import JenkinsHandler

report_directory = os.path.join(os.getcwd(), "app", "callback", "reports")
decoded_component_information_file_path = os.path.join(report_directory, "decoded_information.json")
report_components_jenkins_file_path = os.path.join(report_directory, "report_components_jenkins.md")

def create_report_directory():
    if not os.path.exists(report_directory):
        os.makedirs(report_directory)

def save_decoded_information(data):
    create_report_directory()
    if os.path.isfile(decoded_component_information_file_path):
        os.remove(decoded_component_information_file_path)
    decoded_data = b64decode(data).decode("utf-8") # TEST
    decoded_dict = loads(decoded_data)
    result_msg = decoded_dict.get("result_msg")
    with open(decoded_component_information_file_path, "w") as decoded_information_file:
        decoded_information_file.write(decoded_data)
    with open(report_components_jenkins_file_path, "a") as result_msg_file:
        result_msg_file.write(result_msg)

def rename_decoded_information_file(name_file):
    new_name_path = os.path.join(report_directory, name_file)
    if os.path.isfile(decoded_component_information_file_path):
        os.rename(decoded_component_information_file_path, new_name_path)
        return new_name_path

def extract_tn_vxlan_id(jenkins_tn_id):
    component_report_file = os.path.join(report_directory, "tn_vxlan_" + jenkins_tn_id + ".json")
    if os.path.isfile(component_report_file):
        with open(component_report_file, 'r') as file:
            json_data = load(file)
            tn_vxlan_id = json_data.get("tn_vxlan_id")
            return tn_vxlan_id

def deploy_trial_network(tn_id):
    descriptor_trial_network = get_descriptor_trial_network(tn_id)["trial_network"]
    update_status_trial_network(tn_id, "deploying")
    temp_file_handler = TempFileHandler()
    jenkins_handler = JenkinsHandler()
    jenkins_tn_id = jenkins_handler.get_jenkins_tn_id()
    jenkins_deployment_site = jenkins_handler.get_jenkins_deployment_site()
    for component_name, component_data in descriptor_trial_network.items():
        jenkins_client = jenkins_handler.get_jenkins_client()
        jenkins_job_name = jenkins_handler.get_jenkins_job_name()
        if component_name == "tn_vxlan":
            component_path_temp_file = temp_file_handler.create_component_temp_file(component_name, get_component_public(component_data))
        else:
            component_path_temp_file = temp_file_handler.create_component_temp_file(component_name, get_component_public(component_data), extract_tn_vxlan_id(jenkins_tn_id))
        sleep(1)
        if os.path.isfile(component_path_temp_file):
            with open(component_path_temp_file, 'rb') as component_temp_file:
                parameters = {
                    "TN_ID": jenkins_tn_id,
                    "LIBRARY_COMPONENT_NAME": component_name,
                    "LIBRARY_BRANCH": "update_bastion", # Update
                    "DEPLOYMENT_SITE": jenkins_deployment_site,
                }
                job_url = jenkins_client.build_job_url(name=jenkins_job_name, parameters=parameters)
                file = {"FILE": (component_path_temp_file, component_temp_file)}
                response = jenkins_handler.jenkins_deploy_component(job_url=job_url, file=file)
                if response.status_code == 201:
                    # job_info = server.get_job_info(name=job_name)
                    last_build_number = jenkins_client.get_job_info(name=jenkins_job_name)["nextBuildNumber"]
                    while last_build_number != jenkins_client.get_job_info(name=jenkins_job_name)["lastCompletedBuild"]["number"]:
                        sleep(15)
                    
                    if jenkins_client.get_job_info(name=jenkins_job_name)["lastSuccessfulBuild"]["number"] == last_build_number:
                        sleep(5)
                        rename_decoded_information_file(component_name + "_" + jenkins_tn_id + ".json")
