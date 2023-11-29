from shared import Child, Level
from shared.data import TrialNetwork, Entity
from .base_handler import BaseHandler
from core.Tasks import SSH
from shared import Library


class ToStarted(BaseHandler):
    def __init__(self, trialNetwork: TrialNetwork):
        super().__init__("ToStarted", trialNetwork)

    def Run(self):
        from time import sleep

        order = list(self.tn.Descriptor.DeploymentOrder)

        for name in order:
            entity = self.tn.Entities[name]
            if entity.Playbook is not None:
                print(f"Instantiating '{entity.Name}' - Playbook: '{entity.Playbook.SnapshotMetadata.Commit}'")
                print(f"  Values: {entity.Values}")
                for step in entity.Playbook.Flow['Install']:
                    print(f"    {step}")
            else:
                print(f"Unable to instantiate '{entity.Name}': Unknown type '{entity.Description.Type}'")
            sleep(1)

            # TODO: Actual instantiation goes here!

            # TODO: 1. Create a YAML file (or any other way to pass the values) from the component's variables
            #   (public+private). May need values from other components in the TN. Examples of the files:
            # ----------------------------------------------- VXLAN
            # # GLOBAL VARIABLES SECTION (ADDED BY TNLCM)
            # tn_id: "ABCDEF"  # AlphaNumeric 6 charaters   <- For now we can use part of self.tn.Id, can update later
            # component_name: "tn_vxlan"
            #
            # # tn_terraform_state_url: "http://tnlcm.uma/TN/ASZDV/tfstate" # FROM MINIO
            #
            # # URL To publish result
            # tnlcm_callback: "http://tnlcm.uma/TN/ASZDV/callback"
            #
            # # FROM PUBLIC VARIABLES SECTION
            # one_vxlan_name: "TEST_ABCDEF"
            #
            # # FROM PRIVATE VARIABLES SECTION (ONLY FOR ADVANCED USERS)
            #
            # ----------------------------------------------- Bastion
            # # GLOBAL VARIABLES SECTION (ADDED BY TNLCM)
            # tn_id: "ABCDEF"  # AlphaNumeric 6 charaters
            # component_name: "tn_bastion"
            #
            # # tn_terraform_state_url: "http://tnlcm.uma/TN/ASZDV/tfstate" # FROM MINIO
            #
            # # URL To publish result
            # tnlcm_callback: "http://tnlcm.uma/TN/ASZDV/callback"
            #
            # # FROM PUBLIC VARIABLES SECTION
            # one_bastion_name: "tn_bastion"
            #
            # # FROM PRIVATE VARIABLES SECTION (ONLY FOR ADVANCED USERS)
            # one_component_networks:
            # - 0  # First one is the default network
            # - 31  #                               <- This particular value comes from the instantiation of the VXLAN
            # one_bastion_wireguard_allowed_networks: "192.168.199.0/24"

            # NOTICE: We *will* need real variable expansion in the Trial Network Descriptors (i.e. something like
            #   one_component_networks = [0, {{ VXLAN.Id }}]
            # ) We will need some sort of accessor (<Entity>.<Variable>) possibly with nesting.
            # However, we can probably skip this for now and just hack some ad-hoc management for the variables we
            # need now. In the future, there is an example of variable expansion in /core/Tasks/base_task.py that can
            # be useful as a base.

            # TODO: 2. Call to the pipeline with the file and rest of parameters, for starting probably through REST
            #   Example:
            # curl -X POST http://10.11.28.57/job/02_Trial_Network_Component/buildWithParameters \
            #   --user <redacted>:<redacted> \
            #   --form FILE=@/home/labuser/file_vxlan.yaml \
            #   -F TN_ID=ABCDEF \
            #   -F LIBRARY_COMPONENT_NAME=tn_vxlan \
            #   -F LIBRARY_BRANCH=first_tn_demo \
            #   -F DEPLOYMENT_SITE=uma

            # TODO: 3. Wait until the pipeline ends
            # If using REST we will probably need to make an active wait and check on an endpoint (ask which one)
            # If using the CLI, then we can wait until the process ends (see /shared/cli_executor.py and
            # /shared/library for samples on how to do that and retrieve the output when using the command line).

            # TODO: 4 retrieve the values generated during the pipeline:
            # - Either parse the logs (not so easily scalable)
            # - Use the callback endpoint (if/when available) to retrieve all values as a dictionary

            entity.Status = Entity.Status.Running

        self.tn.CompleteTransition()

